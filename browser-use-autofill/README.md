# Browser-Use + Anima Autofill

Demonstrates an AI browser agent logging into a real website **without ever
seeing the password**. The Anima Chrome extension detects the login form and
autofills credentials from the Anima vault while the
[browser-use](https://browser-use.com/) agent drives the rest of the browser.

## What this shows

- How to load the Anima extension into a Playwright-controlled Chromium
- How to share one browser between Playwright (for extension setup) and
  browser-use (for AI-driven navigation) via CDP
- How credentials stay out of the LLM's context — the prompt never mentions
  the password; only the DOM of the rendered page ever sees it

## Flow

```
1. Script creates an Anima agent + stores HN credentials in the vault
2. Script launches Chromium with the Anima extension pre-loaded
3. Script seeds the extension with an Anima API key so it can read the vault
4. browser-use Agent drives the browser: "go to HN login, submit the form"
5. When the page loads, the extension detects the login form and autofills
6. Agent clicks Login, verifies the header shows a logged-in username
7. Cleanup: delete the credential and the agent from Anima
```

## Prerequisites

- Python 3.10+
- Node.js + pnpm (to build the extension once)
- A real Hacker News account (Anima never sees it outside your vault)
- `ANIMA_API_KEY` and `OPENAI_API_KEY`

## Setup

```bash
# 1. Build the Anima extension (once)
cd ../../anima/apps/extension
pnpm install
pnpm build
cd -

# 2. Install Python deps
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 3. Configure
cp .env.example .env
# ...edit .env and fill in your values

# 4. Run
python main.py
```

## The security property, spelled out

Notice what the script does *not* do:

- It never puts the HN password into the browser-use `task` prompt
- It never logs the password
- After the initial vault write, the script's Python process drops the
  password variable

What happens instead: the Anima extension, running inside the browser, gets
an ephemeral `vtk_` token, resolves it to a credential, fills the DOM fields,
and zeroes the credential out of its own heap. The LLM only sees a form
that already has values in it.

## Caveats

- **Chromium only.** Playwright can only load unpacked extensions into
  Chromium, not Firefox or WebKit.
- **HN's anti-abuse page.** On unfamiliar IPs, HN occasionally shows a
  "Validation required" page with reCAPTCHA. The script detects this and
  exits cleanly rather than hanging.
- **This is an example, not a product.** Real deployments should use
  short-lived scoped API keys (see `anima.vault.oauth.create_link`), not
  long-lived org keys.
