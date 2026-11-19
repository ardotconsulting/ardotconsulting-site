---
layout: post
title: "Never Miss a Contract Renewal Again: Automated Contract Tracking with Open Source Tools"
date: 2027-01-15
author: "ARDOT Consulting"
tags: [contract-management, automation, n8n, ollama, paperless-ngx, documenso, open-source]
excerpt: "Contracts expire silently and cost small businesses thousands in auto-renewals and missed renegotiations. Here's how to build an automated contract tracking system with open source tools that sends reminders before deadlines arrive."
---

# Never Miss a Contract Renewal Again: Automated Contract Tracking with Open Source Tools

Every small business has a folder somewhere — physical or digital — full of contracts that nobody looks at until something goes wrong. The software vendor auto-renews for another year at a 20% price increase. The office lease comes up for renewal and you find out with three weeks of notice. The IT provider's service agreement silently rolls over because nobody flagged the 90-day cancellation window.

These aren't rare events. A single missed cancellation deadline on a SaaS contract can mean thousands of dollars spent on software you no longer use. A missed lease renegotiation window can lock you into unfavorable terms for another year.

The fix isn't complicated. You need a system that knows what contracts you have, when they expire, and when someone needs to act. This post walks through how to build that system using open source tools you can run on your own infrastructure — no per-contract SaaS fees, no sending sensitive agreement terms to a third-party platform.

## Why Contract Management Goes Wrong

Before we build the solution, it helps to understand why this is a universal problem.

Most small businesses manage contracts the same way: someone signs the agreement, it gets filed in a shared drive or a filing cabinet, and a calendar reminder gets set — maybe. If the person who set the reminder leaves the company, the reminder leaves with them. If the contract gets amended, the original expiry date in the calendar is now wrong. If a new contract comes in and nobody thinks to add it to the calendar, it doesn't exist in the system at all.

The result is a contract portfolio that's invisible. You don't know what you have, you don't know when it expires, and you definitely don't know which contracts have auto-renewal clauses that require advance notice to cancel.

A good contract tracking system solves three problems:

1. **Centralization** — every contract lives in one searchable place
2. **Extraction** — key dates, terms, and renewal clauses are pulled out automatically
3. **Proactive alerts** — the right people get notified with enough time to act

Here's how to build that with open source tools.

## The Tool Stack

We'll use five open source tools, all self-hostable:

| Tool | Role | License |
|------|------|---------|
| **Paperless-ngx** | Document storage and OCR | GPL-3.0 |
| **Ollama** | Local AI for contract analysis | MIT |
| **n8n** | Workflow automation and alerts | Sustainable Use License (free for internal business use) |
| **Documenso** | Electronic signatures for renewed contracts | AGPL-3.0 |
| **Mattermost** | Team notifications | (see below) |

All five run on a single VPS with 8–16 GB of RAM. If you've followed our previous guides on [self-hosting Paperless-ngx](/blog/2026/10/02/going-paperless-with-paperless-ngx-open-source-document-management/) or [running local LLMs with Ollama](/blog/2026/08/20/running-local-llms-with-ollama-a-practical-guide-for-businesses/), you already have parts of this stack running.

> **On licenses:** Paperless-ngx is GPL-3.0, Ollama is MIT, Documenso is AGPL-3.0, and n8n uses its Sustainable Use License which permits free internal business use. Cal.com (MIT) and BookStack (MIT) are options we reference for scheduling and documentation, respectively. All are verified at time of writing — always double-check before relying on license terms for compliance decisions.

## Step 1: Centralize Every Contract in Paperless-ngx

Paperless-ngx is a document management system that ingests files, runs OCR on them, and makes everything full-text searchable. If you're not already using it, it takes about 30 minutes to set up with Docker.

The first step is getting every contract into Paperless-ngx. This includes:

- Vendor agreements and SaaS subscriptions
- Office or facility leases
- Service contracts (IT, cleaning, security, maintenance)
- Insurance policies
- Equipment leases and financing agreements
- Partnership or contractor agreements

Paperless-ngx watches a "consume" directory. Drop PDFs in, and they're automatically ingested, OCRed, and indexed. For physical contracts, scan them — Paperless runs Tesseract OCR under the hood, so even scanned images become searchable text.

Create a custom document type called "Contract" and tag incoming agreements as they arrive. You can also set up automated matching rules so that documents containing words like "agreement," "terms," "renewal," or "effective date" get auto-tagged as contracts. This won't be perfect, but it catches most of them and you can correct the edge cases manually.

