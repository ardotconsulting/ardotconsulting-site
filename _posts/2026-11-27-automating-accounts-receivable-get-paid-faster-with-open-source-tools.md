---
layout: post
title: "Automating Accounts Receivable: Get Paid Faster with Open Source Tools"
date: 2026-11-27
author: "ARDOT Consulting"
tags: [accounts-receivable, automation, invoicing, cash-flow, open-source, n8n, ollama, odoo]
excerpt: "Unpaid invoices are the silent killer of small business cash flow. Here's how to automate the follow-up process so you get paid on time without chasing every client manually."
---

Every small business owner knows the feeling. You sent the invoice three weeks ago. The due date came and went. You told yourself you'd follow up today, but a customer called with an urgent issue, a delivery needed signing, and suddenly it's 5 PM and the follow-up didn't happen. Tomorrow. You'll do it tomorrow.

Then tomorrow becomes next week. Next week becomes the end of the month. Now you're looking at a receivables report showing $40,000 in overdue invoices, and you can't remember which ones you've already chased and which ones you haven't.

This isn't a discipline problem. It's a systems problem. Following up on unpaid invoices is important but not urgent — exactly the kind of task that gets pushed aside by things that are both. And the cost is real. According to a Score study, the average small business invoice is paid [21 days late](https://www.score.org/resource/5-ways-get-paid-faster). That's three weeks of cash sitting in someone else's bank account while you pay your own bills on time.

The fix isn't to try harder. It's to build a system that handles follow-ups automatically — consistently, politely, and without you thinking about it. Here's how to do it with open source tools you can self-host.

## The Manual Process (And Why It Fails)

Before we automate, let's name what's broken. A typical accounts receivable process in a small business looks like this:

1. You send the invoice (manually, through your accounting tool)
2. You wait for payment
3. The due date passes
4. You notice — usually during a cash flow review or when your own bills are due
5. You send a reminder email, trying to remember the right tone (firm but not aggressive)
6. You wait again
7. You follow up again, maybe by phone this time
8. You repeat for every overdue invoice, every week

The problem isn't any single step. It's the combination. Each step requires you to remember, decide, and act. Multiply that by 15 overdue invoices from 8 different clients, and you're spending hours on something a workflow can handle in seconds.

Worse, the follow-ups are inconsistent. One client gets a polite email at 15 days. Another gets a phone call at 30 days because you happened to notice it. A third gets nothing until 60 days because it slipped through the cracks. Clients notice this inconsistency, and it affects how seriously they take your payment terms.

## What an Automated AR System Does

An automated accounts receivable system handles three things without human intervention:

**Detection.** It knows when an invoice is overdue, by how many days, and who owes it. This requires connecting to your invoicing tool so the workflow can check invoice status on a schedule.

**Escalation.** It sends the right message at the right time — a friendly reminder at 7 days overdue, a firmer follow-up at 30 days, and a final notice at 60 days. Each message is professional, consistent, and automatically populated with the correct invoice details.

**Visibility.** It gives you a dashboard showing exactly where things stand — total outstanding, average days to pay, which clients are chronically late — without you having to compile a spreadsheet.

The human element doesn't disappear. You still decide on payment terms, approve any write-offs, and handle the genuinely difficult conversations. But the 90% of follow-ups that are routine get handled automatically.

## The Tools

### Invoicing: Odoo or ERPNext

You need an invoicing system that exposes invoice data through an API so your automation tool can query it. Two strong open source options:

**[Odoo](https://www.odoo.com/)** (Community Edition, LGPL-3.0) has a full accounting module with invoicing, payment tracking, and multi-currency support. Its REST API lets external tools query invoice status, due dates, and client details. If you're already using Odoo for CRM or inventory — as we covered in our [Odoo setup guide](/blog/2026/09/09/setting-up-odoo-community-edition-crm-automation-for-small-business/) — the invoicing module is a natural extension.

**[ERPNext](https://erpnext.com/)** (GPL-3.0) is another solid option. We covered it in our [ERPNext self-hosting guide](/blog/2026/12/05/self-hosting-erpnext-replace-netsuite-and-sap-with-your-own-open-source-erp/). It handles invoicing, payment entry, and accounts receivable reports out of the box, with a Python API for automation.

Both tools let you mark invoices as paid, record partial payments, and track aging — all essential for an automated follow-up system.

### Automation: n8n

**[n8n](https://n8n.io/)** uses its Sustainable Use License, which permits free internal business use. It's the automation engine that ties everything together.

n8n runs on a schedule (daily, hourly, whatever you choose), connects to your invoicing system via API, checks for overdue invoices, and triggers follow-up actions. We've used n8n throughout this blog — our [first workflow guide](/blog/2026/08/17/how-to-build-your-first-ai-automation-workflow-with-n8n/) covers the basics if you're new to it.

### Email Delivery: Listmonk or SMTP

For sending reminder emails, you have two options:

**[Listmonk](https://listmonk.app/)** (AGPL-3.0) is a self-hosted email platform we covered in our [Listmonk guide](/blog/2026/10/30/self-hosting-listmonk-replace-mailchimp-with-your-own-newsletter-platform/). While it's primarily a newsletter tool, its transactional email API works well for individualized reminder emails. You create a campaign template with variables (client name, invoice number, amount, due date) and n8n populates and sends them via the API.

**Direct SMTP** is simpler if you're just sending reminders. Configure n8n with your SMTP credentials (Amazon SES, Postfix, or any transactional email service) and send emails directly from the workflow. This is the lighter-weight option — no extra software, just a connection.

### Personalized Reminders: Ollama

Here's where it gets interesting. Standard reminder templates work, but they feel generic. A client who's been with you for five years and is two days late deserves a different tone than a new client who's thirty days late.

**[Ollama](https://ollama.ai/)** (MIT) runs language models on your own server — no data leaves your infrastructure. We covered it in our [local LLM guide](/blog/2026/09/15/running-local-llms-with-ollama-a-practical-guide-for-businesses/). You can use a small model like Llama 3.2 3B to generate personalized reminder text based on the client relationship, invoice amount, and days overdue. The model takes structured inputs (client name, invoice details, relationship history) and produces a professional email body. A human reviews it before sending — or, for low-value invoices, it goes out automatically.

This isn't about replacing human judgment. It's about producing a better first draft than a static template, so the reminder feels less like a form letter and more like a genuine communication.

### Dashboard: Metabase

**[Metabase](https://www.metabase.com/)** (AGPL-3.0 for the open source edition) connects to your invoicing database and gives you a visual AR dashboard. We covered it in our [Metabase self-hosting guide](/blog/2026/09/30/self-hosting-metabase-open-source-business-analytics-without-saas/).

A useful AR dashboard shows:
- Total outstanding by aging bucket (0-30, 31-60, 61-90, 90+ days)
- Average days to pay by client
- Overdue invoice count and value
- Payment trend over time (are things getting better or worse?)

This dashboard replaces the end-of-month spreadsheet ritual. Instead of reconstructing what happened, you see what's happening, in real time, on a single screen.

## Building the Workflow: Step by Step

### Step 1: Connect n8n to Your Invoicing System

In n8n, create a scheduled trigger that runs daily (early morning is best — reminders go out before the client's day gets busy). Add an HTTP Request node that queries your invoicing API for all invoices where status is "unpaid" and due date is before today.

In Odoo, this is a call to the `/api/v2/account.move` endpoint with filters for `state = 'posted'` and `invoice_payment_state = 'not_paid'` and `invoice_date_due < today`. In ERPNext, it's the `/api/resource/Sales Invoice` endpoint with similar filters.

The API returns a JSON array of overdue invoices with client details, amounts, and due dates.

### Step 2: Calculate Days Overdue and Categorize

Add a Function node that processes each invoice and calculates days overdue. Then categorize each invoice into an escalation tier:

- **7 days overdue** — Friendly reminder (first follow-up)
- **15 days overdue** — Second reminder (slightly firmer, reference the original invoice)
- **30 days overdue** — Third reminder (firm, mention late payment terms if applicable)
- **60 days overdue** — Final notice (formal, reference potential late fees or service suspension)

The function also checks whether a reminder has already been sent for this invoice at this tier. You can track this with a simple log table in your database — or use n8n's execution history to avoid duplicate sends.

### Step 3: Generate the Reminder Content

For each overdue invoice that needs a reminder, the workflow has two paths:

**Static templates** (simpler, faster): n8n fills in a pre-written template with the client name, invoice number, amount, and due date. These are professional but generic. Good for a first pass.

**AI-generated content** (more personalized): n8n sends the invoice details and client history to a local Ollama model with a prompt like: "Write a professional but friendly payment reminder email for a client who has been with us for 3 years. Invoice #1042 for $2,400 was due on November 15. This is the first reminder." The model generates a tailored email body. You review it in n8n's execution view before it goes out — or for invoices under a threshold you set, it sends automatically.

### Step 4: Send the Email

Connect an email node — either the Listmonk API or a direct SMTP node. The email is sent from your billing address (e.g., `accounts@yourcompany.com`), includes the original invoice as a PDF attachment (downloaded via your invoicing API), and has a clear subject line: "Invoice #1042 — Payment Overdue (7 days)."

Include a payment link if your invoicing system supports online payments. Odoo and ERPNext both generate payment URLs — include them in the email so the client can pay in two clicks instead of logging into a portal and hunting for the invoice.

### Step 5: Log and Escalate

After sending, the workflow logs the action to your database: invoice ID, reminder tier, date sent, and method. This creates an audit trail — when a client says "I never got a reminder," you can see exactly what was sent and when.

At the 60-day tier, instead of just sending an email, the workflow creates a task in your project management tool (or sends a Slack message via Mattermost, which we covered in our [Mattermost guide](/blog/2026/11/14/self-hosting-mattermost-replace-slack-with-your-own-team-chat-platform/)) flagged for the business owner. At this point, it's a human conversation, not an automated email. The system's job is to surface it — not to resolve it.

### Step 6: Monitor the Dashboard

Your Metabase dashboard updates automatically as invoice data changes. Check it weekly. You're looking for:

- **Trends** — Is average days-to-pay decreasing? If so, the reminders are working.
- **Chronic late payers** — Which clients are consistently 30+ days late? These may need different payment terms (deposit upfront, shorter net terms, or a conversation about their own cash flow).
- **Reminder effectiveness** — What percentage of invoices are paid within 7 days of the first reminder? Within 30 days?

## What This Costs

All the tools above are self-hosted and free in terms of software licensing. The actual cost is infrastructure:

- A VPS to run n8n, Ollama, and your invoicing system: **$10-20/month** (a 4GB RAM VPS handles all three comfortably)
- SMTP sending costs: **$0.10 per 1,000 emails** via Amazon SES, or free via self-hosted Postfix (though deliverability requires more setup)
- Metabase runs on the same server or a separate $5/month instance

Total: **$15-25/month**, regardless of how many invoices you send or how many reminders go out. Compare that to a SaaS dunning tool like Chaser ($79/month for 250 invoices) or Notivize ($49/month per user), and the savings compound as you grow.

The real return isn't the software cost, though. It's the cash flow improvement. If your automated reminders reduce average payment time from 45 days to 30 days on $50,000 in monthly receivables, you've freed up roughly $20,000 in working capital — money that's sitting in your bank account instead of your clients'.

## When to Keep It Manual

Automation isn't the answer for every invoice. Keep these scenarios human:

**Strategic clients.** If a major client is late, a personal call from the owner carries more weight than any email. The system should flag these, not handle them.

**Disputed invoices.** If a client has raised an issue with the invoice, automated reminders are counterproductive — they escalate a conversation that needs resolution, not pressure. The workflow should check for dispute status before sending.

**First-time clients.** A new client's first late payment is information, not just a collection opportunity. It tells you about their payment culture. Handle it personally, then set the right terms for future work.

The automated system handles the 80% of reminders that are routine. The 20% that need judgment stay with you.

## Getting Started

You don't need to build the entire system at once. Start with the highest-impact piece: a daily n8n workflow that checks for invoices 7+ days overdue and sends a templated reminder email. That alone will catch most late payments before they become serious.

Once that's running smoothly, add the AI-personalized reminders, the escalation tiers, and the Metabase dashboard. Each piece builds on the last, and each one reduces the manual work a little more.

The goal isn't to remove yourself from the process entirely. It's to remove the repetitive, forgettable parts so you can focus on the conversations that actually need your attention — and spend less time wondering whether you remembered to follow up on that invoice from three weeks ago.

*Ready to stop chasing unpaid invoices? ARDOT Consulting builds automated accounts receivable systems for small businesses using open source tools you own and control. [Get in touch](/#contact) for a free consultation — we'll look at your current invoicing process and show you exactly where automation can improve your cash flow.*
