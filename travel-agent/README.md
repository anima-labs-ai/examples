# Travel Booking Agent

Demonstrates Anima's **full unified platform** by combining email, virtual cards, and vault for autonomous travel booking.

## What This Example Shows

This agent plans trips, books travel, and manages payments — all autonomously:

```
Travel Request
       |
       v
  [AI Planning] ── GPT-4 creates itinerary and cost estimate
       |
       v
  [Vault Lookup] ── Retrieve airline + hotel loyalty credentials
       |
       v
  [Card Payment] ── Travel-scoped virtual card with category filters
       |
       v
  [Email Confirm] ── Send detailed itinerary to traveler
       |
       v
  [Card Freeze] ── Lock card after booking session
```

### Anima Services Used

| Service | Usage |
|---------|-------|
| **Agent Identity** | Creates a dedicated travel agent |
| **Vault** | Stores airline and hotel loyalty credentials |
| **Cards** | Issues virtual card scoped to travel merchants (airlines, hotels, car rental) |
| **Email** | Sends itinerary confirmation with booking details |
| **Security** | Freezes card after booking to prevent unauthorized use |

## Setup

1. Get an Anima API key at [console.anima.email](https://console.anima.email)
2. Get an OpenAI API key at [platform.openai.com](https://platform.openai.com)

```bash
cp .env.example .env
# Edit .env with your API keys
```

## Run

```bash
pip install -r requirements.txt
python main.py
```

## Expected Output

```
============================================================
  Anima Travel Booking Agent Demo
  Unified Platform: Email + Cards + Vault
============================================================

[1/7] Creating travel agent...
  Agent: ag_abc123 (Travel Assistant)

[2/7] Storing loyalty program credentials in vault...
  Stored: SkyMiles Loyalty
  Stored: Hotel Rewards

[3/7] Creating travel virtual card...
  Card: **** 4242
  Daily limit: $2000.00
  Per-auth limit: $1000.00
  Allowed: Airlines, Hotels, Car Rental, Travel Agencies

[4/7] Planning trip: 'Book a 3-night trip to San Francisco...'
  Destination: San Francisco, USA
  Dates: Mar 15-18, 2026
  Status: APPROVED
  Estimated total: $1,247.00

[5/7] Retrieving loyalty credentials...
  Airline: SkyMiles Loyalty
  Hotel: Hotel Rewards

[6/7] Sending itinerary confirmation...
  Confirmation sent to traveler@example.com

[7/7] Freezing travel card...
  Card **** 4242 frozen
```

## Real-World Extensions

In production, this agent would:
- Monitor an email inbox for travel requests via webhooks
- Use browser extension for real booking form completion
- Automatically apply loyalty points and corporate discounts
- Handle flight changes, cancellations, and rebooking
- Generate expense reports and receipts for accounting
- Use phone/SMS for urgent travel disruption alerts
