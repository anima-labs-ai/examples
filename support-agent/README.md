# Customer Support Agent

Demonstrates Anima's **email + vault + AI triage** by building an autonomous customer support agent.

## What This Example Shows

This agent monitors an inbox, classifies incoming messages, and sends AI-drafted responses:

```
Incoming Email
       |
       v
  [AI Triage] ── GPT-4 classifies urgency, category, sentiment
       |
       v
  [Vault Lookup] ── Retrieve CRM credentials (for production use)
       |
       v
  [Draft Response] ── AI generates context-aware reply
       |
       v
  [Send Reply] ── Respond to customer via email
       |
       v
  [Escalate?] ── Forward critical issues to manager
```

### Anima Services Used

| Service | Usage |
|---------|-------|
| **Agent Identity** | Creates a dedicated support agent |
| **Email** | Receives support requests and sends replies |
| **Vault** | Stores CRM/knowledge base credentials |

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
  Anima Customer Support Agent Demo
  Email + Vault + AI Triage
============================================================

[1/3] Creating support agent...
  Agent: ag_abc123 (Support Assistant)

[2/3] Provisioning vault for CRM credentials...
  Stored: CRM System

[3/3] Agent ready to receive support emails.

Support agent is live! Polling every 10s...

──────────────────────────────────────────────────
  From: customer@example.com
  Subject: Can't access my account
  Category: account | Urgency: high | Sentiment: negative
  Reply sent to customer@example.com
  ⚠ Escalated to manager@example.com
```

## Real-World Extensions

In production, this agent would:
- Use webhooks instead of polling for real-time responses
- Query a CRM for customer history before responding
- Route tickets to specialized sub-agents by category
- Track resolution times and customer satisfaction
- Use phone/SMS for urgent account security issues
