# Voice Appointment Reminder

An appointment reminder agent that calls patients to confirm upcoming appointments and offers to process copay payments via Anima cards. Demonstrates multi-capability usage combining voice and card payment in a single workflow.

## How It Works

1. Provisions a phone number and a virtual card via Anima
2. Iterates through a list of upcoming appointments
3. Calls each patient with a friendly reminder
4. If the patient confirms, offers to process their copay payment
5. Uses Anima cards to handle the payment transaction
6. Logs confirmation and payment status for each appointment

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
