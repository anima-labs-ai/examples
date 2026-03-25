"""
Email Agent — AI-powered auto-reply agent using Anima + OpenAI GPT-4.

Creates an inbox, monitors incoming messages, and sends AI-generated replies.
"""

import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from anima import Anima

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

POLL_INTERVAL_SECONDS = 10
INBOX_NAME = "Email Assistant"
INBOX_EMAIL = "assistant@example.com"

SYSTEM_PROMPT = """You are a helpful, professional email assistant. 
When you receive an email, write a concise, friendly reply that addresses 
the sender's questions or requests. Keep responses under 200 words. 
Sign off as "Email Assistant (powered by Anima)"."""

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

anima = Anima(api_key=os.environ["ANIMA_API_KEY"])
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def generate_reply(subject: str, body: str, sender: str) -> str:
    """Use GPT-4 to draft a reply to an incoming email."""
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Reply to this email.\n\n"
                    f"From: {sender}\n"
                    f"Subject: {subject}\n\n"
                    f"{body}"
                ),
            },
        ],
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content


def setup_inbox() -> dict:
    """Create an inbox to receive and send emails."""
    print("Setting up inbox...")
    inbox = anima.inboxes.create(name=INBOX_NAME, email=INBOX_EMAIL)
    print(f"  Inbox: {inbox.name} ({inbox.id})")
    print(f"  Email: {inbox.email}")

    return {"inbox_id": inbox.id, "email": inbox.email}


def poll_and_reply(inbox_id: str, processed: set[str]) -> set[str]:
    """Check for new inbound emails and reply to each one."""
    messages = anima.messages.list(inbox_id=inbox_id)

    for msg in messages:
        if msg.id in processed:
            continue

        print(f"\n--- New email from {msg.from_email} ---")
        print(f"  Subject: {msg.subject}")
        print(f"  Body: {msg.body[:200]}...")

        # Generate AI reply
        reply_body = generate_reply(
            subject=msg.subject,
            body=msg.body,
            sender=msg.from_email,
        )

        # Send reply through Anima
        reply = anima.messages.create(
            inbox_id=inbox_id,
            subject=f"Re: {msg.subject}",
            body=reply_body,
            to_email=msg.from_email,
        )
        print(f"  Replied: {reply.id}")

        processed.add(msg.id)

    return processed


def main():
    """Run the email agent loop."""
    print("=" * 60)
    print("  Anima Email Agent")
    print("=" * 60)

    # Set up inbox
    config = setup_inbox()
    print(f"\nInbox is live! Send emails to: {config['email']}")
    print(f"Polling every {POLL_INTERVAL_SECONDS}s for new messages...\n")

    processed_ids: set[str] = set()

    try:
        while True:
            processed_ids = poll_and_reply(config["inbox_id"], processed_ids)
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nShutting down email agent...")
    finally:
        anima.close()


if __name__ == "__main__":
    main()
