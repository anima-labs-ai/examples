# Email Agent

An AI-powered email agent that creates an Anima inbox, monitors incoming messages, and auto-replies using OpenAI GPT-4. Demonstrates the core Anima email workflow: inbox creation, message polling, and sending replies.

## How It Works

1. Creates an inbox with a provisioned email address via Anima
2. Polls for new inbound emails on a configurable interval
3. Uses OpenAI GPT-4 to generate contextual replies based on the email content
4. Sends the reply back through Anima's messaging API
5. Tracks processed messages to avoid duplicate replies

## Prerequisites

- Python 3.10+
- An [Anima API key](https://useanima.sh)
- An [OpenAI API key](https://platform.openai.com)

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Copy the environment file and fill in your keys:

   ```bash
   cp .env.example .env
   ```

   ```
   ANIMA_API_KEY=mk_your_anima_api_key
   OPENAI_API_KEY=sk-your_openai_api_key
   ```

3. Run the agent:

   ```bash
   python main.py
   ```

The agent will create an inbox, print the email address, and begin listening for incoming emails. Send an email to the printed address to see it auto-reply.

## Configuration

You can adjust the polling interval and system prompt by editing the constants at the top of `main.py`.

## Learn More

- [Anima Documentation](https://docs.useanima.sh)
- [Anima Python SDK](https://pypi.org/project/anima-labs/)
