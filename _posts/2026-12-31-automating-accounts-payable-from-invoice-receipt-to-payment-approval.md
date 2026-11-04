---
layout: post
title: "Automating Accounts Payable: From Invoice Receipt to Payment Approval"
date: 2026-12-31
author: "ARDOT Consulting"
tags: [accounts-payable, invoices, automation, ocr, n8n, ollama, open-source, finance]
excerpt: "Accounts payable is the kind of repetitive, rules-driven work that automation eats for breakfast. Here's how to build an end-to-end AP workflow with open source tools — from invoice in the inbox to approved payment, with no per-invoice SaaS fees."
---

# Automating Accounts Payable: From Invoice Receipt to Payment Approval

Every invoice that arrives in your business triggers the same journey. Someone opens an email or a PDF. They type the vendor name, invoice number, line items, and due date into your accounting system. They check it against a purchase order or a prior approval. They route it to the right person for sign-off. They wait. They follow up. They eventually schedule the payment. Then they file the invoice somewhere it can be found again at tax time.

Multiply that by 50, 200, or 1,000 invoices a month, and you have one of the most time-consuming, error-prone back-office processes in any business. Studies consistently put the cost of processing a single invoice manually at $10–$15 once you factor in labor, handling, storage, and error correction. For a company handling 300 invoices a month, that's $3,000–$4,500 a month — $36,000–$54,000 a year — spent on work that adds zero value to your customers.

Here's the thing: accounts payable is almost perfectly suited to automation. The inputs are predictable (invoices arrive in a handful of formats). The logic is consistent (match to PO, check amount, route to approver, pay by due date). The exceptions are well-defined (mismatched amounts, missing approvals, duplicate invoices). And the entire process lives in systems you already control — your email, your accounting software, your file storage.

In this post, we'll walk through a complete accounts payable automation built with open source tools: n8n for workflow orchestration, Ollama for local AI document processing, and NocoDB for tracking. No per-invoice SaaS fees, no sending financial documents to a third-party AI API, no vendor lock-in.

---

## The Manual Process (And Why It Hurts)

Before we automate, let's map the manual workflow that most small-to-mid-size businesses actually run. It usually looks something like this:

1. **Receipt.** Invoices arrive by email (as PDF attachments), through a vendor portal (where someone downloads them), by mail (scanned in), or through an EDI connection. Someone has to collect them all in one place.
2. **Data entry.** An AP clerk manually types the key fields — vendor, invoice number, date, due date, line items, subtotal, tax, total — into the accounting system. This is where most errors happen. A transposed digit on the invoice total becomes a reconciliation headache three weeks later.
3. **Matching.** If there's a purchase order, someone compares the invoice to the PO. Do the line items match? Is the quantity correct? Is the price what was agreed? This is called three-way matching (PO + invoice + receiving record), and it's tedious but essential for catching billing errors and fraud.
4. **Approval routing.** The invoice goes to a manager for approval. In many businesses, this means forwarding an email or walking a paper invoice to someone's desk. The approver reviews it, signs off (or sends it back with questions), and returns it.
5. **Payment scheduling.** Once approved, the invoice is scheduled for payment. Someone decides whether to pay early (for a discount), on time, or as late as possible without triggering a late fee. Payment is initiated through the accounting system or bank portal.
6. **Filing and audit trail.** The paid invoice gets filed — in a folder, a binder, a shared drive, or hopefully somewhere it can be found again when the auditor asks for it six months later.

Each step is individually simple. The pain comes from volume and from the handoffs — every time the invoice moves from one person to another, there's a delay, a chance of loss, and a chance of error. A typical invoice touches 3–4 people and sits idle for 5–7 days between receipt and payment. That's not because the work takes that long. It's because the routing is manual.

---

## The Automated Workflow

Here's what the same process looks like when you automate it with n8n, Ollama, and NocoDB:

