---
layout: post
title: "Automating Expense Reports and Receipts with Open Source Tools"
date: 2027-01-20
author: "ARDOT Consulting"
tags: [expense-reports, receipts, automation, ocr, n8n, ollama, open-source, finance, paperless-ngx]
excerpt: "Expense reports are the paperwork nobody wants to do. Receipts pile up in wallets and inboxes, someone types each one into a spreadsheet, and a manager spends an hour checking math that could have been verified automatically. Here's how to build an end-to-end expense report workflow with open source tools — no per-seat SaaS fees."
---

# Automating Expense Reports and Receipts with Open Source Tools

Every month, the same scene plays out in offices everywhere. An employee digs through their wallet, their email, and their car's glove compartment for receipts. They sit down with a spreadsheet and type in each one: the date, the vendor, the amount, the category, the project code. They get halfway through and realize they're missing a receipt from week two. They email the vendor to ask for a duplicate. They finish the spreadsheet, attach scanned receipts, and email it to their manager. The manager opens it, checks the math, approves it, and forwards it to accounting. Accounting enters the same data into their accounting system, reconciles it against the corporate card statement, and processes the reimbursement.

If that sounds familiar, you're not alone. Expense reporting is one of the most universally disliked back-office tasks in business — and one of the most wasteful. A 2023 survey by the GBTA found that the average employee spends 20 minutes per expense report, and managers spend another 15 minutes reviewing each one. For a company with 50 employees submitting monthly reports, that's over 280 hours a year spent on receipt data entry and approval. At a fully loaded labor cost of $40–60/hour, you're spending $11,000–$17,000 a year on a process that produces no value for your customers.

The good news: expense reports are almost perfectly suited to automation. The inputs are predictable (receipts have a standard structure). The logic is consistent (match amount, categorize, check policy, route for approval). The outputs go to systems you already use (accounting software, reimbursement records). And the entire workflow can be built with open source tools you may already be running.

In this post, we'll walk through a complete expense report automation built with Paperless-ngx for receipt capture, Ollama for AI-powered receipt extraction, NocoDB for expense tracking, and n8n for workflow orchestration. No per-seat expense management SaaS, no sending financial data to a third-party API, no vendor lock-in.

---

## The Problem with Manual Expense Reports

Before we get to the solution, let's be precise about what's broken. Manual expense reports fail in four specific ways:

**1. Data entry is slow and error-prone.** A typical receipt has 5–10 data points: date, vendor name, total amount, tax, individual line items, payment method, and sometimes a tip. A human typing these into a spreadsheet will make typos. A misplaced decimal point turns a $12.50 lunch into a $1,250 expense — and if nobody catches it, that's a problem at reconciliation time.

**2. Receipts get lost.** Paper receipts fade, get thrown away, or get left in hotel rooms. Digital receipts sit in inboxes that nobody searches until it's time to file. The result is incomplete reports that bounce back and forth between employee and manager until the missing receipts are found — or the expense is written off.

**3. Policy compliance is manual.** Most companies have expense policies: meals capped at $50, hotel rates under $200/night, no alcohol, pre-approval required for purchases over $500. But enforcement depends on a manager reading each line item and remembering the policy. People miss things. Inconsistent enforcement breeds resentment — "why did you reject my $55 dinner when you approved Sarah's $60 dinner last month?"

**4. Reconciliation is a separate nightmare.** After approval, someone in accounting has to match each expense report against the corporate card statement, verify the amounts, and enter the data into the accounting system. This is the same data, entered for the second or third time, by a different person, in a different system.

Automation addresses all four of these. Let's build it.

---

## The Tool Stack

| Tool | Role | Why This Tool |
|------|------|---------------|
| Paperless-ngx | Receipt capture and storage | Auto-imports emailed receipts, OCRs them, stores them searchable |
| Ollama | AI receipt extraction | Reads receipts locally, extracts structured data without sending to a cloud API |
| NocoDB | Expense tracking database | Spreadsheet-like interface that's actually a database, accessible by non-technical staff |
| n8n | Workflow orchestration | Connects everything, routes approvals, sends notifications |

