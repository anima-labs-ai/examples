# Anima Smoke Test

Minimal verification that email and SMS send/receive work end-to-end.

## Tests

| # | Test | What it does |
|---|------|-------------|
| 1 | Send Email | Sends a test email via `messages.send_email` |
| 2 | Receive Email | Lists inbound emails via `messages.list(channel=EMAIL, direction=INBOUND)` |
| 3 | Send SMS | Sends a test SMS via `messages.send_sms` |
| 4 | Receive SMS | Lists inbound SMS via `messages.list(channel=SMS, direction=INBOUND)` |

## Setup

```bash
cd examples/smoke-test
cp .env.example .env
# Edit .env with your values
pip install -r requirements.txt
```

## Run

```bash
python smoke_test.py
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANIMA_API_KEY` | Master key or agent-scoped API key |
| `ANIMA_AGENT_ID` | Agent ID to test with |
| `TEST_EMAIL_TO` | Email address to send test email to |
| `TEST_SMS_TO` | Phone number in E.164 format (e.g. `+15551234567`) |

## Receive Tests

The receive tests check for **existing** inbound messages. To make them pass:

1. **Email**: Send an email to your agent's email address from any external mailbox
2. **SMS**: Send an SMS to your agent's provisioned phone number

Then re-run the smoke test.

## MCP Smoke Test

If you're using Claude Code with the Anima MCP, you can also test via MCP tools directly:

```
# In Claude Code, ask:
"Use the Anima MCP to: 1) send a test email, 2) list inbox, 3) send a test SMS, 4) check phone status"
```

This exercises the MCP tool layer (`email_send`, `email_list`, `phone_send_sms`, `phone_status`).