The goal: one place where every contract lives, searchable by vendor name, contract type, or any text within the document. No more "where did we file that?" conversations.

## Step 2: Extract Key Dates and Terms with Ollama

Having all your contracts in one place is necessary but not sufficient. A PDF of a 30-page lease agreement isn't useful when you're trying to figure out what expires next month. You need the key data points extracted and structured:

- **Contract title and counterparty** — who is this with?
- **Effective date** — when did it start?
- **Expiration date** — when does it end?
- **Auto-renewal terms** — does it renew automatically? On what terms?
- **Cancellation notice period** — how much advance notice is required to cancel or renegotiate?
- **Payment terms** — what are you paying, and how often?
- **Key obligations** — anything that requires ongoing action

This is where Ollama comes in. Running a local language model on your server, you can feed it the OCR text from Paperless-ngx and ask it to extract these fields in a structured format. No contract text leaves your infrastructure — which matters, because contracts contain pricing, terms, and strategic information you don't want sitting on a third-party AI vendor's servers.

Here's the extraction prompt pattern that works well:

```
You are a contract analyst. Extract the following fields from this 
contract text and return them as a JSON object:

- contract_title: brief descriptive title
- counterparty: the other party's name
- effective_date: start date (YYYY-MM-DD)
- expiration_date: end date (YYYY-MM-DD)
- auto_renewal: true or false
- renewal_terms: description of auto-renewal conditions if applicable
- cancellation_notice_days: number of days advance notice required
- payment_amount: recurring payment amount if specified
- payment_frequency: monthly, annual, etc.
- key_obligations: list of ongoing obligations

If a field is not present in the text, use null. Do not guess.

Contract text:
{ocr_text_here}
```

For model selection, a 7B parameter model like Qwen 2.5 handles most standard business contracts. For complex legal language, a 14B model gives better accuracy. Both run on a server with 16 GB of RAM.

> **On accuracy:** AI extraction isn't perfect, especially on poorly scanned documents. Treat extracted data as a first draft. Have a human review key fields — especially expiration dates and cancellation notice periods — before relying on them. The AI reads 30 pages and pulls out the numbers. The human confirms they're correct. That's roughly 10x faster than doing it all manually.

The output is a JSON object you can store in a database — we use NocoDB or Directus for this — and query against. "Show me all contracts expiring in the next 90 days" becomes a simple database query instead of a manual document review.

## Step 3: Build the Alert Workflow in n8n

Now you have structured contract data with expiration dates and cancellation notice periods. The final piece is proactive alerts — telling the right person, with enough lead time, that action is needed.

This is a scheduled workflow in n8n that runs daily. Here's the logic:

1. **Query the contract database** for all contracts where `expiration_date` is within the next 120 days (or whatever your preferred window is).

2. **Calculate the action deadline** for each contract. If the cancellation notice period is 60 days, the action deadline is `expiration_date - 60 days`. This is the date by which someone needs to decide: renew, renegotiate, or cancel.

3. **Check whether action has already been taken.** If the contract has a status of "renewed" or "cancelled" in the database, skip it. If it's still "active" and the action deadline is approaching, generate an alert.

4. **Route the alert to the right person.** Different contracts have different owners. The IT manager handles software contracts. The office manager handles the lease. The finance lead handles insurance. Your contract database should have an `owner` field — n8n uses it to send the alert to the right person via Mattermost, email, or both.

Here's what the alert message looks like:

```
CONTRACT ACTION NEEDED

Contract: Adobe Creative Cloud — Annual Subscription
Counterparty: Adobe Inc.
Expiration: March 15, 2027
Action deadline: January 15, 2027 (60 days notice required)
Current cost: $5,988/year
Status: Auto-renews if no action taken

Options:
1. Renew as-is
2. Renegotiate terms
3. Cancel (requires written notice by Jan 15)

Contract document: [link to Paperless-ngx]
```

That message gives the contract owner everything they need to make a decision in one glance. They don't have to go hunting for the document, look up the terms, or calculate the deadline — it's all there.

### Escalation Logic

One alert isn't always enough. People get busy, messages get buried. Build a simple escalation chain:

- **120 days before expiration:** Initial notification to contract owner
- **90 days before expiration:** Reminder to contract owner
- **60 days before expiration (action deadline):** Notification to owner + their manager
- **30 days before expiration:** Notification to owner + manager + operations lead
- **7 days before expiration:** Urgent notification to all stakeholders

The escalation isn't about being annoying — it's about making sure a missed reminder doesn't become a missed deadline. If the contract gets marked as "actioned" at any point, all future alerts for that contract stop automatically.