All four are open source, self-hosted, and run on a single server with 8GB of RAM. If you've been following this blog's self-hosting series, you may already have some of these running.

---

## Step 1: Capture Receipts Automatically with Paperless-ngx

The first step is getting receipts into a single, searchable place without anyone having to manually scan or upload them. Paperless-ngx is built for exactly this.

If you haven't set it up yet, Paperless-ngx runs in Docker and can be deployed in about 15 minutes. The key feature for expense reports is its consumption directory and email integration:

- **Email integration:** Configure Paperless-ngx to monitor a dedicated inbox (e.g., `receipts@yourcompany.com`). Every receipt emailed to that address — from airlines, hotels, Uber, restaurants, online stores — is automatically imported, OCR'd, and stored.
- **Consumption directory:** For paper receipts, employees snap a photo with their phone and upload it to a shared folder (Nextcloud, a simple web upload form, or even an email attachment). Paperless-ngx watches that folder and imports anything dropped into it.
- **Mobile app:** Paperless-ngx has mobile apps that let employees photograph and upload receipts directly, tagging them as they go.

Once a receipt is in Paperless-ngx, it's OCR'd automatically. The full text is searchable. You can tag receipts by employee, by project, by trip — whatever taxonomy makes sense for your business.

The key setup step: create a tag called `pending-expense` and a corresponding document type called `receipt`. Every imported receipt gets these by default. This is how n8n will know which documents to process.

---

## Step 2: Extract Structured Data with Ollama

Paperless-ngx gives you searchable text. But "searchable text" isn't the same as structured data. You can search for "Hilton" and find all Hilton receipts, but you can't automatically sum up all hotel expenses for Q1 or flag a receipt that exceeds your nightly rate cap.

That's where Ollama comes in. Ollama runs language models locally on your server — no data leaves your infrastructure. For receipt extraction, a model like Llama 3.2 (8B) or Qwen 2.5 (7B) works well. These are small enough to run on a modest server and accurate enough for structured receipt extraction.

The workflow: when Paperless-ngx OCRs a receipt, n8n sends the extracted text to Ollama with a structured prompt:

```
You are a receipt data extraction assistant. Extract the following fields
from this receipt text and return them as JSON:

- vendor_name: the name of the business
- transaction_date: in YYYY-MM-DD format
- total_amount: the total paid, as a number
- tax_amount: the tax portion, as a number (0 if not shown)
- payment_method: cash, credit_card, debit_card, or other
- category: one of: meals, travel, lodging, transportation,
  office_supplies, software, other
- line_items: an array of {description, amount} objects

Receipt text:
[OCR text from Paperless-ngx]

Return only valid JSON. No explanation.
```

Ollama reads the receipt text and returns structured JSON. No more typing. No more typos. The model extracts the vendor name, date, amount, tax, and even attempts categorization based on the vendor and line items.

Is it perfect? No. OCR quality matters — a crumpled, faded receipt will produce worse results than a clean digital one. Categorization is right about 90% of the time with a well-tuned prompt. But that's the point of having a human in the loop for approval — the automation handles the 90% that's straightforward, and the human reviews the result instead of doing all the data entry.

---

## Step 3: Store and Track in NocoDB

NocoDB turns any database into a spreadsheet-like interface that non-technical staff can use. For expense tracking, create a table called `expenses` with these columns:

| Column | Type | Notes |
|--------|------|-------|
| id | Auto number | Primary key |
| employee | Single select | List of employees |
| vendor_name | Text | From Ollama extraction |
| transaction_date | Date | From Ollama extraction |
| total_amount | Decimal | From Ollama extraction |
| tax_amount | Decimal | From Ollama extraction |
| category | Single select | meals, travel, lodging, etc. |
| payment_method | Single select | cash, credit_card, etc. |
| receipt_url | URL | Link to the receipt in Paperless-ngx |
| status | Single select | pending, approved, rejected, reimbursed |
| submitted_date | Date | When the expense was submitted |
| approver | Single select | Manager responsible |
| policy_flag | Checkbox | Auto-checked if amount exceeds policy |
| policy_note | Text | Explanation of the flag |

