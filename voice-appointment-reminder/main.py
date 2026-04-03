"""
Voice Appointment Reminder — Outbound calls with copay payment via Anima.

Calls patients to remind them of appointments and offers to process
copay payments using Anima cards. Demonstrates voice + cards integration.
"""

import os
import time

from dotenv import load_dotenv

from anima import Anima

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a friendly medical office assistant calling to remind
a patient about their upcoming appointment. Be warm and professional.

Your tasks:
1. Confirm the patient's appointment date and time
2. Ask if they would like to pay their copay now over the phone
3. If yes, let them know the payment has been processed
4. If no, remind them to bring payment to their appointment
5. Ask if they have any questions about their visit

Keep the call brief and respectful."""

# Replace with your actual appointment data
APPOINTMENTS = [
    {
        "patient": "Sarah Miller",
        "phone": "+15551234010",
        "date": "Monday, April 7th at 10:00 AM",
        "doctor": "Dr. Chen",
        "copay": 25.00,
    },
    {
        "patient": "James Wilson",
        "phone": "+15551234011",
        "date": "Tuesday, April 8th at 2:30 PM",
        "doctor": "Dr. Patel",
        "copay": 40.00,
    },
    {
        "patient": "Maria Garcia",
        "phone": "+15551234012",
        "date": "Wednesday, April 9th at 9:00 AM",
        "doctor": "Dr. Chen",
        "copay": 25.00,
    },
]

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

anima = Anima()


def setup_resources() -> dict:
    """Provision a phone number and payment card."""
    print("Setting up resources...")

    phone = anima.phones.create(name="Appointment Reminders")
    print(f"  Phone: {phone.number}")

    card = anima.cards.create(
        name="Copay Collections",
        spending_limit=500.00,
    )
    print(f"  Card: **** {card.last_four}")

    return {"phone_id": phone.id, "card_id": card.id}


def remind_patient(phone_id: str, card_id: str, appt: dict) -> dict:
    """Call a patient and optionally process their copay."""
    print(f"\n  Calling {appt['patient']}...")

    try:
        call = anima.calls.create(
            phone_id=phone_id,
            to_number=appt["phone"],
            system_prompt=(
                f"{SYSTEM_PROMPT}\n\n"
                f"Patient: {appt['patient']}\n"
                f"Appointment: {appt['date']} with {appt['doctor']}\n"
                f"Copay amount: ${appt['copay']:.2f}"
            ),
            voice="nova",
        )

        result = anima.calls.wait(call_id=call.id, timeout=120)
        confirmed = result.status == "answered"

        # Check if patient agreed to pay copay (from call metadata)
        payment_accepted = getattr(result, "payment_accepted", False)
        payment_status = "not_offered"

        if confirmed and payment_accepted:
            try:
                payment = anima.cards.charge(
                    card_id=card_id,
                    amount=appt["copay"],
                    description=f"Copay - {appt['doctor']} - {appt['patient']}",
                )
                payment_status = "paid"
                print(f"  Payment processed: ${appt['copay']:.2f}")
            except Exception as e:
                payment_status = "failed"
                print(f"  Payment failed: {e}")
        elif confirmed:
            payment_status = "declined"

        print(f"  Call: {result.status} | Payment: {payment_status}")

        return {
            "patient": appt["patient"],
            "call_status": result.status,
            "confirmed": confirmed,
            "payment_status": payment_status,
        }

    except Exception as e:
        print(f"  Error: {e}")
        return {
            "patient": appt["patient"],
            "call_status": "error",
            "confirmed": False,
            "payment_status": "not_attempted",
        }


def print_report(results: list[dict]):
    """Print appointment reminder summary."""
    print("\n" + "=" * 60)
    print("  Appointment Reminder Report")
    print("=" * 60)

    confirmed = sum(1 for r in results if r["confirmed"])
    paid = sum(1 for r in results if r["payment_status"] == "paid")

    for r in results:
        status = "CONFIRMED" if r["confirmed"] else r["call_status"].upper()
        print(f"  {r['patient']:20s} | {status:12s} | Payment: {r['payment_status']}")

    print("-" * 60)
    print(f"  Confirmed: {confirmed}/{len(results)}")
    print(f"  Copays collected: {paid}/{len(results)}")


def main():
    print("=" * 60)
    print("  Anima Appointment Reminder Agent")
    print("=" * 60)

    config = setup_resources()

    print(f"\nProcessing {len(APPOINTMENTS)} appointment reminders...\n")

    results = []
    for i, appt in enumerate(APPOINTMENTS):
        print(f"[{i + 1}/{len(APPOINTMENTS)}]", end="")
        result = remind_patient(config["phone_id"], config["card_id"], appt)
        results.append(result)

        if i < len(APPOINTMENTS) - 1:
            time.sleep(3)

    print_report(results)
    anima.close()


if __name__ == "__main__":
    main()
