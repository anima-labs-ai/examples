"""
Voice Customer Support — Inbound voice agent using Anima + FastAPI.

Provisions a phone number, receives incoming calls via webhook,
and handles them with an AI-powered support persona.
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

SYSTEM_PROMPT = """You are a friendly, professional customer support agent.
Listen carefully to the caller's issue, ask clarifying questions when needed,
and provide helpful solutions. Keep responses concise and conversational.
If you cannot resolve an issue, offer to escalate to a human agent.
Sign off calls politely."""

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

anima = Anima()
app = FastAPI(title="Voice Support Agent")

# In-memory transcript log
call_log: list[dict] = []

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------


def setup_phone() -> dict:
    """Provision a phone number and register the webhook."""
    print("Provisioning phone number...")
    phone = anima.phones.create(
        name="Support Line",
        webhook_url=f"{WEBHOOK_URL}/webhook/call",
    )
    print(f"  Phone number: {phone.number}")
    print(f"  Webhook: {WEBHOOK_URL}/webhook/call")
    return {"phone_id": phone.id, "number": phone.number}


# ---------------------------------------------------------------------------
# Webhook handlers
# ---------------------------------------------------------------------------


@app.post("/webhook/call")
async def handle_call(request: Request):
    """Handle incoming call events from Anima."""
    payload = await request.json()
    event_type = payload.get("type")
    call_id = payload.get("call_id")

    logging.info(f"Call event: {event_type} (call_id={call_id})")

    if event_type == "call.incoming":
        # Answer the call with our AI voice agent
        anima.calls.answer(
            call_id=call_id,
            system_prompt=SYSTEM_PROMPT,
            voice="alloy",
        )
        print(f"  Answered call {call_id}")

    elif event_type == "call.ended":
        # Log the transcript
        transcript = payload.get("transcript", "")
        duration = payload.get("duration_seconds", 0)
        caller = payload.get("from_number", "unknown")

        entry = {
            "call_id": call_id,
            "caller": caller,
            "duration": duration,
            "transcript": transcript,
            "timestamp": datetime.now().isoformat(),
        }
        call_log.append(entry)

        print(f"\n--- Call ended ---")
        print(f"  Caller: {caller}")
        print(f"  Duration: {duration}s")
        print(f"  Transcript: {transcript[:200]}...")
        print(f"  Total calls handled: {len(call_log)}")

    return {"status": "ok"}


@app.get("/calls")
async def list_calls():
    """View all call transcripts."""
    return {"calls": call_log, "total": len(call_log)}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("=" * 60)
    print("  Anima Voice Customer Support Agent")
    print("=" * 60)

    config = setup_phone()
    print(f"\nSupport line is live: {config['number']}")
    print(f"Call this number to talk to the AI agent.\n")

    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
