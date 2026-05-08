"""
Travel Booking Agent — Demonstrates Anima's unified platform.

This agent handles travel booking requests using Anima capabilities:
email for communication, vault for loyalty program credentials,
and AI for itinerary planning.

Flow:
  1. Create a travel agent with email + vault
  2. Store airline/hotel loyalty credentials
  3. Receive a travel request via email
  4. AI plans the itinerary and estimates costs
  5. Send itinerary confirmation email
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

AGENT_NAME = "Travel Assistant"

PLANNER_PROMPT = """You are an AI travel planner. Given a travel request,
create an itinerary and cost estimate. Return JSON:
{
  "approved": true/false,
  "destination": "City, Country",
  "dates": "Mar 15-18, 2026",
  "itinerary": [
    {"day": 1, "activities": "...", "estimated_cost": 0.00}
  ],
  "total_estimated_cost": 0.00,
  "flights": {"outbound": "...", "return": "...", "cost": 0.00},
  "hotel": {"name": "...", "nights": 0, "cost_per_night": 0.00},
  "reason": "Why this plan works or why the request was declined"
}"""

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

anima = Anima(api_key=os.environ["ANIMA_API_KEY"])
openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def plan_trip(request: str) -> dict:
    """Use GPT-4 to plan a trip and estimate costs."""
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": PLANNER_PROMPT},
            {"role": "user", "content": f"Travel request: {request}"},
        ],
        response_format={"type": "json_object"},
        temperature=0.5,
    )
    return json.loads(response.choices[0].message.content)


def main():
    print("=" * 60)
    print("  Anima Travel Booking Agent Demo")
    print("  Unified Platform: Email + Vault")
    print("=" * 60)

    # ------------------------------------------------------------------
    # Step 1: Create the travel agent
    # ------------------------------------------------------------------
    print("\n[1/5] Creating travel agent...")
    agent = anima.agents.create(name=AGENT_NAME)
    print(f"  Agent: {agent.id} ({agent.name})")

    # ------------------------------------------------------------------
    # Step 2: Store loyalty program credentials
    # ------------------------------------------------------------------
    print("\n[2/5] Storing loyalty program credentials in vault...")
    anima.vault.provision(agent_id=agent.id)

    airline_cred = anima.vault.create_credential(
        agent_id=agent.id,
        name="SkyMiles Loyalty",
        type="login",
        username="traveler@example.com",
        password="loyalty-demo-123",
        uris=["https://airline.example.com"],
    )
    print(f"  Stored: {airline_cred.name}")

    hotel_cred = anima.vault.create_credential(
        agent_id=agent.id,
        name="Hotel Rewards",
        type="login",
        username="traveler@example.com",
        password="rewards-demo-456",
        uris=["https://hotel.example.com"],
    )
    print(f"  Stored: {hotel_cred.name}")

    # ------------------------------------------------------------------
    # Step 3: AI plans the trip
    # ------------------------------------------------------------------
    travel_request = (
        "Book a 3-night trip to San Francisco for a tech conference. "
        "Need flights from NYC, a hotel near Moscone Center, and "
        "budget for meals and local transport. Max budget $1500."
    )
    print(f"\n[3/5] Planning trip: '{travel_request[:60]}...'")

    plan = plan_trip(travel_request)
    approved = plan.get("approved", False)
    print(f"  Destination: {plan.get('destination', 'N/A')}")
    print(f"  Dates: {plan.get('dates', 'N/A')}")
    print(f"  Status: {'APPROVED' if approved else 'DECLINED'}")
    print(f"  Reason: {plan.get('reason', 'N/A')}")
    print(f"  Estimated total: ${plan.get('total_estimated_cost', 0):.2f}")

    if plan.get("itinerary"):
        print("\n  Itinerary:")
        for day in plan["itinerary"]:
            print(f"    Day {day['day']}: {day['activities']} (${day.get('estimated_cost', 0):.2f})")

    if not approved:
        print("\n  Trip declined. Cleaning up...")
        anima.vault.delete_credential(agent_id=agent.id, credential_id=airline_cred.id)
        anima.vault.delete_credential(agent_id=agent.id, credential_id=hotel_cred.id)
        anima.vault.deprovision(agent_id=agent.id)
        anima.agents.delete(agent_id=agent.id)
        return

    # ------------------------------------------------------------------
    # Step 4: Retrieve loyalty credentials for booking
    # ------------------------------------------------------------------
    print("\n[4/5] Retrieving loyalty credentials...")
    airline = anima.vault.get_credential(agent_id=agent.id, credential_id=airline_cred.id)
    hotel = anima.vault.get_credential(agent_id=agent.id, credential_id=hotel_cred.id)
    print(f"  Airline: {airline.name} ({airline.username})")
    print(f"  Hotel: {hotel.name} ({hotel.username})")
    print("  (In production, agent would log in and complete bookings)")

    # ------------------------------------------------------------------
    # Step 5: Send itinerary confirmation
    # ------------------------------------------------------------------
    print("\n[5/5] Sending itinerary confirmation...")
    flights = plan.get("flights", {})
    hotel_info = plan.get("hotel", {})
    total = plan.get("total_estimated_cost", 0)

    anima.messages.send_email(
        agent_id=agent.id,
        to="traveler@example.com",
        subject=f"Trip Confirmed: {plan.get('destination', 'Your Trip')} — ${total:.2f}",
        body=f"""Hello,

Your travel assistant has planned your trip:

  Destination: {plan.get('destination', 'N/A')}
  Dates: {plan.get('dates', 'N/A')}
  Total estimate: ${total:.2f}

  Flights:
    Outbound: {flights.get('outbound', 'N/A')}
    Return: {flights.get('return', 'N/A')}
    Cost: ${flights.get('cost', 0):.2f}

  Hotel: {hotel_info.get('name', 'N/A')}
    {hotel_info.get('nights', 0)} nights @ ${hotel_info.get('cost_per_night', 0):.2f}/night

— {AGENT_NAME} (powered by Anima)""",
    )
    print("  Confirmation sent to traveler@example.com")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  Demo Complete!")
    print("=" * 60)
    print(f"""
  This demo used the following Anima services:
    - Agent Identity: Created agent '{AGENT_NAME}'
    - Vault: Stored airline + hotel loyalty credentials
    - Email: Sent itinerary confirmation

  In a real deployment, this agent would:
    - Monitor an inbox for travel requests
    - Use browser extension to fill booking forms
    - Apply loyalty points automatically
    - Handle flight changes and cancellations
""")

    # Cleanup
    print("Cleaning up demo resources...")
    anima.vault.delete_credential(agent_id=agent.id, credential_id=airline_cred.id)
    anima.vault.delete_credential(agent_id=agent.id, credential_id=hotel_cred.id)
    anima.vault.deprovision(agent_id=agent.id)
    anima.agents.delete(agent_id=agent.id)
    print("Done.")


if __name__ == "__main__":
    main()
