# E-Commerce Purchasing Agent

Demonstrates Anima's **unified platform** by using email, virtual cards, and vault together in a single agent workflow.

## What This Example Shows

This agent performs a complete e-commerce purchasing flow:

```
Purchase Request
       |
       v
  [AI Evaluation] ── GPT-4 decides if purchase is reasonable
       |
       v
  [Vault Lookup] ── Retrieve stored merchant credentials
       |
       v
  [Card Payment] ── Use virtual card with spending limits
       |
       v
  [Email Receipt] ── Send confirmation to owner
       |
       v
  [Card Freeze] ── Lock card after single-use transaction
```

### Anima Services Used

| Service | Usage |
|---------|-------|
| **Agent Identity** | Creates a dedicated shopping agent |
| **Vault** | Stores and retrieves merchant login credentials |
| **Cards** | Issues virtual card with daily/per-auth limits and merchant category filters |
| **Email** | Sends purchase confirmation with receipt details |
| **Security** | Freezes card after transaction to limit exposure |

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

## Expected Output

```
============================================================
  Anima E-Commerce Agent Demo
  Unified Platform: Email + Cards + Vault
============================================================

[1/7] Creating agent...
  Agent created: ag_abc123
  Name: Shopping Assistant

[2/7] Storing merchant credentials in vault...
  Credential stored: Demo Grocery Store

[3/7] Creating virtual card with spending policy...
  Card created: **** 4242
  Daily limit: $100.00
  Per-auth limit: $50.00

[4/7] Evaluating purchase: 'Buy organic milk and bread'
  AI Decision: APPROVED
  Reason: Reasonable grocery purchase within budget
  Estimated cost: $8.48

[5/7] Retrieving merchant credentials from vault...
  Retrieved credentials for: Demo Grocery Store

[6/7] Sending confirmation email...
  Confirmation email sent to owner@example.com

[7/7] Freezing card after transaction...
  Card **** 4242 frozen
```

## Real-World Extensions

In production, this agent would:
- Monitor an email inbox for purchase requests via webhooks
- Use the browser extension for real checkout form filling
- Handle multi-step authentication with stored credentials
- Track transaction history and generate expense reports
- Use phone/SMS for urgent purchase approvals
