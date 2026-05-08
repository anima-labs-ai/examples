"""
Anima Full-Flow Smoke Test — End-to-end verification of email and SMS.

Steps:
  1. Connect domain (brawz.ai)
  2. Create an agent with email identity
  3. Register webhooks (message.received, message.sent)
  4. Send an email
  5. Receive an email (via webhook deliveries + messages API)
  6. Provision a phone number
  7. Send an SMS
  8. Receive an SMS (via webhook deliveries + messages API)

Usage:
  cp .env.example .env   # fill in your values
  pip install -r requirements.txt
  python smoke_test.py
"""

import json
import os
import sys
import time

from dotenv import load_dotenv

from anima import Anima

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_KEY = os.environ.get("ANIMA_API_KEY", "")
ORG_ID = os.environ.get("ANIMA_ORG_ID", "")
DOMAIN = os.environ.get("ANIMA_DOMAIN", "brawz.ai")
TEST_EMAIL_TO = os.environ.get("TEST_EMAIL_TO", "")
TEST_SMS_TO = os.environ.get("TEST_SMS_TO", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")

POLL_TIMEOUT = 60
POLL_INTERVAL = 5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class StepResult:
    def __init__(self, name: str, passed: bool, detail: str = "", data: dict | None = None):
        self.name = name
        self.passed = passed
        self.detail = detail
        self.data = data or {}


def header(text: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {text}")
    print(f"{'─' * 60}")


def step(num: int, label: str) -> None:
    print(f"\n  Step {num}: {label}")


def ok(msg: str) -> None:
    print(f"    [+] {msg}")


def fail(msg: str) -> None:
    print(f"    [x] {msg}")


def info(msg: str) -> None:
    print(f"    [.] {msg}")


def dump(label: str, obj: object) -> None:
    """Pretty-print a pydantic model or dict."""
    if hasattr(obj, "model_dump"):
        data = obj.model_dump(mode="json")
    elif isinstance(obj, dict):
        data = obj
    else:
        print(f"    {label}: {obj}")
        return
    print(f"    {label}:")
    for line in json.dumps(data, indent=2).splitlines():
        print(f"      {line}")


def check_env() -> list[str]:
    missing = []
    if not API_KEY:
        missing.append("ANIMA_API_KEY")
    if not ORG_ID:
        missing.append("ANIMA_ORG_ID")
    if not TEST_EMAIL_TO:
        missing.append("TEST_EMAIL_TO")
    if not TEST_SMS_TO:
        missing.append("TEST_SMS_TO")
    return missing


def poll_for_message(client: Anima, agent_id: str, channel: str, direction: str,
                     after_id: str | None = None) -> object | None:
    """Poll messages.list until a matching message appears or timeout."""
    deadline = time.time() + POLL_TIMEOUT
    seen_ids = set()

    while time.time() < deadline:
        result = client.messages.list(
            agent_id=agent_id,
            channel=channel,
            direction=direction,
            limit=10,
        )
        for msg in result.items:
            if msg.id not in seen_ids:
                if after_id is None or msg.id != after_id:
                    return msg
            seen_ids.add(msg.id)

        remaining = int(deadline - time.time())
        info(f"Polling... {remaining}s remaining")
        time.sleep(POLL_INTERVAL)

    return None


def poll_webhook_deliveries(client: Anima, webhook_id: str, event_type: str,
                            min_count: int = 1) -> list:
    """Poll webhook deliveries until we see at least min_count for a given event."""
    deadline = time.time() + POLL_TIMEOUT
    while time.time() < deadline:
        deliveries = client.webhooks.list_deliveries(webhook_id, limit=20)
        matched = [d for d in deliveries.items if d.event.value == event_type]
        if len(matched) >= min_count:
            return matched

        remaining = int(deadline - time.time())
        info(f"Waiting for webhook delivery ({event_type})... {remaining}s remaining")
        time.sleep(POLL_INTERVAL)

    return []


# ---------------------------------------------------------------------------
# Test steps
# ---------------------------------------------------------------------------


def step_connect_domain(client: Anima) -> StepResult:
    """Step 1: Add domain and get DNS records."""
    try:
        # Check if domain already exists
        existing = client.domains.list()
        for d in existing:
            if d.domain == DOMAIN:
                info(f"Domain already registered: id={d.id}, status={d.status.value}")
                dns = client.domains.dns_records(d.id)
                dump("DNS records", dns)

                if not d.verified:
                    info("Attempting verification...")
                    verified = client.domains.verify(d.id)
                    if verified.verified:
                        ok(f"Domain verified: {DOMAIN}")
                    else:
                        info(f"Verification status: {verified.status.value} (DNS may need time to propagate)")

                return StepResult("Connect domain", True,
                                  f"id={d.id}, status={d.status.value}, verified={d.verified}",
                                  {"domain_id": d.id, "verified": d.verified})

        # Add new domain
        info(f"Adding domain: {DOMAIN}")
        domain = client.domains.add(domain=DOMAIN)
        ok(f"Domain added: id={domain.id}")
        dump("Domain", domain)

        # Get DNS records
        dns = client.domains.dns_records(domain.id)
        dump("Required DNS records", dns)

        # Try verification (may fail if DNS not propagated)
        info("Attempting verification...")
        verified = client.domains.verify(domain.id)
        verified_flag = verified.verified

        return StepResult("Connect domain", True,
                          f"id={domain.id}, verified={verified_flag}",
                          {"domain_id": domain.id, "verified": verified_flag})

    except Exception as exc:
        return StepResult("Connect domain", False, str(exc))


def step_create_agent(client: Anima) -> StepResult:
    """Step 2: Create an agent with email identity."""
    try:
        slug = "smoke-test-agent"
        email = f"smoke-test@{DOMAIN}"

        # Check if agent already exists
        agents = client.agents.list(limit=50)
        for a in agents.items:
            if a.slug == slug:
                info(f"Agent already exists: id={a.id}, name={a.name}")
                dump("Agent", a)
                return StepResult("Create agent", True,
                                  f"id={a.id}, email identities={len(a.email_identities)}",
                                  {"agent_id": a.id, "agent": a})

        # Create new agent
        info(f"Creating agent: {slug} ({email})")
        agent = client.agents.create(
            org_id=ORG_ID,
            name="Smoke Test Agent",
            slug=slug,
            email=email,
        )
        ok(f"Agent created: id={agent.id}")
        dump("Agent", agent)

        return StepResult("Create agent", True,
                          f"id={agent.id}, email={email}",
                          {"agent_id": agent.id, "agent": agent})

    except Exception as exc:
        return StepResult("Create agent", False, str(exc))


def step_register_webhook(client: Anima) -> StepResult:
    """Step 3: Register webhook for message events."""
    try:
        if not WEBHOOK_URL:
            info("No WEBHOOK_URL set — skipping webhook registration")
            info("Set WEBHOOK_URL in .env to test webhook deliveries")
            info("(Use https://webhook.site for a free test endpoint)")
            return StepResult("Register webhook", True,
                              "skipped (no WEBHOOK_URL)", {"webhook_id": None})

        events = ["message.received", "message.sent"]

        # Check if webhook already exists for this URL
        existing = client.webhooks.list(limit=50)
        for w in existing.items:
            if w.url == WEBHOOK_URL:
                info(f"Webhook already exists: id={w.id}")
                dump("Webhook", w)
                return StepResult("Register webhook", True,
                                  f"id={w.id} (existing)",
                                  {"webhook_id": w.id})

        info(f"Registering webhook: {WEBHOOK_URL}")
        webhook = client.webhooks.create(
            url=WEBHOOK_URL,
            events=events,
            description="Smoke test webhook for email + SMS events",
        )
        ok(f"Webhook created: id={webhook.id}")
        dump("Webhook", webhook)

        # Test webhook connectivity
        info("Testing webhook endpoint...")
        test_result = client.webhooks.test(webhook.id)
        ok(f"Webhook test delivery: id={test_result.delivery_id}")

        return StepResult("Register webhook", True,
                          f"id={webhook.id}, events={events}",
                          {"webhook_id": webhook.id})

    except Exception as exc:
        return StepResult("Register webhook", False, str(exc))


def step_send_email(client: Anima, agent_id: str) -> StepResult:
    """Step 4: Send a test email."""
    try:
        info(f"Sending email to {TEST_EMAIL_TO}...")
        msg = client.messages.send_email(
            agent_id=agent_id,
            to=[TEST_EMAIL_TO],
            subject=f"Anima Smoke Test ({time.strftime('%Y-%m-%d %H:%M:%S')})",
            body="This is an automated smoke test from Anima.\n\nIf you received this, email sending works!",
            body_html="<p>This is an automated smoke test from <strong>Anima</strong>.</p><p>If you received this, email sending works!</p>",
        )
        ok(f"Email sent: id={msg.id}, status={msg.status.value}")
        dump("Message", msg)

        return StepResult("Send email", True,
                          f"id={msg.id}, status={msg.status.value}",
                          {"message_id": msg.id})

    except Exception as exc:
        return StepResult("Send email", False, str(exc))


def step_receive_email(client: Anima, agent_id: str, webhook_id: str | None) -> StepResult:
    """Step 5: Check for inbound emails via webhook deliveries and messages API."""
    try:
        # 5a: Check webhook deliveries for message.received (EMAIL)
        if webhook_id:
            info("Checking webhook deliveries for inbound email...")
            deliveries = poll_webhook_deliveries(client, webhook_id, "message.received")
            email_deliveries = [d for d in deliveries
                                if d.payload.get("channel") == "EMAIL"
                                or d.payload.get("data", {}).get("channel") == "EMAIL"]
            if email_deliveries:
                ok(f"Webhook received {len(email_deliveries)} email delivery(ies)")
                dump("Latest delivery", email_deliveries[0])
            else:
                if deliveries:
                    info(f"Got {len(deliveries)} message.received deliveries (may include SMS)")
                    dump("Latest delivery", deliveries[0])
                else:
                    info("No webhook deliveries yet for message.received")
        else:
            info("Webhook not configured — skipping webhook delivery check")

        # 5b: Check messages API for inbound emails
        info("Checking messages API for inbound emails...")
        result = client.messages.list(
            agent_id=agent_id,
            channel="EMAIL",
            direction="INBOUND",
            limit=5,
        )
        count = len(result.items)
        if count > 0:
            ok(f"{count} inbound email(s) found via messages API")
            dump("Latest inbound email", result.items[0])
            return StepResult("Receive email", True,
                              f"{count} inbound email(s)")
        else:
            info("No inbound emails found yet")
            info(f"Send an email to this agent's address and re-run, or wait {POLL_TIMEOUT}s")

            # Poll for a bit
            msg = poll_for_message(client, agent_id, "EMAIL", "INBOUND")
            if msg:
                ok("Inbound email arrived!")
                dump("Inbound email", msg)
                return StepResult("Receive email", True, f"id={msg.id}")

            return StepResult("Receive email", False,
                              "no inbound emails — send one to the agent's address")

    except Exception as exc:
        return StepResult("Receive email", False, str(exc))


def step_provision_phone(client: Anima, agent_id: str) -> StepResult:
    """Step 6: Provision a phone number for the agent."""
    try:
        # Check if agent already has a phone number
        phones = client.phones.list(agent_id=agent_id)
        if phones:
            phone = phones[0]
            ok(f"Phone already provisioned: {phone.phone_number}")
            dump("Phone", phone)
            return StepResult("Provision phone", True,
                              f"number={phone.phone_number} (existing)",
                              {"phone_id": phone.id, "phone_number": phone.phone_number})

        # Provision new phone number
        info("Provisioning phone number...")
        phone = client.phones.provision(
            agent_id=agent_id,
            capabilities=["sms"],
        )
        ok(f"Phone provisioned: {phone.phone_number}")
        dump("Phone", phone)

        return StepResult("Provision phone", True,
                          f"number={phone.phone_number}",
                          {"phone_id": phone.id, "phone_number": phone.phone_number})

    except Exception as exc:
        return StepResult("Provision phone", False, str(exc))


def step_send_sms(client: Anima, agent_id: str) -> StepResult:
    """Step 7: Send a test SMS."""
    try:
        info(f"Sending SMS to {TEST_SMS_TO}...")
        msg = client.messages.send_sms(
            agent_id=agent_id,
            to=TEST_SMS_TO,
            body=f"Anima Smoke Test - SMS works! ({time.strftime('%H:%M:%S')})",
        )
        ok(f"SMS sent: id={msg.id}, status={msg.status.value}")
        dump("Message", msg)

        return StepResult("Send SMS", True,
                          f"id={msg.id}, status={msg.status.value}",
                          {"message_id": msg.id})

    except Exception as exc:
        return StepResult("Send SMS", False, str(exc))


def step_receive_sms(client: Anima, agent_id: str, webhook_id: str | None) -> StepResult:
    """Step 8: Check for inbound SMS via webhook deliveries and messages API."""
    try:
        # 8a: Check webhook deliveries
        if webhook_id:
            info("Checking webhook deliveries for inbound SMS...")
            deliveries = poll_webhook_deliveries(client, webhook_id, "message.received")
            sms_deliveries = [d for d in deliveries
                              if d.payload.get("channel") == "SMS"
                              or d.payload.get("data", {}).get("channel") == "SMS"]
            if sms_deliveries:
                ok(f"Webhook received {len(sms_deliveries)} SMS delivery(ies)")
                dump("Latest delivery", sms_deliveries[0])
            else:
                info("No SMS-specific webhook deliveries yet")
        else:
            info("Webhook not configured — skipping webhook delivery check")

        # 8b: Check messages API
        info("Checking messages API for inbound SMS...")
        result = client.messages.list(
            agent_id=agent_id,
            channel="SMS",
            direction="INBOUND",
            limit=5,
        )
        count = len(result.items)
        if count > 0:
            ok(f"{count} inbound SMS(s) found via messages API")
            dump("Latest inbound SMS", result.items[0])
            return StepResult("Receive SMS", True, f"{count} inbound SMS(s)")
        else:
            info("No inbound SMS found yet")
            info("Send an SMS to the agent's phone number and re-run")

            msg = poll_for_message(client, agent_id, "SMS", "INBOUND")
            if msg:
                ok("Inbound SMS arrived!")
                dump("Inbound SMS", msg)
                return StepResult("Receive SMS", True, f"id={msg.id}")

            return StepResult("Receive SMS", False,
                              "no inbound SMS — send one to the agent's phone number")

    except Exception as exc:
        return StepResult("Receive SMS", False, str(exc))


def step_check_webhook_sent(client: Anima, webhook_id: str | None) -> StepResult:
    """Bonus: verify message.sent webhook deliveries fired for outbound messages."""
    if not webhook_id:
        return StepResult("Webhook (message.sent)", True, "skipped (no webhook)")

    try:
        info("Checking webhook deliveries for message.sent...")
        deliveries = client.webhooks.list_deliveries(webhook_id, limit=20)
        sent = [d for d in deliveries.items if d.event.value == "message.sent"]
        if sent:
            ok(f"{len(sent)} message.sent delivery(ies) found")
            dump("Latest sent delivery", sent[0])
            return StepResult("Webhook (message.sent)", True, f"{len(sent)} deliveries")
        else:
            info("No message.sent deliveries yet (may arrive async)")
            return StepResult("Webhook (message.sent)", False, "no deliveries yet")

    except Exception as exc:
        return StepResult("Webhook (message.sent)", False, str(exc))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 60)
    print("  Anima Full-Flow Smoke Test")
    print("=" * 60)

    missing = check_env()
    if missing:
        print(f"\n  Missing env vars: {', '.join(missing)}")
        print("  Copy .env.example to .env and fill in your values.")
        sys.exit(1)

    client = Anima(api_key=API_KEY)
    results: list[StepResult] = []

    # Connectivity check
    header("Pre-flight")
    info("Checking API connectivity...")
    try:
        agents = client.agents.list(limit=1)
        ok(f"Connected. {len(agents.items)} agent(s) visible.")
    except Exception as exc:
        fail(f"Connection failed: {exc}")
        sys.exit(1)

    # Step 1: Domain
    header("Step 1: Connect Domain")
    step(1, f"Add and verify {DOMAIN}")
    r = step_connect_domain(client)
    results.append(r)
    (ok if r.passed else fail)(r.detail)

    # Step 2: Agent
    header("Step 2: Create Agent")
    step(2, "Create agent with email identity")
    r = step_create_agent(client)
    results.append(r)
    (ok if r.passed else fail)(r.detail)
    agent_id = r.data.get("agent_id", "")

    if not agent_id:
        fail("Cannot continue without an agent. Aborting.")
        sys.exit(1)

    # Step 3: Webhook
    header("Step 3: Register Webhook")
    step(3, "Register webhook for message events")
    r = step_register_webhook(client)
    results.append(r)
    (ok if r.passed else fail)(r.detail)
    webhook_id = r.data.get("webhook_id")

    # Step 4: Send Email
    header("Step 4: Send Email")
    step(4, f"Send test email to {TEST_EMAIL_TO}")
    r = step_send_email(client, agent_id)
    results.append(r)
    (ok if r.passed else fail)(r.detail)

    # Step 5: Receive Email
    header("Step 5: Receive Email")
    step(5, "Check inbound email (webhook + messages API)")
    r = step_receive_email(client, agent_id, webhook_id)
    results.append(r)
    (ok if r.passed else fail)(r.detail)

    # Step 6: Phone
    header("Step 6: Provision Phone")
    step(6, "Provision phone number for SMS")
    r = step_provision_phone(client, agent_id)
    results.append(r)
    (ok if r.passed else fail)(r.detail)

    # Step 7: Send SMS
    header("Step 7: Send SMS")
    step(7, f"Send test SMS to {TEST_SMS_TO}")
    r = step_send_sms(client, agent_id)
    results.append(r)
    (ok if r.passed else fail)(r.detail)

    # Step 8: Receive SMS
    header("Step 8: Receive SMS")
    step(8, "Check inbound SMS (webhook + messages API)")
    r = step_receive_sms(client, agent_id, webhook_id)
    results.append(r)
    (ok if r.passed else fail)(r.detail)

    # Bonus: Outbound webhook deliveries
    header("Step 9: Webhook Sent Events")
    step(9, "Verify outbound message webhook deliveries")
    r = step_check_webhook_sent(client, webhook_id)
    results.append(r)
    (ok if r.passed else fail)(r.detail)

    # Summary
    header("Summary")
    for r in results:
        marker = "+" if r.passed else "x"
        print(f"  [{marker}] {r.name}: {'PASS' if r.passed else 'FAIL'}  ({r.detail})")

    passed = sum(1 for r in results if r.passed)
    total = len(results)
    failed = total - passed

    print(f"\n  {passed}/{total} passed", end="")
    if failed:
        print(f", {failed} failed")
    else:
        print(" — all clear!")

    client.close()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
