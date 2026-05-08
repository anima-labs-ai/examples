"""
Browser-Use + Anima Autofill — the Anima Chrome extension autofills login
credentials while a browser-use Agent drives the browser.

Run:
    cp .env.example .env      # fill in your values
    python main.py

See README.md for the end-to-end story.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import BrowserContext, async_playwright

from anima import Anima

# browser-use: driven by an LLM. We use OpenAI here but any LangChain chat
# model works.
from browser_use import Agent, Browser
from langchain_openai import ChatOpenAI

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ANIMA_API_KEY = os.environ["ANIMA_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
HN_USERNAME = os.environ["HN_USERNAME"]
HN_PASSWORD = os.environ["HN_PASSWORD"]
EXTENSION_PATH = Path(
    os.environ.get("ANIMA_EXTENSION_PATH", "../../anima/apps/extension/dist")
).resolve()

HN_LOGIN_URL = "https://news.ycombinator.com/login"
CDP_PORT = 9222
PROFILE_DIR = Path("/tmp/anima-browser-use-demo-profile")

# The task prompt given to the LLM. Notice: it never mentions the password.
# The agent is told to *expect* autofill and not to type credentials itself.
AGENT_TASK = f"""
Go to {HN_LOGIN_URL}.

The Anima Vault extension is installed in this browser and will autofill the
login fields within a second of the page loading. DO NOT type the username or
password yourself — just wait for the fields to be pre-filled, then click the
"login" button.

After submitting, verify success by checking the header of the resulting page:
- SUCCESS: the top-right shows a link with the logged-in username (and the
  word "logout")
- FAILURE: you see an error like "Bad login." or a page titled
  "Validation required" (this means HN is asking for reCAPTCHA — just
  report this and stop, do not attempt to solve it)

Report exactly one of: LOGGED_IN, BAD_LOGIN, CAPTCHA_BLOCKED, or UNKNOWN.
"""

# ---------------------------------------------------------------------------
# Anima setup — provision agent identity and stash the credentials in vault
# ---------------------------------------------------------------------------


def provision_vault_credential(anima: Anima) -> tuple[str, str]:
    """Create an Anima agent and store the HN credential in its vault.

    Returns (agent_id, credential_id). After this function returns, the
    Python-side HN_PASSWORD variable is the last place the raw password
    lives in this process — everything downstream goes through the vault.
    """
    print("[anima] creating agent identity...")
    agent = anima.agents.create(name="Browser-Use Demo Agent")
    print(f"  agent_id = {agent.id}")

    print("[anima] provisioning vault + storing HN credential...")
    anima.vault.provision(agent_id=agent.id)
    credential = anima.vault.create_credential(
        agent_id=agent.id,
        name="Hacker News",
        type="login",
        username=HN_USERNAME,
        password=HN_PASSWORD,
        uris=["https://news.ycombinator.com"],
    )
    print(f"  credential_id = {credential.id}")
    return agent.id, credential.id


def cleanup(anima: Anima, agent_id: str, credential_id: str) -> None:
    """Delete the credential and the agent. Idempotent."""
    print("[anima] cleaning up...")
    try:
        anima.vault.delete_credential(agent_id=agent_id, credential_id=credential_id)
    except Exception as e:
        print(f"  warn: credential delete failed: {e}")
    try:
        anima.vault.deprovision(agent_id=agent_id)
    except Exception as e:
        print(f"  warn: vault deprovision failed: {e}")
    try:
        anima.agents.delete(agent_id=agent_id)
    except Exception as e:
        print(f"  warn: agent delete failed: {e}")


# ---------------------------------------------------------------------------
# Chromium + extension launch
# ---------------------------------------------------------------------------


async def launch_chromium_with_extension(pw) -> BrowserContext:
    """Launch a persistent-context Chromium with the Anima extension loaded
    and remote debugging exposed on CDP_PORT so browser-use can attach.
    """
    if not EXTENSION_PATH.exists():
        sys.exit(
            f"Extension not built at {EXTENSION_PATH}. "
            "Run `pnpm build` inside anima/apps/extension first."
        )

    print(f"[browser] launching Chromium with extension at {EXTENSION_PATH}")
    context = await pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=False,  # Chromium extensions need a real UI context
        args=[
            f"--disable-extensions-except={EXTENSION_PATH}",
            f"--load-extension={EXTENSION_PATH}",
            f"--remote-debugging-port={CDP_PORT}",
            "--no-first-run",
            "--no-default-browser-check",
        ],
    )
    return context


async def wait_for_extension_service_worker(context: BrowserContext, timeout_s: float = 10.0):
    """Block until the extension's background service worker is available."""
    # MV3 extensions register as service_workers on the context.
    deadline = asyncio.get_event_loop().time() + timeout_s
    while asyncio.get_event_loop().time() < deadline:
        if context.service_workers:
            return context.service_workers[0]
        await asyncio.sleep(0.2)
    # Fall back to an explicit wait
    return await context.wait_for_event("serviceworker", timeout=timeout_s * 1000)


