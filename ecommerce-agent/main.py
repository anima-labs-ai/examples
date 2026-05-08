"""
E-Commerce Purchasing Agent — Demonstrates Anima's unified platform.

This agent showcases how a single AI agent can use Anima's capabilities
together: email, vault (credential storage), and more.

Flow:
  1. Create an agent with an email inbox
  2. Store merchant credentials in the vault
  3. Use AI to evaluate a purchase request
  4. Retrieve credentials and simulate purchase
  5. Send a confirmation email with receipt details
"""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from anima import Anima

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AGENT_NAME = "Shopping Assistant"

SYSTEM_PROMPT = """You are an AI shopping assistant. Given a purchase request,
evaluate whether it's reasonable and decide whether to proceed. Respond with
a JSON object: {"approved": true/false, "reason": "...", "estimated_cost": 0.00}"""

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

anima = Anima(api_key=os.environ["ANIMA_API_KEY"])
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def evaluate_purchase(request: str) -> dict:
    """Use GPT-4 to evaluate whether a purchase request should proceed."""
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Purchase request: {request}"},
        ],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


def main():
    print("=" * 60)
    print("  Anima E-Commerce Agent Demo")
    print("  Unified Platform: Email + Vault")
    print("=" * 60)

    # ------------------------------------------------------------------
    # Step 1: Create an agent with email capability
    # ------------------------------------------------------------------
    print("\n[1/5] Creating agent...")
    agent = anima.agents.create(name=AGENT_NAME)
    print(f"  Agent created: {agent.id}")
    print(f"  Name: {agent.name}")

    # ------------------------------------------------------------------
    # Step 2: Store merchant credentials in the vault
    # ------------------------------------------------------------------
    print("\n[2/5] Storing merchant credentials in vault...")
    anima.vault.provision(agent_id=agent.id)

    credential = anima.vault.create_credential(
        agent_id=agent.id,
        name="Demo Grocery Store",
        type="login",
        username="agent@example.com",
        password="demo-password-123",
        uris=["https://grocery-store.example.com"],
    )
    print(f"  Credential stored: {credential.name}")

    # ------------------------------------------------------------------
    # Step 3: AI evaluates the purchase request
    # ------------------------------------------------------------------
    purchase_request = "Buy organic milk ($4.99) and whole wheat bread ($3.49) from the grocery store"
    print(f"\n[3/5] Evaluating purchase: '{purchase_request}'")

    decision = evaluate_purchase(purchase_request)
    print(f"  AI Decision: {'APPROVED' if decision.get('approved') else 'DECLINED'}")
    print(f"  Reason: {decision.get('reason', 'N/A')}")
    print(f"  Estimated cost: ${decision.get('estimated_cost', 0):.2f}")

    if not decision.get("approved"):
        print("\n  Purchase declined by AI. Cleaning up...")
        anima.agents.delete(agent_id=agent.id)
        return

    # ------------------------------------------------------------------
    # Step 4: Retrieve credentials and simulate purchase
    # ------------------------------------------------------------------
    print("\n[4/5] Retrieving merchant credentials from vault...")
    creds = anima.vault.get_credential(
        agent_id=agent.id,
        credential_id=credential.id,
    )
    print(f"  Retrieved credentials for: {creds.name}")
    print(f"  Login: {creds.username}")
    print("  (In production, agent would now authenticate and complete checkout)")

    # ------------------------------------------------------------------
    # Step 5: Send confirmation email
    # ------------------------------------------------------------------
    print("\n[5/5] Sending confirmation email...")
    estimated_cost = decision.get("estimated_cost", 8.48)
    anima.messages.send_email(
        agent_id=agent.id,
        to="owner@example.com",
        subject=f"Purchase Completed - ${estimated_cost:.2f}",
        body=f"""Hello,

Your AI shopping assistant has completed a purchase:

  Items: Organic milk, whole wheat bread
  Total: ${estimated_cost:.2f}
  Merchant: Demo Grocery Store

— {AGENT_NAME} (powered by Anima)""",
    )
    print("  Confirmation email sent to owner@example.com")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  Demo Complete!")
    print("=" * 60)
    print(f"""
  This demo used the following Anima services:
    - Agent Identity: Created agent '{AGENT_NAME}'
    - Vault: Stored and retrieved merchant credentials
    - Email: Sent purchase confirmation

  In a real deployment, this agent would:
    - Monitor an inbox for purchase requests
    - Use webhooks for real-time notifications
    - Handle multi-step checkout via browser extension
    - Track transaction history for reconciliation
""")

    # Cleanup
    print("Cleaning up demo resources...")
    anima.vault.delete_credential(agent_id=agent.id, credential_id=credential.id)
    anima.vault.deprovision(agent_id=agent.id)
    anima.agents.delete(agent_id=agent.id)
    print("Done.")


if __name__ == "__main__":
    main()