NocoDB gives you a clean, spreadsheet-like view that anyone can use. You can create filtered views — "all pending expenses for employee X," "all policy-flagged expenses," "all expenses for project Y." You can build dashboards showing total spend by category, by employee, by month.

Because NocoDB is backed by a real database (PostgreSQL or MySQL), you can connect other tools to it. Your accounting software can pull from it. You can export to CSV for your accountant. You can build reports in Metabase or Grafana if you want deeper analysis.

---

## Step 4: Orchestrate the Workflow in n8n

n8n ties everything together. Here's the workflow, step by step:

### Trigger: New receipt in Paperless-ngx

n8n polls Paperless-ngx for documents tagged `pending-expense` every 5 minutes. When it finds one, the workflow starts.

### Step A: Extract data with Ollama

n8n sends the OCR text to Ollama using the HTTP Request node (Ollama runs a local API at `http://localhost:11434`). The prompt is the extraction template above. The response is parsed as JSON.

### Step B: Identify the employee

Paperless-ngx's document metadata includes who uploaded it (or which inbox it came from). n8n maps this to an employee in the NocoDB table using a simple lookup: if the receipt came from `jsmith@yourcompany.com`, it belongs to Jane Smith.

### Step C: Check policy compliance

n8n runs a series of policy checks against the extracted data:

```
- If category is "meals" and total_amount > 50 → policy_flag = true,
  policy_note = "Meal exceeds $50 limit"
- If category is "lodging" and total_amount > 200 → policy_flag = true,
  policy_note = "Lodging exceeds $200/night limit"
- If total_amount > 500 → policy_flag = true,
  policy_note = "Expense exceeds $500 pre-approval threshold"
- If payment_method is "cash" and total_amount > 100 → policy_flag = true,
  policy_note = "Cash expense over $100 requires receipt verification"
```

These rules are just JSON config in n8n — you can edit them without touching code. When your policy changes, you update the rules.

### Step D: Create the expense record

n8n creates a new row in the NocoDB `expenses` table with all the extracted data, the policy flag, the receipt URL, and a status of `pending`.

### Step E: Route for approval

If the expense has no policy flag, n8n sends a simple approval notification to the employee's manager via Mattermost or email:

> *New expense from Jane Smith: $48.50 at Panera Bread (meals), 2027-01-15. No policy flags. [Approve] [Reject]*

If the expense has a policy flag, the notification includes the flag:

> *New expense from Jane Smith: $235.00 at Hilton Garden Inn (lodging), 2027-01-15. POLICY FLAG: Lodging exceeds $200/night limit. [Approve] [Reject] [Request explanation]*

The manager clicks approve or reject. n8n receives the webhook and updates the NocoDB record accordingly.

### Step F: Handle approvals and rejections

- **Approved:** n8n updates the status to `approved` and sends a confirmation to the employee. If the expense is over the pre-approval threshold, it routes to a second approver (e.g., department head or finance).
- **Rejected:** n8n updates the status to `rejected` and notifies the employee with the reason. The employee can submit additional documentation or a corrected receipt.

### Step G: Reimbursement

Approved expenses accumulate in NocoDB. On a schedule you define — weekly, biweekly, or monthly — n8n generates a reimbursement summary: all approved expenses for each employee, grouped by category, with totals. This summary can be exported as a CSV and imported into your accounting system, or sent directly to accounting via an API if your accounting software supports one.

n8n also marks the Paperless-ngx document as `processed` (removing the `pending-expense` tag) so it doesn't get picked up again.

---

## What This Saves

Let's put real numbers on it. For a company with 50 employees submitting monthly expense reports:

