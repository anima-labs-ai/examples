/**
 * Vercel AI Agent — Streaming chat agent with Anima email tools.
 *
 * Uses the Vercel AI SDK's `streamText` with custom tools backed by
 * the Anima API for sending and receiving emails.
 */

import "dotenv/config";

import { createInterface } from "node:readline";
import { openai } from "@ai-sdk/openai";
import { Anima } from "@anima-labs/sdk";
import { streamText, tool } from "ai";
import { z } from "zod";

// ---------------------------------------------------------------------------
// Clients
// ---------------------------------------------------------------------------

const anima = new Anima({ apiKey: process.env.ANIMA_API_KEY! });

let agentId: string;
let agentEmail: string;

// ---------------------------------------------------------------------------
// Tools — Anima email operations
// ---------------------------------------------------------------------------

const emailTools = {
	listEmails: tool({
		description:
			"List recent emails in the agent's inbox. Returns email summaries with id, sender, subject, date, and a snippet of the body.",
		parameters: z.object({
			limit: z.number().optional().default(10).describe("Maximum number of emails to return"),
		}),
		execute: async ({ limit }) => {
			const messages = await anima.messages.list({
				agentId,
				channel: "EMAIL",
				limit,
			});

			return messages.items.map((msg) => ({
				id: msg.id,
				sender: msg.sender,
				subject: msg.subject,
				date: msg.createdAt,
				direction: msg.direction,
				snippet: msg.body?.slice(0, 150) ?? "",
			}));
		},
	}),

	readEmail: tool({
		description: "Read the full content of a specific email by its message ID.",
		parameters: z.object({
			messageId: z.string().describe("The ID of the email to read"),
		}),
		execute: async ({ messageId }) => {
			const msg = await anima.messages.get(messageId);

			return {
				id: msg.id,
				sender: msg.sender,
				to: msg.to,
				subject: msg.subject,
				body: msg.body,
				bodyHtml: msg.bodyHtml,
				date: msg.createdAt,
				direction: msg.direction,
				status: msg.status,
			};
		},
	}),

	sendEmail: tool({
		description:
			"Send an email from the agent's email address. Confirm details with the user before calling this tool.",
		parameters: z.object({
			to: z.string().describe("Recipient email address"),
			subject: z.string().describe("Email subject line"),
			body: z.string().describe("Plain text email body"),
		}),
		execute: async ({ to, subject, body }) => {
			const msg = await anima.messages.sendEmail({
				agentId,
				to: [to],
				subject,
				body,
			});

			return {
				id: msg.id,
				to: msg.to,
				subject: msg.subject,
				status: msg.status,
			};
		},
	}),

	searchEmails: tool({
		description: "Search emails by keyword across subject and body.",
		parameters: z.object({
			query: z.string().describe("Search term"),
			limit: z.number().optional().default(5).describe("Maximum results to return"),
		}),
		execute: async ({ query, limit }) => {
			const results = await anima.messages.search(query, {
				filters: { status: "SENT", channel: "EMAIL" },
				pagination: { limit },
			});

			return results.items.map((msg) => ({
				id: msg.id,
				sender: msg.sender,
				subject: msg.subject,
				snippet: msg.body?.slice(0, 150) ?? "",
			}));
		},
	}),
};

// ---------------------------------------------------------------------------
// Agent setup
// ---------------------------------------------------------------------------

async function setupAgent(): Promise<void> {
	console.log("Setting up Anima agent...");

	const org = await anima.organizations.create({
		name: "Vercel AI Agent Org",
		slug: "vercel-ai-agent-org",
	});

	const agent = await anima.agents.create({
		orgId: org.id,
		name: "Vercel AI Email Agent",
		slug: "vercel-ai-email-agent",
	});

	agentId = agent.id;
	agentEmail = agent.email!;

	console.log(`  Agent: ${agent.name} (${agent.id})`);
	console.log(`  Email: ${agentEmail}`);
}

// ---------------------------------------------------------------------------
// Chat loop
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
	console.log("=".repeat(60));
	console.log("  Anima + Vercel AI SDK Agent");
	console.log("=".repeat(60));

	await setupAgent();

	console.log(`\nReady! Your agent's email: ${agentEmail}`);
	console.log('Type your messages below. Type "quit" or "exit" to stop.\n');

	const rl = createInterface({
		input: process.stdin,
		output: process.stdout,
	});

	const messages: Array<{ role: "user" | "assistant"; content: string }> = [];

	const prompt = (): void => {
		rl.question("You: ", async (input) => {
			const trimmed = input.trim();
			if (!trimmed) return prompt();
			if (["quit", "exit"].includes(trimmed.toLowerCase())) {
				rl.close();
				process.exit(0);
			}

			messages.push({ role: "user", content: trimmed });

			process.stdout.write("\nAssistant: ");

			const result = streamText({
				model: openai("gpt-4o"),
				system: `You are an email assistant with access to a real email inbox via Anima.
You can list emails, read specific emails, send new emails, and search messages.
The user's email address is: ${agentEmail}
When the user asks about emails, use your tools to check the actual inbox.
When sending emails, confirm the details with the user first. Be concise and helpful.`,
				messages,
				tools: emailTools,
				maxSteps: 5,
			});

			let fullResponse = "";

			for await (const chunk of result.textStream) {
				process.stdout.write(chunk);
				fullResponse += chunk;
			}

			console.log("\n");

			messages.push({ role: "assistant", content: fullResponse });

			prompt();
		});
	};

	prompt();
}

main().catch(console.error);