```
Invoice arrives (email/PDF/scan)
        │
        ▼
  ┌─────────────┐
  │  n8n watch   │  ← Email inbox monitor or upload folder
  └─────────────┘
        │
        ▼
  ┌─────────────┐
  │  Ollama      │  ← Extract vendor, invoice #, dates, amounts, line items
  │  (local AI)  │     from the PDF using a vision-capable model
  └─────────────┘
        │
        ▼
  ┌─────────────┐
  │  Validation  │  ← Check for duplicates, missing fields, amount math
  └─────────────┘
        │
        ▼
  ┌─────────────┐
  │  PO matching │  ← Look up PO in NocoDB / accounting system, compare
  └─────────────┘
        │
        ▼
  ┌─────────────┐
  │  Approval    │  ← Route to approver based on amount/vendor rules
  │  routing     │     Notifier sends a summary + link to approve/reject
  └─────────────┘
        │
        ▼
  ┌─────────────┐
  │  Scheduling  │  ← Approved invoice queued for payment by due date
  └─────────────┘
        │
        ▼
  ┌─────────────┐
  │  NocoDB log  │  ← Full audit trail: who approved, when, original PDF
  └─────────────┘
```

Let's break down each stage.

### Stage 1: Invoice capture

The workflow starts the moment an invoice arrives. The most common entry point is email — vendors send invoices to `ap@yourcompany.com` as PDF attachments. n8n's IMAP node can monitor that inbox, and every time a new message arrives with a PDF attachment, it triggers the workflow.

For invoices that arrive through other channels — a vendor portal, EDI, or paper mail that gets scanned — you can set up a shared upload folder (using Nextcloud, for example) where anything dropped in triggers the same workflow. The goal is one entry point that captures every invoice regardless of how it arrives.

```yaml
# n8n trigger — simplified
- IMAP Email Trigger:
    mailbox: INBOX
    filter: has_attachment=true
    format: file
```

### Stage 2: Data extraction with local AI

This is where Ollama comes in. Instead of a human typing invoice fields into your accounting system, a local language model reads the PDF and extracts the structured data.

You'll want a vision-capable model — something like Llama 3.2 Vision or Qwen2.5-VL — because invoices are visual documents. The layout matters: the "total" at the bottom isn't always labeled clearly, and line items sit in columns that a text-only model might misread. A vision model can look at the invoice the way a human does.

The n8n workflow sends the PDF to Ollama with a prompt like:

```
Extract the following from this invoice as JSON:
- vendor_name
- vendor_address
- invoice_number
- invoice_date
- due_date
- line_items (array of: description, quantity, unit_price, amount)
- subtotal
- tax
- total

Return only valid JSON. If a field is not present, use null.
```

Ollama returns structured JSON. n8n parses it and passes it to the next stage. The entire extraction happens on your server — the invoice never leaves your infrastructure. For a business handling sensitive vendor pricing or financial documents, that's not a minor detail. It's the difference between automation you can actually deploy and automation your CFO blocks.

A realistic extraction takes 3–8 seconds per invoice on a modest server (16GB RAM, no GPU). With a GPU, it drops to under 2 seconds. Either way, it's faster than a human typing the same fields, and it runs 24/7 without coffee breaks.

### Stage 3: Validation

Before the extracted data goes anywhere, n8n runs a set of validation checks:

- **Duplicate detection.** Is this invoice number from this vendor already in the system? NocoDB query catches duplicates — a common source of double-payment.
- **Math check.** Do the line items add up to the subtotal? Does subtotal plus tax equal the total? If the numbers don't add up, the invoice is flagged for manual review rather than routed for approval.
- **Required fields.** Are vendor name, invoice number, date, and total all present? If the AI couldn't read something clearly, it goes to a review queue instead of silently failing.
- **Date sanity.** Is the invoice date in the past? Is the due date reasonable (not 2 years out)? Catch obvious OCR or extraction errors early.

This stage typically flags 2–5% of invoices for manual review. That's expected — the goal isn't 100% automation. It's automating the 95–98% that are straightforward and surfacing the exceptions for human attention.

### Stage 4: Purchase order matching

