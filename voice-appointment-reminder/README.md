# Voice Appointment Reminder

An appointment reminder agent that calls patients to confirm upcoming appointments. Demonstrates outbound voice calling with Anima.

## How It Works

1. Provisions a phone number via Anima
2. Iterates through a list of upcoming appointments
3. Calls each patient with a friendly reminder
4. Logs confirmation status for each appointment

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

3. Edit the `APPOINTMENTS` list in `main.py` with your patient data.

4. Run the agent:

   ```bash
   python main.py
   ```

## Configuration

Adjust the `APPOINTMENTS` list and `SYSTEM_PROMPT` at the top of `main.py`.

## Learn More

- [Anima Documentation](https://docs.useanima.sh)
- [Anima Python SDK](https://pypi.org/project/anima-labs/)
