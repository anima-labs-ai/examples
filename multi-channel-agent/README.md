# Multi-Channel Agent

A unified agent that handles customer inquiries across email, SMS, and voice using Anima. Routes conversations between channels -- for example, sending an email follow-up after a phone call or triggering an SMS confirmation after an email request.

## How It Works

1. Creates an agent with email, phone (voice + SMS), and webhook capabilities
2. Listens for incoming events on all channels via FastAPI webhooks
3. Routes inquiries across channels based on the interaction type:
   - Incoming call -> answers with AI voice, sends email summary after
   - Incoming SMS -> replies via SMS, escalates to call if complex
   - Incoming email -> replies via email, sends SMS notification
4. Maintains a unified conversation log across all channels

## Prerequisites

- Python 3.10+
- An [Anima API key](https://useanima.sh)
- A publicly accessible URL for webhooks (use [ngrok](https://ngrok.com) for local development)

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set your environment variables:

   ```bash
   export ANIMA_API_KEY=mk_your_anima_api_key
   export WEBHOOK_URL=https://your-domain.ngrok.io
   ```

3. Run the agent:

   ```bash
   python main.py
   ```

## Configuration

Adjust the system prompts and routing logic in `main.py`.

## Learn More

- [Anima Documentation](https://docs.useanima.sh)
- [Anima Python SDK](https://pypi.org/project/anima-labs/)
