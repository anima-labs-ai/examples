# Card Provisioning

Provision virtual debit cards for AI agents, create spending policies to control agent spending, and list transactions. Demonstrates the full Anima Cards API: card lifecycle, policy management, and transaction monitoring.

## How It Works

1. Creates an organization and agent via Anima
2. Provisions a virtual card with monthly and daily spend limits
3. Creates spending policies (category blocks, approval requirements)
4. Lists active cards and their policies
5. Monitors recent transactions
6. Demonstrates the kill switch for emergency card freezing

## Prerequisites

- Node.js 18+
- An [Anima API key](https://useanima.sh)

## Setup

1. Install dependencies:

   ```bash
   npm install
   ```

2. Copy the environment file and fill in your key:

   ```bash
   cp .env.example .env
   ```

   ```
   ANIMA_API_KEY=mk_your_anima_api_key
   ```

3. Run the example:

   ```bash
   npx tsx index.ts
   ```

## What It Demonstrates

- **Card creation** — Provision a virtual card with configurable spend limits
- **Spending policies** — Block specific merchant categories, require approval for large purchases
- **Transaction monitoring** — List and inspect recent card transactions
- **Card management** — Freeze, unfreeze, update limits, and delete cards
- **Kill switch** — Emergency freeze all cards for an agent

## Learn More

- [Anima Documentation](https://docs.useanima.sh)
- [@anima-labs/sdk](https://www.npmjs.com/package/@anima-labs/sdk)