| Task | Before (Manual) | After (Automated) | Savings |
|------|-----------------|-------------------|---------|
| Receipt collection | 10 min/employee/month | 2 min (snap and email) | 6.7 hrs/month |
| Data entry | 15 min/employee/month | 0 min (automated) | 12.5 hrs/month |
| Manager review | 10 min/report | 3 min (click approve) | 5.8 hrs/month |
| Reconciliation | 5 min/report | 1 min (export to accounting) | 3.3 hrs/month |
| **Total** | **~33 hrs/month** | **~6 hrs/month** | **~27 hrs/month** |

Over a year, that's 324 hours saved — roughly $13,000–$19,000 in labor costs at $40–$60/hour. The server running Paperless-ngx, Ollama, NocoDB, and n8n costs about $20–$40/month if you're already self-hosting other tools. Even if you're starting from scratch, the hardware costs are a fraction of what you'd pay for a per-seat expense management SaaS at $8–$15/user/month ($4,800–$9,000/year for 50 employees).

But the savings go beyond time. Automated policy checking means consistent enforcement — no more "why did you approve theirs but not mine." Structured data in NocoDB means you can actually analyze spending patterns: which categories are growing, which employees are consistently over policy, which vendors you're spending the most with. That data is invisible when expenses live in emailed spreadsheets.

---

## Getting Started: A Phased Approach

You don't have to build the entire workflow at once. Here's a practical rollout:

**Week 1: Receipt capture.** Deploy Paperless-ngx. Set up the receipts inbox. Get employees used to emailing or uploading receipts instead of keeping paper. This alone eliminates lost receipts and makes everything searchable.

**Week 2: Data extraction.** Deploy Ollama with a small model. Set up the n8n workflow to extract data from new receipts and populate NocoDB. Review the extraction accuracy for a week — tune the prompt, fix categorization errors. Expect 85–90% accuracy out of the box, improving to 95%+ with prompt refinement.

**Week 3: Policy checks and approvals.** Add the policy rules to the n8n workflow. Set up approval notifications. Train managers on the approve/reject flow. Run the automated and manual systems in parallel for a week to catch any edge cases.

**Week 4: Reconciliation and reporting.** Set up the reimbursement export. Connect to your accounting system (if it has an API) or establish the CSV import workflow. Build a NocoDB dashboard for spend analysis. Retire the old spreadsheet-based process.

---

## When This Might Not Work

Being honest about limitations:

- **Very small teams (under 10 people):** The setup time may not pay off if you only have a few expense reports a month. A shared spreadsheet with a receipt folder might be sufficient.
- **Complex multi-currency expenses:** Ollama can extract currency, but handling exchange rates and multi-currency reconciliation adds complexity. You may need additional logic in n8n or manual review of foreign-currency expenses.
- **Receipts in poor condition:** If your employees regularly submit crumpled, faded, or handwritten receipts, OCR quality will suffer. Encourage digital receipts where possible.
- **Strict audit requirements:** Some industries require specific expense report formats for audit trails. Check your requirements before replacing an existing process — NocoDB's export capabilities may need to be customized to match your audit format.

---

## Conclusion

Expense reports are a textbook automation candidate: repetitive, rules-driven, and universally disliked. By combining Paperless-ngx for capture, Ollama for extraction, NocoDB for tracking, and n8n for orchestration, you can eliminate the bulk of the manual work while keeping full control of your financial data on your own infrastructure.

The approach scales from 10 employees to 500. The tools are free and open source. The workflow is adaptable — change your expense policy, and you update a config file, not a SaaS subscription tier. And because everything is self-hosted, your financial data never leaves your server.

If you want help setting this up — whether it's deploying the tools, building the n8n workflow, or tuning the Ollama extraction prompt for your specific receipt types — [reach out to us](/#contact). We specialize in practical, open source automation for small and mid-sized businesses, and we'd be happy to walk through your expense process and design a workflow that fits.
