# Voice Customer Support Agent

An inbound voice support agent that answers customer calls using Anima's voice API and AI-powered responses. Creates a phone number, listens for incoming calls via webhooks, and handles conversations with a configurable support persona.

## How It Works

1. Provisions a phone number via Anima
2. Registers a webhook endpoint for incoming call events
3. When a call arrives, connects it to Anima's voice AI with a support system prompt
4. Logs call transcripts for review

## Prerequisites

- Python 3.10+ (or Node.js 18+)
- An [Anima API key](https://useanima.sh)
- A publicly accessible URL for webhooks (use [ngrok](https://ngrok.com) for local development)

## Setup (Python)

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

## Setup (Node.js)

1. Install dependencies:

   ```bash
   npm install
   ```

2. Set your environment variables:

   ```bash
   export ANIMA_API_KEY=mk_your_anima_api_key
   export WEBHOOK_URL=https://your-domain.ngrok.io
   ```

3. Run the agent:

   ```bash
   npx tsx main.ts
   ```

## Webhook Setup

For local development, use ngrok to expose your local server:

```bash
ngrok http 8000
```

Then set `WEBHOOK_URL` to the ngrok URL before starting the agent.

## Learn More

- [Anima Documentation](https://docs.useanima.sh)
- [Anima Python SDK](https://pypi.org/project/anima-labs/)
