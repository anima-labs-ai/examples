"""
Multi-Channel Agent — Email + SMS + Voice using Anima + FastAPI.

Creates a unified agent that handles inquiries across all channels
and routes follow-ups between them.
"""

import os
import logging
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn

from anima import Anima

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "http://localhost:8000")
PORT = int(os.environ.get("PORT", "8000"))

VOICE_PROMPT = """You are a helpful support agent for Acme Corp.
Answer customer questions clearly and concisely.
At the end of the call, let them know you will send a summary email."""

SMS_PROMPT = """You are a helpful support agent for Acme Corp.
Reply to SMS messages concisely (under 160 characters when possible).
For complex issues, let the customer know you will call them."""

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

anima = Anima()
app = FastAPI(title="Multi-Channel Agent")

# Unified conversation log
conversations: list[dict] = []

# Resource IDs (populated at startup)
resources: dict = {}


def setup_channels() -> dict:
    """Provision email inbox, phone number, and register webhooks."""
    print("Setting up channels...")

    inbox = anima.inboxes.create(name="Support Inbox")
    print(f"  Email: {inbox.email}")

    phone = anima.phones.create(
        name="Support Phone",
        webhook_url=f"{WEBHOOK_URL}/webhook/voice",
        sms_webhook_url=f"{WEBHOOK_URL}/webhook/sms",
    )
    print(f"  Phone: {phone.number}")

    # Register email webhook
    anima.webhooks.create(
        event="message.inbound",
        url=f"{WEBHOOK_URL}/webhook/email",
    )
    print(f"  Webhooks registered")

    return {
        "inbox_id": inbox.id,
        "inbox_email": inbox.email,
        "phone_id": phone.id,
        "phone_number": phone.number,
    }


def log_event(channel: str, direction: str, contact: str, summary: str):
    """Log a conversation event."""
    entry = {
        "channel": channel,
        "direction": direction,
        "contact": contact,
        "summary": summary,
        "timestamp": datetime.now().isoformat(),
    }
    conversations.append(entry)
    logging.info(f"[{channel}] {direction}: {contact} - {summary[:80]}")


# ---------------------------------------------------------------------------
# Voice webhook
# ---------------------------------------------------------------------------


@app.post("/webhook/voice")
async def handle_voice(request: Request):
    """Handle incoming voice call events."""
    payload = await request.json()
    event_type = payload.get("type")
    call_id = payload.get("call_id")

    if event_type == "call.incoming":
        caller = payload.get("from_number", "unknown")
        log_event("voice", "inbound", caller, "Incoming call")

        anima.calls.answer(
            call_id=call_id,
            system_prompt=VOICE_PROMPT,
            voice="alloy",
        )

    elif event_type == "call.ended":
        caller = payload.get("from_number", "unknown")
        transcript = payload.get("transcript", "No transcript available.")
        duration = payload.get("duration_seconds", 0)

        log_event("voice", "completed", caller, f"Call ended ({duration}s)")

        # Send email follow-up with call summary
        anima.messages.create(
            inbox_id=resources["inbox_id"],
            to_email=caller,  # In practice, look up email from contact DB
            subject="Summary of your call with Acme Support",
            body=(
                f"Hi,\n\n"
                f"Thank you for calling Acme Support. "
                f"Here is a summary of your call:\n\n"
                f"{transcript}\n\n"
                f"If you have further questions, reply to this email.\n\n"
                f"Best,\nAcme Support Team"
            ),
        )
        log_event("email", "outbound", caller, "Sent call summary email")

    return {"status": "ok"}


# ---------------------------------------------------------------------------
# SMS webhook
# ---------------------------------------------------------------------------


@app.post("/webhook/sms")
async def handle_sms(request: Request):
    """Handle incoming SMS messages."""
    payload = await request.json()
    sender = payload.get("from_number", "unknown")
    body = payload.get("body", "")

    log_event("sms", "inbound", sender, body[:80])

    # Simple routing: short messages get SMS reply, long ones trigger a call
    if len(body) > 200:
        # Complex issue -- offer to call
        anima.sms.send(
            phone_id=resources["phone_id"],
            to_number=sender,
            body="Your question needs a detailed answer. We will call you shortly!",
        )
        log_event("sms", "outbound", sender, "Escalating to call")

        anima.calls.create(
            phone_id=resources["phone_id"],
            to_number=sender,
            system_prompt=f"{VOICE_PROMPT}\n\nContext from their SMS: {body}",
            voice="alloy",
        )
        log_event("voice", "outbound", sender, "Callback initiated")
    else:
        # Quick SMS reply
        anima.sms.send(
            phone_id=resources["phone_id"],
            to_number=sender,
            body=f"Thanks for reaching out! We received: '{body[:60]}'. "
                 f"A team member will follow up shortly.",
        )
        log_event("sms", "outbound", sender, "Auto-reply sent")

    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Email webhook
# ---------------------------------------------------------------------------


@app.post("/webhook/email")
async def handle_email(request: Request):
    """Handle incoming email messages."""
    payload = await request.json()
    sender = payload.get("from_email", "unknown")
    subject = payload.get("subject", "")
    body = payload.get("body", "")

    log_event("email", "inbound", sender, subject)

    # Reply via email
    anima.messages.create(
        inbox_id=resources["inbox_id"],
        to_email=sender,
        subject=f"Re: {subject}",
        body=(
            f"Thank you for contacting Acme Support.\n\n"
            f"We have received your message and will respond within 24 hours.\n\n"
            f"Best,\nAcme Support Team"
        ),
    )
    log_event("email", "outbound", sender, f"Auto-reply to: {subject}")

    # Send SMS notification if we have a phone number for the contact
    phone_number = payload.get("contact_phone")
    if phone_number:
        anima.sms.send(
            phone_id=resources["phone_id"],
            to_number=phone_number,
            body=f"We got your email about '{subject[:40]}'. We will reply within 24hrs.",
        )
        log_event("sms", "outbound", phone_number, "Email receipt notification")

    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Status endpoint
# ---------------------------------------------------------------------------


@app.get("/conversations")
async def list_conversations():
    """View all conversation events across channels."""
    return {"conversations": conversations, "total": len(conversations)}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    global resources

    print("=" * 60)
    print("  Anima Multi-Channel Agent")
    print("=" * 60)

    resources = setup_channels()

    print(f"\nAgent is live!")
    print(f"  Email: {resources['inbox_email']}")
    print(f"  Phone: {resources['phone_number']}")
    print(f"  Dashboard: http://localhost:{PORT}/conversations\n")

    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
