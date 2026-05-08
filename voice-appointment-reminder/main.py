"""
Voice Appointment Reminder — Outbound calls via Anima.

Calls patients to remind them of upcoming appointments.
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
2. Remind them to bring any required paperwork or insurance information
3. Ask if they have any questions about their visit

Keep the call brief and respectful."""

# Replace with your actual appointment data
APPOINTMENTS = [
    {
        "patient": "Sarah Miller",
        "phone": "+15551234010",
        "date": "Monday, April 7th at 10:00 AM",
        "doctor": "Dr. Chen",
    },
    {
        "patient": "James Wilson",
        "phone": "+15551234011",
        "date": "Tuesday, April 8th at 2:30 PM",
        "doctor": "Dr. Patel",
    },
    {
        "patient": "Maria Garcia",
        "phone": "+15551234012",
        "date": "Wednesday, April 9th at 9:00 AM",
        "doctor": "Dr. Chen",
    },
]

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

anima = Anima()


def setup_resources() -> dict:
    """Provision a phone number for outbound calls."""
    print("Setting up resources...")

    phone = anima.phones.create(name="Appointment Reminders")
    print(f"  Phone: {phone.number}")

    return {"phone_id": phone.id}


def remind_patient(phone_id: str, appt: dict) -> dict:
    """Call a patient with their appointment reminder."""
    print(f"\n  Calling {appt['patient']}...")

    try:
        call = anima.calls.create(
            phone_id=phone_id,
            to_number=appt["phone"],
            system_prompt=(
                f"{SYSTEM_PROMPT}\n\n"
                f"Patient: {appt['patient']}\n"
                f"Appointment: {appt['date']} with {appt['doctor']}"
            ),
            voice="nova",
        )

        result = anima.calls.wait(call_id=call.id, timeout=120)
        confirmed = result.status == "answered"

        print(f"  Call: {result.status}")

        return {
            "patient": appt["patient"],
            "call_status": result.status,
            "confirmed": confirmed,
        }

    except Exception as e:
        print(f"  Error: {e}")
        return {
            "patient": appt["patient"],
            "call_status": "error",
            "confirmed": False,
        }


def print_report(results: list[dict]):
    """Print appointment reminder summary."""
    print("\n" + "=" * 60)
    print("  Appointment Reminder Report")
    print("=" * 60)

    confirmed = sum(1 for r in results if r["confirmed"])

    for r in results:
        status = "CONFIRMED" if r["confirmed"] else r["call_status"].upper()
        print(f"  {r['patient']:20s} | {status}")

    print("-" * 60)
    print(f"  Confirmed: {confirmed}/{len(results)}")


def main():
    print("=" * 60)
    print("  Anima Appointment Reminder Agent")
    print("=" * 60)

    config = setup_resources()

    print(f"\nProcessing {len(APPOINTMENTS)} appointment reminders...\n")

    results = []
    for i, appt in enumerate(APPOINTMENTS):
        print(f"[{i + 1}/{len(APPOINTMENTS)}]", end="")
        result = remind_patient(config["phone_id"], appt)
        results.append(result)

        if i < len(APPOINTMENTS) - 1:
            time.sleep(3)

    print_report(results)
    anima.close()


if __name__ == "__main__":
    main()
