# E-Commerce Purchasing Agent

Demonstrates Anima's **unified platform** by using email and vault together in a single agent workflow.

## What This Example Shows

This agent performs a complete e-commerce purchasing flow:

```
Purchase Request
       |
       v
  [AI Evaluation] -- GPT-4 decides if purchase is reasonable
       |
       v
  [Vault Lookup] -- Retrieve stored merchant credentials
       |
       v
  [Email Receipt] -- Send confirmation to owner
```

### Anima Services Used

| Service | Usage |
|---------|-------|
| **Agent Identity** | Creates a dedicated shopping agent |
| **Vault** | Stores and retrieves merchant login credentials |
| **Email** | Sends purchase confirmation with receipt details |

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
- Monitor an email inbox for purchase requests via webhooks
- Use the browser extension for real checkout form filling
- Handle multi-step authentication with stored credentials
- Use phone/SMS for urgent purchase approvals
