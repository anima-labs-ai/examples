"""
Voice Outbound Sales — AI-powered outbound sales caller using Anima.

Reads a list of leads, makes outbound calls with a sales pitch,
and tracks call outcomes.
"""

import os
import time

from dotenv import load_dotenv

from anima import Anima

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DELAY_BETWEEN_CALLS = 5  # seconds between calls

SYSTEM_PROMPT = """You are a friendly, professional sales representative for Acme Corp.
You are calling to introduce our new product line. Keep the pitch under 60 seconds.
Be respectful of the person's time. If they are not interested, thank them and end the call.
If they want more info, offer to send a follow-up email.
Never be pushy or aggressive."""

# Replace with your actual leads
LEADS = [
    {"name": "Alice Johnson", "phone": "+15551234001", "company": "TechStart Inc."},
    {"name": "Bob Smith", "phone": "+15551234002", "company": "DataFlow LLC"},
    {"name": "Carol Davis", "phone": "+15551234003", "company": "CloudNine Corp."},
]

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

anima = Anima()


def make_sales_call(phone_id: str, lead: dict) -> dict:
    """Place an outbound sales call to a lead and return the outcome."""
    print(f"\n  Calling {lead['name']} at {lead['company']}...")

    try:
        call = anima.calls.create(
            phone_id=phone_id,
            to_number=lead["phone"],
            system_prompt=(
                f"{SYSTEM_PROMPT}\n\n"
                f"You are calling {lead['name']} at {lead['company']}. "
                f"Address them by name."
            ),
            voice="alloy",
        )

        # Wait for call to complete
        result = anima.calls.wait(call_id=call.id, timeout=120)

        outcome = result.status  # answered, voicemail, no_answer, failed
        print(f"  Result: {outcome} (duration: {result.duration_seconds}s)")

        return {
            "lead": lead["name"],
            "phone": lead["phone"],
            "outcome": outcome,
            "duration": result.duration_seconds,
            "transcript": getattr(result, "transcript", ""),
        }

    except Exception as e:
        print(f"  Error calling {lead['name']}: {e}")
        return {
            "lead": lead["name"],
            "phone": lead["phone"],
            "outcome": "error",
            "duration": 0,
            "transcript": "",
        }


def print_report(results: list[dict]):
    """Print a summary of all call outcomes."""
    print("\n" + "=" * 60)
    print("  Sales Call Report")
    print("=" * 60)

    outcomes = {}
    for r in results:
        outcomes[r["outcome"]] = outcomes.get(r["outcome"], 0) + 1
        status = r["outcome"].upper()
        print(f"  {r['lead']:20s} | {r['phone']:15s} | {status}")

    print("-" * 60)
    for outcome, count in sorted(outcomes.items()):
        print(f"  {outcome}: {count}")
    print(f"  Total calls: {len(results)}")


def main():
    print("=" * 60)
    print("  Anima Outbound Sales Agent")
    print("=" * 60)

    # Provision a phone number for outbound calls
    print("\nProvisioning phone number...")
    phone = anima.phones.create(name="Sales Line")
    print(f"  Outbound number: {phone.number}")

    print(f"\nStarting {len(LEADS)} sales calls...\n")

    results = []
    for i, lead in enumerate(LEADS):
        print(f"[{i + 1}/{len(LEADS)}]", end="")
        result = make_sales_call(phone.id, lead)
        results.append(result)

        # Brief pause between calls
        if i < len(LEADS) - 1:
            time.sleep(DELAY_BETWEEN_CALLS)

    print_report(results)
    anima.close()


if __name__ == "__main__":
    main()
