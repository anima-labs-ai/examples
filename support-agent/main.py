"""
Customer Support Agent — Demonstrates Anima's email + vault + AI triage.

This agent monitors an inbox for customer support emails, classifies them
by urgency/category using AI, retrieves relevant knowledge base credentials
from the vault, and sends tailored responses.

Flow:
  1. Create an agent with a support inbox
  2. Store knowledge base / CRM credentials in vault
  3. Monitor inbox for support requests
  4. Classify and triage incoming messages with AI
  5. Generate context-aware responses
  6. Send replies and escalate critical issues
"""

import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from anima import Anima

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AGENT_NAME = "Support Assistant"
POLL_INTERVAL_SECONDS = 10
ESCALATION_EMAIL = "manager@example.com"

TRIAGE_PROMPT = """You are a customer support triage system. Given a support email,
classify it and draft a response. Return JSON:
{
  "category": "billing|technical|account|general",
  "urgency": "low|medium|high|critical",
  "sentiment": "positive|neutral|negative|angry",
  "needs_escalation": true/false,
  "response": "Your drafted response to the customer",
  "internal_notes": "Notes for the support team"
}"""

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

anima = Anima(api_key=os.environ["ANIMA_API_KEY"])
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def triage_message(subject: str, body: str, sender: str) -> dict:
    """Use GPT-4 to classify a support message and draft a response."""
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": TRIAGE_PROMPT},
            {
                "role": "user",
                "content": (
                    f"From: {sender}\n"
                    f"Subject: {subject}\n\n"
                    f"{body}"
                ),
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    return json.loads(response.choices[0].message.content)


def setup_agent() -> dict:
    """Create agent, inbox, and store knowledge base credentials."""
    print("\n[1/3] Creating support agent...")
    agent = anima.agents.create(name=AGENT_NAME)
    print(f"  Agent: {agent.id} ({agent.name})")

    print("\n[2/3] Provisioning vault for CRM credentials...")
    anima.vault.provision(agent_id=agent.id)
    credential = anima.vault.create_credential(
        agent_id=agent.id,
        name="CRM System",
        type="login",
        username="support-bot@example.com",
        password="crm-api-key-demo",
        uris=["https://crm.example.com/api"],
    )
    print(f"  Stored: {credential.name}")

    print("\n[3/3] Agent ready to receive support emails.")
    return {
        "agent_id": agent.id,
        "credential_id": credential.id,
    }


def handle_message(agent_id: str, msg) -> None:
    """Triage a single support message and respond."""
    print(f"\n{'─' * 50}")
    print(f"  From: {msg.from_email}")
    print(f"  Subject: {msg.subject}")

    # AI triage
    result = triage_message(
        subject=msg.subject,
        body=msg.body,
        sender=msg.from_email,
    )

    urgency = result.get("urgency", "medium")
    category = result.get("category", "general")
    sentiment = result.get("sentiment", "neutral")
    needs_escalation = result.get("needs_escalation", False)

    print(f"  Category: {category} | Urgency: {urgency} | Sentiment: {sentiment}")

    # Send AI-drafted response
    anima.messages.send_email(
        agent_id=agent_id,
        to=msg.from_email,
        subject=f"Re: {msg.subject}",
        body=result.get("response", "We received your message and will respond shortly."),
    )
    print(f"  Reply sent to {msg.from_email}")

    # Escalate critical issues
    if needs_escalation or urgency == "critical":
        anima.messages.send_email(
            agent_id=agent_id,
            to=ESCALATION_EMAIL,
            subject=f"[ESCALATION] {msg.subject}",
            body=(
                f"Escalated support ticket:\n\n"
                f"From: {msg.from_email}\n"
                f"Category: {category}\n"
                f"Urgency: {urgency}\n"
                f"Sentiment: {sentiment}\n\n"
                f"Original message:\n{msg.body}\n\n"
                f"Internal notes:\n{result.get('internal_notes', 'N/A')}"
            ),
        )
        print(f"  ⚠ Escalated to {ESCALATION_EMAIL}")


def poll_inbox(agent_id: str, processed: set[str]) -> set[str]:
    """Check for new messages and handle each one."""
    messages = anima.messages.list(agent_id=agent_id)
    for msg in messages:
        if msg.id in processed:
            continue
        handle_message(agent_id, msg)
        processed.add(msg.id)
    return processed


def main():
    print("=" * 60)
    print("  Anima Customer Support Agent Demo")
    print("  Email + Vault + AI Triage")
    print("=" * 60)

    config = setup_agent()
    agent_id = config["agent_id"]

    print(f"\nSupport agent is live! Polling every {POLL_INTERVAL_SECONDS}s...\n")

    processed_ids: set[str] = set()
    try:
        while True:
            processed_ids = poll_inbox(agent_id, processed_ids)
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nShutting down support agent...")
    finally:
        # Cleanup
        print("Cleaning up...")
        anima.vault.delete_credential(
            agent_id=agent_id,
            credential_id=config["credential_id"],
        )
        anima.vault.deprovision(agent_id=agent_id)
        anima.agents.delete(agent_id=agent_id)
        print("Done.")


if __name__ == "__main__":
    main()
