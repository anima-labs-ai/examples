"""
OpenAI Terminal Agent — Interactive chat agent with Anima email tools.

Uses the OpenAI Agents SDK to create a terminal-based assistant that can
send and receive emails through Anima.
"""

import asyncio
import json
import os

from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

from anima import Anima

load_dotenv()

# ---------------------------------------------------------------------------
# Anima client
# ---------------------------------------------------------------------------

anima = Anima(api_key=os.environ["ANIMA_API_KEY"])
inbox_state: dict = {}


# ---------------------------------------------------------------------------
# Tools — Anima email operations exposed to the OpenAI agent
# ---------------------------------------------------------------------------


@function_tool
def list_emails(limit: int = 10) -> str:
    """List recent emails in the inbox.

    Args:
        limit: Maximum number of emails to return (default 10).

    Returns:
        JSON string with email summaries (id, from, subject, snippet).
    """
    inbox_id = inbox_state.get("inbox_id")
    if not inbox_id:
        return json.dumps({"error": "Inbox not initialized"})

    messages = anima.messages.list(inbox_id=inbox_id, page_size=limit)

    emails = []
    for msg in messages:
        emails.append(
            {
                "id": msg.id,
                "from": msg.from_email,
                "to": msg.to_email,
                "subject": msg.subject,
                "snippet": msg.body[:150] if msg.body else "",
            }
        )

    return json.dumps(emails, indent=2)


@function_tool
def read_email(message_id: str) -> str:
    """Read the full content of a specific email.

    Args:
        message_id: The ID of the email to read.

    Returns:
        JSON string with the full email content.
    """
    inbox_id = inbox_state.get("inbox_id")
    if not inbox_id:
        return json.dumps({"error": "Inbox not initialized"})

    msg = anima.messages.get(inbox_id=inbox_id, message_id=message_id)

    return json.dumps(
        {
            "id": msg.id,
            "from": msg.from_email,
            "to": msg.to_email,
            "subject": msg.subject,
            "body": msg.body,
            "created_at": str(msg.created_at),
        },
        indent=2,
    )


@function_tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email from the inbox.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        body: Plain text email body.

    Returns:
        JSON string with the sent message details.
    """
    inbox_id = inbox_state.get("inbox_id")
    if not inbox_id:
        return json.dumps({"error": "Inbox not initialized"})

    msg = anima.messages.create(
        inbox_id=inbox_id,
        subject=subject,
        body=body,
        to_email=to,
    )

    return json.dumps(
        {
            "id": msg.id,
            "to": msg.to_email,
            "subject": msg.subject,
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Agent setup
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an email assistant with access to a real email inbox via Anima.
You can list emails, read specific emails, and send new emails.

The inbox email address is: {email}

When the user asks about emails, always use your tools to check the actual inbox.
When sending emails, confirm the recipient, subject, and body with the user before sending.
Be concise and helpful. Format email content clearly when presenting it."""


def setup_inbox() -> dict:
    """Create an Anima inbox to receive and send emails."""
    print("Setting up Anima inbox...")

    inbox = anima.inboxes.create(
        name="Terminal Agent Inbox",
        email="terminal-agent@example.com",
    )

    print(f"  Inbox created: {inbox.name}")
    print(f"  Email address: {inbox.email}")

    return {"inbox_id": inbox.id, "email": inbox.email}


async def main():
    """Run the interactive terminal agent."""
    print("=" * 60)
    print("  Anima + OpenAI Terminal Agent")
    print("=" * 60)

    # Initialize Anima inbox
    config = setup_inbox()
    inbox_state.update(config)

    # Create OpenAI agent with Anima tools
    email_agent = Agent(
        name="Email Assistant",
        instructions=SYSTEM_PROMPT.format(email=config["email"]),
        tools=[list_emails, read_email, send_email],
    )

    print(f"\nReady! Your inbox email: {config['email']}")
    print("Type your messages below. Type 'quit' or 'exit' to stop.\n")

    history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            break

        # Run the agent with conversation history
        result = await Runner.run(
            email_agent,
            input=user_input,
            context=history,
        )

        print(f"\nAssistant: {result.final_output}\n")

        # Maintain conversation context
        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": result.final_output})

    print("\nGoodbye!")
    anima.close()


if __name__ == "__main__":
    asyncio.run(main())
