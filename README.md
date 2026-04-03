# Anima Examples

Example projects demonstrating the [Anima API](https://docs.useanima.sh) — unified identity infrastructure for AI agents.

Each example is a standalone project you can clone and run. They cover email, voice calls, messaging, virtual cards, and agent orchestration using the Anima SDKs.

## Examples

| Example | Language | Description |
| --- | --- | --- |
| **Voice** | | |
| [voice-customer-support](./voice-customer-support) | Python + TS | Inbound voice support agent with webhook handling and transcription |
| [voice-outbound-sales](./voice-outbound-sales) | Python | Outbound sales caller with lead tracking and call outcome reporting |
| [voice-appointment-reminder](./voice-appointment-reminder) | Python | Appointment reminder calls with card payment processing |
| [voice-mcp-claude](./voice-mcp-claude) | Config | Make phone calls from Claude Desktop via MCP |
| **Multi-Channel** | | |
| [multi-channel-agent](./multi-channel-agent) | Python | Email + SMS + Voice combined workflow with cross-channel routing |
| **Email** | | |
| [email-agent](./email-agent) | Python | AI agent that creates an inbox, receives emails, and auto-replies using OpenAI GPT-4 |
| [openai-terminal](./openai-terminal) | Python | Terminal chat agent using the OpenAI Agents SDK with email tools powered by Anima |
| [vercel-ai-agent](./vercel-ai-agent) | TypeScript | Streaming AI agent using the Vercel AI SDK with Anima email tools |
| **Cards & Commerce** | | |
| [card-provisioning](./card-provisioning) | TypeScript | Provision virtual cards for AI agents, create spending policies, and list transactions |
| [ecommerce-agent](./ecommerce-agent) | Python | E-commerce purchasing agent using email, virtual cards, and vault together |
| **Full Agents** | | |
| [support-agent](./support-agent) | Python | Customer support agent with AI triage, email handling, and escalation |
| [travel-agent](./travel-agent) | Python | Travel booking agent combining AI planning, cards, vault, and email |

## Prerequisites

- An Anima API key — sign up at [useanima.sh](https://useanima.sh)
- Python 3.10+ (for Python examples) or Node.js 18+ (for TypeScript examples)
- An [OpenAI API key](https://platform.openai.com) (for AI-powered examples)

## Getting Started

1. Clone this repository:

   ```bash
   git clone https://github.com/anima-labs-ai/examples.git
   cd examples
   ```

2. Pick an example directory and follow its README for setup instructions.

## SDKs

- **Python**: [`anima-labs`](https://pypi.org/project/anima-labs/) — `pip install anima-labs`
- **Node.js**: [`@anima-labs/sdk`](https://www.npmjs.com/package/@anima-labs/sdk) — `npm install @anima-labs/sdk`

## Documentation

Full API documentation is available at [docs.useanima.sh](https://docs.useanima.sh).

## License

MIT
