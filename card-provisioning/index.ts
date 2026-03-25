/**
 * Card Provisioning — Virtual card lifecycle with Anima.
 *
 * Demonstrates creating virtual cards for AI agents, configuring
 * spending policies, and monitoring transactions.
 */

import "dotenv/config";
import { Anima } from "@anima-labs/sdk";

// ---------------------------------------------------------------------------
// Client
// ---------------------------------------------------------------------------

const anima = new Anima({ apiKey: process.env.ANIMA_API_KEY! });

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatCents(cents: number): string {
	return `$${(cents / 100).toFixed(2)}`;
}

function divider(title: string): void {
	console.log(`\n${"─".repeat(60)}`);
	console.log(`  ${title}`);
	console.log(`${"─".repeat(60)}\n`);
}

// ---------------------------------------------------------------------------
// Step 1: Create organization and agent
// ---------------------------------------------------------------------------

async function setupAgent(): Promise<{ orgId: string; agentId: string }> {
	divider("Step 1: Create Organization & Agent");

	const org = await anima.organizations.create({
		name: "Card Demo Org",
		slug: "card-demo-org",
	});
	console.log(`Organization: ${org.name} (${org.id})`);

	const agent = await anima.agents.create({
		orgId: org.id,
		name: "Procurement Agent",
		slug: "procurement-agent",
	});
	console.log(`Agent: ${agent.name} (${agent.id})`);

	return { orgId: org.id, agentId: agent.id };
}

// ---------------------------------------------------------------------------
// Step 2: Provision a virtual card
// ---------------------------------------------------------------------------

async function createCard(agentId: string): Promise<string> {
	divider("Step 2: Provision Virtual Card");

	const card = await anima.cards.create({
		agentId,
		label: "SaaS Subscriptions",
		spendLimitMonthly: 50000, // $500.00
		spendLimitDaily: 10000, // $100.00
	});

	console.log(`Card created:`);
	console.log(`  ID:            ${card.id}`);
	console.log(`  Label:         ${card.label}`);
	console.log(`  Last 4:        ${card.last4}`);
	console.log(`  Status:        ${card.status}`);
	console.log(`  Monthly limit: ${formatCents(card.spendLimitMonthly)}`);
	console.log(`  Daily limit:   ${formatCents(card.spendLimitDaily)}`);

	return card.id;
}

// ---------------------------------------------------------------------------
// Step 3: Create spending policies
// ---------------------------------------------------------------------------

async function createPolicies(cardId: string): Promise<void> {
	divider("Step 3: Create Spending Policies");

	// Policy 1: Block gambling and adult content
	const blockPolicy = await anima.cards.createPolicy(cardId, {
		name: "Block restricted categories",
		action: "ALWAYS_DECLINE",
		blockedCategories: ["gambling", "adult_entertainment", "tobacco"],
	});
	console.log(`Policy created: "${blockPolicy.name}"`);
	console.log(`  Action: ${blockPolicy.action}`);
	console.log(`  Blocked: ${blockPolicy.blockedCategories.join(", ")}`);

	// Policy 2: Require approval for purchases over $50
	const approvalPolicy = await anima.cards.createPolicy(cardId, {
		name: "Large purchase approval",
		action: "REQUIRE_APPROVAL",
		amountThreshold: 5000, // $50.00
	});
	console.log(`\nPolicy created: "${approvalPolicy.name}"`);
	console.log(`  Action: ${approvalPolicy.action}`);
	console.log(`  Threshold: ${formatCents(approvalPolicy.amountThreshold)}`);

	// List all policies
	const policies = await anima.cards.listPolicies(cardId);
	console.log(`\nTotal policies on card: ${policies.length}`);
}

// ---------------------------------------------------------------------------
// Step 4: List cards and check status
// ---------------------------------------------------------------------------

async function listCards(agentId: string): Promise<void> {
	divider("Step 4: List Active Cards");

	const cards = await anima.cards.list({ agentId, status: "ACTIVE" });

	console.log(`Active cards for agent: ${cards.items.length}`);
	for (const card of cards.items) {
		console.log(`\n  ${card.label} (****${card.last4})`);
		console.log(`    Status:  ${card.status}`);
		console.log(`    Monthly: ${formatCents(card.spendLimitMonthly)}`);
		console.log(`    Daily:   ${formatCents(card.spendLimitDaily)}`);
	}
}

// ---------------------------------------------------------------------------
// Step 5: Check transactions
// ---------------------------------------------------------------------------

async function checkTransactions(cardId: string): Promise<void> {
	divider("Step 5: Check Recent Transactions");

	const txns = await anima.cards.listTransactions({ cardId, limit: 10 });

	if (txns.items.length === 0) {
		console.log("No transactions yet (card was just created).");
		console.log("Transactions will appear here once the card is used.");
		return;
	}

	for (const txn of txns.items) {
		console.log(`  ${txn.merchantName}`);
		console.log(`    Amount: ${formatCents(txn.amount)}`);
		console.log(`    Status: ${txn.status}`);
		console.log(`    Date:   ${txn.createdAt}`);
		console.log();
	}
}

// ---------------------------------------------------------------------------
// Step 6: Card management operations
// ---------------------------------------------------------------------------

async function manageCard(cardId: string, agentId: string): Promise<void> {
	divider("Step 6: Card Management");

	// Freeze the card
	console.log("Freezing card...");
	const frozen = await anima.cards.freeze(cardId);
	console.log(`  Status: ${frozen.status}`);

	// Unfreeze the card
	console.log("\nUnfreezing card...");
	const unfrozen = await anima.cards.unfreeze(cardId);
	console.log(`  Status: ${unfrozen.status}`);

	// Update spend limit
	console.log("\nUpdating daily limit to $200...");
	const updated = await anima.cards.update(cardId, {
		spendLimitDaily: 20000,
	});
	console.log(`  New daily limit: ${formatCents(updated.spendLimitDaily)}`);

	// Demonstrate kill switch (freeze all cards)
	console.log("\nActivating kill switch (freeze all agent cards)...");
	await anima.cards.killSwitch({ agentId, active: true });
	console.log("  All cards frozen.");

	// Deactivate kill switch
	console.log("\nDeactivating kill switch...");
	await anima.cards.killSwitch({ agentId, active: false });
	console.log("  Cards restored.");
}

// ---------------------------------------------------------------------------
// Step 7: Cleanup
// ---------------------------------------------------------------------------

async function cleanup(cardId: string): Promise<void> {
	divider("Step 7: Cleanup");

	await anima.cards.delete(cardId);
	console.log(`Card ${cardId} deleted.`);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main(): Promise<void> {
	console.log("=".repeat(60));
	console.log("  Anima Card Provisioning Example");
	console.log("=".repeat(60));

	try {
		const { orgId, agentId } = await setupAgent();
		const cardId = await createCard(agentId);
		await createPolicies(cardId);
		await listCards(agentId);
		await checkTransactions(cardId);
		await manageCard(cardId, agentId);
		await cleanup(cardId);

		divider("Done");
		console.log("Card provisioning example completed successfully.");
		console.log("See https://docs.anima.email for the full Cards API reference.");
	} catch (error) {
		console.error("Error:", error);
		process.exit(1);
	}
}

main();
