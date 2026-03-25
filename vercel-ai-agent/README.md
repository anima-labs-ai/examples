# Vercel AI Agent

A streaming AI agent built with the [Vercel AI SDK](https://sdk.vercel.ai) that can send and receive emails through Anima. Demonstrates how to create custom tools backed by real infrastructure and use them in a streaming chat agent.

## How It Works

1. Creates an Anima agent with a provisioned email address
2. Defines email tools (list, read, send, search) compatible with the Vercel AI SDK
3. Runs a streaming chat loop in the terminal using `streamText` with tool support
4. The model autonomously calls email tools and streams responses back to the user

## Prerequisites

- Node.js 18+
- An [Anima API key](https://anima.email)
- An [OpenAI API key](https://platform.openai.com)

## Setup

1. Install dependencies:

   ```bash
   npm install
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
   npx tsx index.ts
   ```

## Usage

Once running, type messages in your terminal. The agent can:

- **Check inbox**: "Show me my recent emails"
- **Read email**: "Open the email from Alice"
- **Send email**: "Email bob@example.com about the meeting tomorrow"
- **Search**: "Find emails about the quarterly report"

Type `quit` or `exit` to stop the agent.

## Learn More

- [Anima Documentation](https://docs.anima.email)
- [Vercel AI SDK — Tools](https://sdk.vercel.ai/docs/ai-sdk-core/tools-and-tool-calling)
- [@anima-labs/sdk](https://www.npmjs.com/package/@anima-labs/sdk)