## Step 4: Close the Loop with Documenso

When a contract owner decides to renew or renegotiate, the next step is getting signatures. If you're still printing, signing, scanning, and emailing contracts, that's another bottleneck — and another place where things get lost.

[Documenso](https://github.com/documenso/documenso) is an open source electronic signature platform that we covered in our [self-hosting guide](/blog/2026/11/11/self-hosting-documenso-replace-docusign-with-your-own-document-signing-platform/). It's AGPL-3.0 licensed and handles the full signature workflow: upload a document, place signature fields, send to signers, track status, and store the signed copy.

The integration is straightforward. When a contract is marked "renewed — pending signature" in your database, n8n can:

1. Generate the renewed contract document (from a template, with updated terms)
2. Upload it to Documenso
3. Add the required signature fields
4. Send it to the counterparty
5. When signing is complete, automatically file the signed copy back into Paperless-ngx with the updated expiration date

This closes the loop. Every contract has a lifecycle: stored → analyzed → alerted → acted on → signed → re-stored. No steps require manual data entry or document shuffling.

> **One limitation to be aware of:** Documenso uses standard electronic signatures, which are legally binding under ESIGN/UETA in the United States. If you need EU eIDAS Qualified Electronic Signatures (QES) for certain contracts, Documenso doesn't support that yet. For most small business contracts in the US, standard e-signatures are sufficient — but check with your legal counsel for specific requirements.

## What This Actually Costs

Let's break down the cost of running this system:

| Component | Cost |
|-----------|------|
| VPS (8 GB RAM, 160 GB storage) | $20–40/month |
| Paperless-ngx | Free (GPL-3.0) |
| Ollama | Free (MIT) |
| n8n | Free for internal use |
| Documenso | Free (AGPL-3.0) |
| Mattermost | Free (open source team edition) |
| Domain + SSL | $10–15/year (or free with Caddy) |

**Total: $240–480/year in hosting costs.** No per-contract fees. No per-user fees. No per-signature fees. Compare that to commercial contract management platforms, which typically charge $20–50 per user per month plus per-contract storage fees — easily $2,000–5,000/year for a small team.

The trade-off is setup time. Plan on a weekend to get the full stack running from scratch, or a few hours if you already have Paperless-ngx and Ollama deployed. The n8n workflows take another few hours to build and test. After that, maintenance is minimal — updates run through Docker, and the system largely takes care of itself.

## Getting Started: A Practical First Step

You don't need to build the whole system at once. Here's a phased approach that delivers value at each step:

**Phase 1 (Week 1): Centralize.** Get Paperless-ngx running and import every contract you can find. Tag them all as "Contract" type. This alone is a huge improvement — one searchable archive instead of scattered files.

**Phase 2 (Week 2): Extract.** Set up Ollama and run the extraction prompt against your contracts. Store the results in a simple database (NocoDB or Directus both work well). Have someone review the extracted dates and terms for accuracy.

**Phase 3 (Week 3): Alert.** Build the n8n scheduled workflow that checks for upcoming expirations and sends alerts. Start with just the 60-day and 30-day alerts — you can add the full escalation chain later.

**Phase 4 (Week 4): Sign.** Connect Documenso for the renewal signature workflow. This is the polish layer — nice to have but not essential for the first month.

By the end of week three, you have a system that will never let a contract renewal sneak up on you. Every agreement is stored, analyzed, and tracked. Every approaching deadline generates an alert to the right person with enough time to act. Renewals can be signed and filed without printing a single page.

## The Bigger Picture

Contract management is one of those operational areas that every business knows is broken but nobody wants to fix because it seems like it should be simple. "Just keep track of the dates." The reality is that tracking dates across dozens of agreements, each with different terms and notice periods, is exactly the kind of work that automation handles well and humans handle poorly.

The open source approach matters here for a specific reason: contracts contain your most sensitive commercial information — pricing, terms, obligations, strategy. Sending all of that to a SaaS contract management platform means your entire vendor negotiation position lives on someone else's server. Running the same workflow on your own infrastructure, with a local AI model that never touches the internet, means your contracts stay yours.

Start with Phase 1 this week. Get your contracts into one place. The rest follows naturally once you can actually see what you have.

*Ready to get your contract house in order? ARDOT Consulting builds automated contract management systems for small and mid-size businesses using open source tools. [Contact us](/#contact) for a free consultation — we'll audit your current contract portfolio and show you exactly where automation can prevent costly missed deadlines.*