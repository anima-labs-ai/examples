# Travel Booking Agent

Demonstrates Anima's **unified platform** by combining email and vault for autonomous travel booking.

## What This Example Shows

This agent plans trips and manages itineraries — all autonomously:

```
Travel Request
       |
       v
  [AI Planning] -- GPT-4 creates itinerary and cost estimate
       |
       v
  [Vault Lookup] -- Retrieve airline + hotel loyalty credentials
       |
       v
  [Email Confirm] -- Send detailed itinerary to traveler
```

### Anima Services Used

| Service | Usage |
|---------|-------|
| **Agent Identity** | Creates a dedicated travel agent |
| **Vault** | Stores airline and hotel loyalty credentials |
| **Email** | Sends itinerary confirmation with booking details |

## Setup

1. Get an Anima API key at [console.useanima.sh](https://console.useanima.sh)
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

## Real-World Extensions

In production, this agent would:
- Monitor an email inbox for travel requests via webhooks
- Use browser extension for real booking form completion
- Automatically apply loyalty points and corporate discounts
- Handle flight changes, cancellations, and rebooking
- Use phone/SMS for urgent travel disruption alerts
