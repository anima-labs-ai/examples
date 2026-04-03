/**
 * Voice Customer Support — Inbound voice agent using Anima + Express.
 *
 * Provisions a phone number, receives incoming calls via webhook,
 * and handles them with an AI-powered support persona.
 */

import Anima from "@anima-labs/sdk";
import express, { Request, Response } from "express";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const WEBHOOK_URL = process.env.WEBHOOK_URL || "http://localhost:3000";
const PORT = parseInt(process.env.PORT || "3000", 10);

const SYSTEM_PROMPT = `You are a friendly, professional customer support agent.
Listen carefully to the caller's issue, ask clarifying questions when needed,
and provide helpful solutions. Keep responses concise and conversational.
If you cannot resolve an issue, offer to escalate to a human agent.
Sign off calls politely.`;

// ---------------------------------------------------------------------------
// Clients
// ---------------------------------------------------------------------------

const anima = new Anima();
const app = express();
app.use(express.json());

interface CallEntry {
  callId: string;
  caller: string;
  duration: number;
  transcript: string;
  timestamp: string;
}

const callLog: CallEntry[] = [];

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------

async function setupPhone() {
  console.log("Provisioning phone number...");
  const phone = await anima.phones.create({
    name: "Support Line",
    webhookUrl: `${WEBHOOK_URL}/webhook/call`,
  });
  console.log(`  Phone number: ${phone.number}`);
  console.log(`  Webhook: ${WEBHOOK_URL}/webhook/call`);
  return { phoneId: phone.id, number: phone.number };
}

// ---------------------------------------------------------------------------
// Webhook handlers
// ---------------------------------------------------------------------------

app.post("/webhook/call", async (req: Request, res: Response) => {
  const { type: eventType, call_id: callId } = req.body;
  console.log(`Call event: ${eventType} (call_id=${callId})`);

  if (eventType === "call.incoming") {
    await anima.calls.answer({
      callId,
      systemPrompt: SYSTEM_PROMPT,
      voice: "alloy",
    });
    console.log(`  Answered call ${callId}`);
  } else if (eventType === "call.ended") {
    const { transcript = "", duration_seconds: duration = 0, from_number: caller = "unknown" } = req.body;

    const entry: CallEntry = {
      callId,
      caller,
      duration,
      transcript,
      timestamp: new Date().toISOString(),
    };
    callLog.push(entry);

    console.log(`\n--- Call ended ---`);
    console.log(`  Caller: ${caller}`);
    console.log(`  Duration: ${duration}s`);
    console.log(`  Transcript: ${transcript.slice(0, 200)}...`);
    console.log(`  Total calls handled: ${callLog.length}`);
  }

  res.json({ status: "ok" });
});

app.get("/calls", (_req: Request, res: Response) => {
  res.json({ calls: callLog, total: callLog.length });
});

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  console.log("=".repeat(60));
  console.log("  Anima Voice Customer Support Agent");
  console.log("=".repeat(60));

  const config = await setupPhone();
  console.log(`\nSupport line is live: ${config.number}`);
  console.log("Call this number to talk to the AI agent.\n");

  app.listen(PORT, () => {
    console.log(`Server listening on port ${PORT}`);
  });
}

main().catch(console.error);