If your business uses purchase orders, this is where the workflow compares the invoice against the original PO. NocoDB (or your accounting system's API) holds the PO records. n8n looks up the PO number referenced on the invoice and checks:

- Does the PO exist?
- Are the line items and quantities consistent?
- Is the total within an acceptable tolerance (typically 1–2% for tax and rounding differences)?

If everything matches, the invoice is auto-approved up to a threshold you define. If there's a mismatch — wrong quantity, price above PO, missing PO — the invoice is routed to a buyer or manager for review with the discrepancy highlighted.

For businesses without formal POs (many small businesses operate on verbal or email approvals), this stage can be simplified to checking against a list of approved vendors and expected invoice ranges. The principle is the same: catch discrepancies before money moves.

### Stage 5: Approval routing

This is where automation replaces the "forward the email and wait" loop. Based on rules you define, n8n routes the invoice to the right approver:

| Rule | Approver | Action |
|------|----------|--------|
| Total < $500, PO matched | Auto-approved | Payment scheduled |
| Total $500–$5,000 | Department manager | Notification + approve/reject link |
| Total > $5,000 | CFO / Finance Director | Notification + approve/reject link |
| No PO, any amount | Purchasing manager | Review why no PO, then approve/reject |
| New vendor | Finance Director | Verify vendor, then approve/reject |

The notification can go out through whatever channel your team actually uses — email, a Mattermost message, or a ticket in your help desk system. The approver gets a summary (vendor, amount, due date, PO match status) and a single link to approve or reject. They don't need to log into a system, hunt for the invoice, and figure out where to click. One link, one decision.

If an approver doesn't respond within a configurable timeframe (say, 3 days), n8n sends a reminder. If still no response after 5 days, it escalates to the next person in the chain. No more invoices sitting in someone's inbox for two weeks because they were on vacation and nobody noticed.

### Stage 6: Payment scheduling and the audit trail

Once approved, the invoice is queued for payment. n8n calculates the optimal payment date based on:
- The vendor's payment terms (net 30, net 60, etc.)
- Early-payment discounts (if the vendor offers 2/10 net 30, paying in 10 days saves 2%)
- Your cash flow preferences (pay as late as possible without late fees, unless there's a discount)

The scheduled payment lands in NocoDB as a record with the full audit trail: original PDF, extracted data, validation results, PO match, approver name, approval timestamp, and scheduled payment date. When your auditor or CPA asks for documentation at year-end, it's all in one place — queryable, exportable, and linked to the original invoice.

---

## What This Costs (And What It Replaces)

Let's talk numbers. Here's the cost of running this automation versus the manual process and the typical AP automation SaaS.

| | Manual Process | AP Automation SaaS | Open Source Automation |
|---|---|---|---|
| **Software cost** | $0 (just your existing accounting system) | $15–$30 per user/month + $0.50–$2 per invoice | $0 |
| **Hosting** | $0 | Included | $10–$20/month (VPS) |
| **Per-invoice cost** | $10–$15 (labor + errors) | $0.50–$2 | ~$0 (electricity + amortized hardware) |
| **Data leaves your network?** | No | Yes (vendor processes your invoices) | No |
| **Customizable workflow?** | N/A | Limited to vendor's configuration | Fully — you own every rule |
| **Vendor lock-in** | N/A | High (migration is painful) | None |

For a business processing 300 invoices a month, the open source stack costs $10–$20/month in hosting. The manual process costs $3,000–$4,500/month in labor. An AP SaaS would cost $150–$600/month in per-invoice fees alone, plus user licenses. The open source approach pays for itself with the first dozen invoices it processes.

### Hardware requirements

You don't need a data center. A VPS with 8GB RAM handles the workflow orchestration (n8n) and database (NocoDB) comfortably. For the Ollama document extraction, you'll want either:

- **A server with 16GB RAM and no GPU:** Runs an 8B vision model at 3–8 seconds per invoice. Fine for up to ~500 invoices/day.
- **A server with a modest GPU (e.g., a used RTX 3060, ~$300):** Drops extraction to under 2 seconds and can handle thousands per day.

If you already have a server for other self-hosted tools (Nextcloud, Odoo, Metabase — we've covered many of these in previous posts), you can run AP automation on the same machine. These workloads don't conflict.

---

## Realistic Implementation Timeline

Don't try to build the entire workflow in a weekend. Here's how we recommend rolling it out:

**Week 1: Invoice capture and extraction.** Set up the email monitor and Ollama extraction. Get the AI reading invoices accurately. This is the foundation — if extraction is unreliable, everything downstream breaks. Test with 20–30 real invoices from different vendors. Expect to refine the prompt a few times. Vendors format invoices differently, and the model needs to handle the variety.

**Week 2: Validation and duplicate detection.** Add the checks that catch errors and duplicates. Connect to NocoDB (or your accounting system) so extracted invoices land in a tracking table. At this point, you have a system that captures, reads, and logs invoices — already a big improvement over manual entry, even before approvals are automated.

**Week 3: Approval routing.** Define your approval rules and set up the notifications. Start with a simple threshold (everything over $500 goes to a manager) and refine from there. Test the approve/reject flow end-to-end. Make sure the audit trail captures every decision.

**Week 4: Payment scheduling and PO matching.** Add the PO comparison logic and the payment date calculation. If you don't use POs, skip that part and focus on the scheduling rules. By the end of week 4, you have a complete AP workflow running.

**Weeks 5–8: Tuning and edge cases.** Run the system alongside your manual process for a month. Compare results. The AI will misread the occasional invoice — add those to a review queue and refine the prompt or add a validation rule. Approval rules will need adjusting (you'll discover edge cases like recurring invoices that don't need re-approval each month). This tuning period is normal and expected.

After 8 weeks, most businesses are running fully automated AP for 95%+ of their invoices, with the remaining 5% flowing through a manual review queue that's much smaller and more manageable than the original full-manual process.

---

## When This Approach Is Right (And When It Isn't)

This setup is a strong fit for businesses that:
- Process 50+ invoices per month (below that, the setup effort may not pay off)
- Want to keep financial documents on their own infrastructure
- Already self-host other tools or are open to it
- Have clear approval rules (even informal ones) that can be codified

It's **not** the right fit if:
- You process fewer than 20 invoices a month — the manual cost is low enough that automation isn't worth the setup
- Your invoices are wildly inconsistent (handwritten, photographed at angles, multilingual with no standard format) — extraction accuracy will suffer and you'll spend more time fixing errors than you save
- You have no one on the team comfortable with basic server administration — if Docker and a VPS are completely foreign, you'll want help with the initial setup (which is, conveniently, what we do)

---

## Common Questions

**"What if the AI reads an invoice wrong?"**
The validation stage catches most errors. Math checks flag amounts that don't add up. Duplicate detection catches double-submissions. And every invoice still goes through human approval before payment — the AI handles data entry and routing, not the final sign-off. For high-value invoices, you can require the approver to visually confirm the extracted total against the original PDF (included in the approval notification).

**"Does this work with my existing accounting software?"**
Most likely yes. If your accounting system has an API (ERPNext, Odoo, Frappe Books, Akaunting — all open source), n8n can push approved invoices directly into it. If you're using something without an API, the workflow can export a CSV or generate the entry in a format your bookkeeper imports manually. The extraction and approval automation still saves significant time even if the final accounting entry is manual.

**"What about paper invoices?"**
Scan them. A cheap document scanner (or even a phone scanner app) turns paper into PDFs. Drop the PDFs in the monitored upload folder, and the workflow treats them identically to emailed invoices. The vision model handles scanned documents well — the same technology that reads invoices off a screen reads them off a scan.

---

## The Bottom Line

Accounts payable is one of the highest-ROI automation opportunities in any business. The work is repetitive, rule-driven, and volume-heavy — exactly the conditions where automation delivers the most value. And unlike sales or customer service, where automation touches the customer experience, AP is purely internal. You can automate it aggressively without anyone outside the company noticing, except that your vendors start getting paid on time more consistently.

The open source approach — n8n, Ollama, NocoDB — gives you a system that costs essentially nothing to run, keeps your financial data on your own infrastructure, and can be customized to match your exact approval rules. The alternative is paying $0.50–$2 per invoice to a SaaS vendor forever, plus user license fees, plus the cost of migrating when they raise prices or change their terms.

If you're processing more than 50 invoices a month and still doing data entry by hand, you're leaving time and money on the table every single day. The tools are free. The workflow is proven. The question is whether you want to keep typing invoice numbers or let a system handle it.

---

*Want help building an accounts payable automation for your business? ARDOT Consulting designs and deploys open source automation systems tailored to your workflows — no SaaS lock-in, no per-invoice fees, no financial data leaving your control. [Get in touch](/#contact) and we'll map out your AP workflow.*