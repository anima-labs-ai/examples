# OpenAI Terminal Agent

A terminal-based chat agent built with the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) that can send and receive emails through Anima. Chat with the agent in your terminal and ask it to check your inbox, read emails, or send messages on your behalf.

## How It Works

1. Creates an Anima inbox with a provisioned email address
2. Registers Anima email operations as tools for the OpenAI agent
3. Starts an interactive terminal session where you can chat with the agent
4. The agent can autonomously decide when to check for emails, read messages, or compose and send replies

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

## Usage

Once running, type messages in your terminal. The agent can:

- **Check inbox**: "Do I have any new emails?"
- **Read email**: "What does the latest email say?"
- **Send email**: "Send an email to alice@example.com saying I'll be there at 3pm"
- **Reply to emails**: "Reply to the last email thanking them"

Type `quit` or `exit` to stop the agent.

## Learn More

- [Anima Documentation](https://docs.useanima.sh)
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
