# Voice MCP for Claude Desktop

Use Claude Desktop to make phone calls through Anima via the Model Context Protocol (MCP). This is a configuration-only example -- no code required. Once configured, you can ask Claude to make calls, send SMS messages, and check call history using natural language.

## How It Works

1. The Anima MCP server connects Claude Desktop to Anima's voice and SMS APIs
2. Claude can provision phone numbers, make outbound calls, and send SMS
3. All interactions happen through natural language prompts in Claude Desktop

## Prerequisites

- [Claude Desktop](https://claude.ai/download) installed
- An [Anima API key](https://useanima.sh)
- Node.js 18+ (for the MCP server)

## Setup

1. Install the Anima MCP server:

   ```bash
   npm install -g @anima-labs/mcp
   ```

2. Open Claude Desktop settings and navigate to the MCP configuration file:

   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

3. Add the Anima MCP server to your configuration:

   ```json
   {
     "mcpServers": {
       "anima": {
         "command": "npx",
         "args": ["-y", "@anima-labs/mcp@latest"],
         "env": {
           "ANIMA_API_KEY": "mk_your_anima_api_key"
         }
       }
     }
   }
   ```

4. Restart Claude Desktop. You should see the Anima tools available in the MCP tools menu.

## Example Prompts

Once configured, try these prompts in Claude Desktop:

### Make a phone call

> "Call +1-555-123-4567 and ask if they have availability for a haircut appointment this Saturday afternoon."

### Send an SMS

> "Send a text message to +1-555-987-6543 saying: Hi, I'm running 10 minutes late to our meeting. Be there soon!"

### Appointment reminder

> "Call the following three numbers and remind them about their dentist appointment tomorrow at 2pm: +1-555-111-2222, +1-555-333-4444, +1-555-555-6666"

### Customer outreach

> "Call +1-555-789-0123. Introduce yourself as being from Acme Corp, ask if they received our proposal, and if they have any questions about pricing."

### Check call history

> "Show me the recent calls made from my Anima phone number."

## MCP Configuration Reference

Full configuration with all options:

```json
{
  "mcpServers": {
    "anima": {
      "command": "npx",
      "args": ["-y", "@anima-labs/mcp@latest"],
      "env": {
        "ANIMA_API_KEY": "mk_your_anima_api_key"
      }
    }
  }
}
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANIMA_API_KEY` | Yes | Your Anima API key from [useanima.sh](https://useanima.sh) |

## Available MCP Tools

Once connected, Claude Desktop will have access to these tools:

- **make_call** -- Place an outbound phone call with an AI voice agent
- **send_sms** -- Send an SMS text message
- **list_calls** -- View recent call history and transcripts
- **list_phones** -- View provisioned phone numbers
- **create_phone** -- Provision a new phone number

## Learn More

- [Anima Documentation](https://docs.useanima.sh)
- [Anima MCP Server](https://www.npmjs.com/package/@anima-labs/mcp)
- [Model Context Protocol](https://modelcontextprotocol.io)