# ---------------------------------------------------------------------------
# 👉 USER CONTRIBUTION ZONE 👈
# ---------------------------------------------------------------------------
#
# This is the one place where you need to make a real design decision.
#
# The Anima extension reads its API key from `chrome.storage.local.anima_api_key`
# (persistent, survives browser restarts) OR `chrome.storage.session.anima_api_key`
# (ephemeral, cleared when the browser closes). See:
#   anima/apps/extension/src/shared/messages.ts → getApiKey()
#
# We've launched a Chromium that has the extension loaded but no API key.
# The extension's service worker is available; we need to seed it.
#
# Trade-offs to consider:
#   • session storage   → auto-wiped when Chromium exits. Safer. What this
#                         demo probably wants.
#   • local storage     → persists across runs (the /tmp/...-demo-profile is
#                         reused). Faster for repeated runs, but leaves a key
#                         on disk after the script exits.
#   • Retry / readiness → service workers can be "installed but not yet
#                         activated". You may need a short retry if evaluate()
#                         throws "Target page, context or browser has been
#                         closed".
#
# Write ~5–10 lines that seed the api key into the extension's storage.
# The SDK-level API key is already in the `api_key` parameter below.
#
async def seed_extension_api_key(context: BrowserContext, api_key: str) -> None:
    """Push the Anima API key into the extension so it can read the vault.

    Implement this: find the extension's service worker and call
    chrome.storage.<session|local>.set({ anima_api_key: <api_key> }) via
    service_worker.evaluate(...).
    """
    # TODO (you): your 5-10 lines go here.
    #
    # Hints:
    #   sw = await wait_for_extension_service_worker(context)
    #   await sw.evaluate("""(key) => chrome.storage.session.set({anima_api_key: key})""", api_key)
    #
    # Then maybe verify:
    #   got = await sw.evaluate("""async () => (await chrome.storage.session.get('anima_api_key')).anima_api_key""")
    #   assert got == api_key
    raise NotImplementedError(
        "Implement seed_extension_api_key — see the comment block above."
    )


# ---------------------------------------------------------------------------
# browser-use agent
# ---------------------------------------------------------------------------


async def run_agent_task() -> str:
    """Point browser-use at the already-running Chromium via CDP and run the
    task. Returns the agent's final message (one of LOGGED_IN, BAD_LOGIN,
    CAPTCHA_BLOCKED, UNKNOWN).
    """
    print("[browser-use] attaching to Chromium via CDP...")
    browser = Browser(cdp_url=f"http://localhost:{CDP_PORT}")
    llm = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)
    agent = Agent(task=AGENT_TASK, llm=llm, browser=browser)

    history = await agent.run(max_steps=12)
    final = (history.final_result() or "UNKNOWN").strip().upper()
    # Extract just the status keyword if the LLM returned prose
    for marker in ("LOGGED_IN", "BAD_LOGIN", "CAPTCHA_BLOCKED", "UNKNOWN"):
        if marker in final:
            return marker
    return "UNKNOWN"


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


async def main() -> int:
    anima = Anima(api_key=ANIMA_API_KEY)
    agent_id, credential_id = provision_vault_credential(anima)

    async with async_playwright() as pw:
        context = await launch_chromium_with_extension(pw)
        try:
            await seed_extension_api_key(context, ANIMA_API_KEY)
            status = await run_agent_task()
            print(f"\n=== RESULT: {status} ===")
            return 0 if status == "LOGGED_IN" else 1
        finally:
            await context.close()
            cleanup(anima, agent_id, credential_id)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
