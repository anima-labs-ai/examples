"""
E-Commerce Purchasing Agent — Demonstrates Anima's unified platform.

This agent showcases how a single AI agent can use ALL of Anima's capabilities
together: email, virtual cards, vault (credential storage), and more.

Flow:
  1. Create an agent with an email inbox
  2. Store merchant credentials in the vault
  3. Create a virtual card with a spending policy
  4. Use AI to evaluate a purchase request
  5. Execute the purchase with the virtual card
  6. Send a confirmation email with receipt details
  7. Freeze the card after the transaction
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
SPENDING_LIMIT_DAILY = 10000  # $100.00 in cents
SPENDING_LIMIT_PER_AUTH = 5000  # $50.00 per transaction
ALLOWED_MERCHANT_CATEGORIES = ["5411", "5412", "5499"]  # Grocery stores

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
    print("  Unified Platform: Email + Cards + Vault")
    print("=" * 60)

    # ------------------------------------------------------------------
    # Step 1: Create an agent with email capability
    # ------------------------------------------------------------------
    print("\n[1/7] Creating agent...")
    agent = anima.agents.create(name=AGENT_NAME)
    print(f"  Agent created: {agent.id}")
    print(f"  Name: {agent.name}")

    # ------------------------------------------------------------------
    # Step 2: Store merchant credentials in the vault
    # ------------------------------------------------------------------
    print("\n[2/7] Storing merchant credentials in vault...")
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
    # Step 3: Create a virtual card with spending policies
    # ------------------------------------------------------------------
    print("\n[3/7] Creating virtual card with spending policy...")
    card = anima.cards.create(
        agent_id=agent.id,
        label="Grocery Shopping Card",
        currency="usd",
        spend_limit_daily=SPENDING_LIMIT_DAILY,
        spend_limit_per_auth=SPENDING_LIMIT_PER_AUTH,
        allowed_merchant_categories=ALLOWED_MERCHANT_CATEGORIES,
    )
    print(f"  Card created: **** {card.last4}")
    print(f"  Daily limit: ${SPENDING_LIMIT_DAILY / 100:.2f}")
    print(f"  Per-auth limit: ${SPENDING_LIMIT_PER_AUTH / 100:.2f}")

    # ------------------------------------------------------------------
    # Step 4: AI evaluates the purchase request
    # ------------------------------------------------------------------
    purchase_request = "Buy organic milk ($4.99) and whole wheat bread ($3.49) from the grocery store"
    print(f"\n[4/7] Evaluating purchase: '{purchase_request}'")

    decision = evaluate_purchase(purchase_request)
    print(f"  AI Decision: {'APPROVED' if decision.get('approved') else 'DECLINED'}")
    print(f"  Reason: {decision.get('reason', 'N/A')}")
    print(f"  Estimated cost: ${decision.get('estimated_cost', 0):.2f}")

    if not decision.get("approved"):
        print("\n  Purchase declined by AI. Cleaning up...")
        anima.cards.delete(card_id=card.id)
        anima.agents.delete(agent_id=agent.id)
        return

    # ------------------------------------------------------------------
    # Step 5: Retrieve credentials and simulate purchase
    # ------------------------------------------------------------------
    print("\n[5/7] Retrieving merchant credentials from vault...")
    creds = anima.vault.get_credential(
        agent_id=agent.id,
        credential_id=credential.id,
    )
    print(f"  Retrieved credentials for: {creds.name}")
    print(f"  Login: {creds.username}")
    print("  (In production, agent would now authenticate and complete checkout)")

    # ------------------------------------------------------------------
    # Step 6: Send confirmation email
    # ------------------------------------------------------------------
    print("\n[6/7] Sending confirmation email...")
    estimated_cost = decision.get("estimated_cost", 8.48)
    anima.messages.send_email(
        agent_id=agent.id,
        to="owner@example.com",
        subject=f"Purchase Completed - ${estimated_cost:.2f}",
        body=f"""Hello,

Your AI shopping assistant has completed a purchase:

  Items: Organic milk, whole wheat bread
  Total: ${estimated_cost:.2f}
  Card: **** {card.last4}
  Merchant: Demo Grocery Store

The virtual card has been frozen after this transaction for security.

— {AGENT_NAME} (powered by Anima)""",
    )
    print("  Confirmation email sent to owner@example.com")

    # ------------------------------------------------------------------
    # Step 7: Freeze the card after use
    # ------------------------------------------------------------------
    print("\n[7/7] Freezing card after transaction...")
    anima.cards.freeze(card_id=card.id)
    print(f"  Card **** {card.last4} frozen")

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
    - Cards: Created virtual card with spending limits
    - Email: Sent purchase confirmation
    - Security: Froze card after single-use transaction

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
    anima.cards.delete(card_id=card.id)
    anima.agents.delete(agent_id=agent.id)
    print("Done.")


if __name__ == "__main__":
    main()
