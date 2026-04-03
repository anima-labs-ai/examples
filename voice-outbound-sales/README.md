# Voice Outbound Sales Agent

An outbound sales caller that works through a list of leads, makes AI-powered phone calls with a configurable sales pitch, and tracks call outcomes. Demonstrates Anima's outbound calling capabilities.

## How It Works

1. Provisions a phone number via Anima for outbound calling
2. Reads a list of leads (hardcoded in the script, easily swappable for a file or CRM)
3. Makes outbound calls to each lead with an AI sales persona
4. Tracks outcomes: answered, voicemail, no answer, callback requested
5. Prints a summary report after all calls complete

## Prerequisites

- Python 3.10+
- An [Anima API key](https://useanima.sh)

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set your environment variables:

   ```bash
   export ANIMA_API_KEY=mk_your_anima_api_key
   ```

3. Edit the `LEADS` list in `main.py` with your target numbers.

4. Run the agent:

   ```bash
   python main.py
   ```

## Configuration

Adjust the `SYSTEM_PROMPT`, `LEADS` list, and `DELAY_BETWEEN_CALLS` at the top of `main.py`.

## Learn More

- [Anima Documentation](https://docs.useanima.sh)
- [Anima Python SDK](https://pypi.org/project/anima-labs/)
