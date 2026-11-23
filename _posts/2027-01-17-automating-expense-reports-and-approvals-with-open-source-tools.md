---
layout: post
title: "Automating Expense Reports and Approvals: Ditch the Receipt Shoebox with Open Source Tools"
date: 2027-01-17
author: "ARDOT Consulting"
tags: [expense-reports, automation, n8n, ollama, paperless-ngx, odoo, invoice-ninja, open-source]
excerpt: "Expense reports are the paperwork nobody enjoys. Here's how to build an automated expense capture, approval, and reimbursement workflow using open source tools you can self-host."
---

# Automating Expense Reports and Approvals: Ditch the Receipt Shoebox with Open Source Tools

Every small business has an expense report problem. Maybe it's the sales rep who stuffs receipts in a glovebox for three months then submits a crumpled envelope at quarter-end. Maybe it's the project manager who emails photos of lunch receipts to the bookkeeper, who manually types each one into a spreadsheet. Maybe it's the owner who reviews and approves expenses on a Saturday night because that's the only time there's room to think.

The cost adds up. A 2023 survey by GBTA found that processing a single expense report costs businesses an average of $58 in labor and takes 20 minutes of employee time. For a 15-person company submitting 30 expense reports a month, that's over $20,000 a year in administrative overhead — not counting the reimbursement delays that frustrate employees and the errors that slip through manual entry.

The fix isn't buying Expensify or Concur at $5–$9 per user per month. That adds another subscription, sends your financial data to a third party, and locks you into a per-seat pricing model that scales badly. The fix is building an automated workflow with open source tools you already run or can self-host for free.

Here's how.

## Why Expense Reports Break

Before building the solution, let's name what actually goes wrong:

1. **Capture is manual.** Employees collect paper receipts, then someone types the vendor, date, amount, and category into a spreadsheet or accounting system. Every keystroke is an opportunity for a typo — and typos in expense records create reconciliation headaches at month-end.

2. **Approval is ad hoc.** The report sits in an inbox. The approver forgets. The employee follows up with a Slack message. The approver approves verbally but nobody records it. Two weeks later, nobody remembers whether the $340 client dinner was approved.

3. **Categorization is inconsistent.** One employee calls it "Meals." Another calls it "Client Entertainment." A third calls it "Business Dining." Your chart of accounts has one category for all three, and the bookkeeper spends hours normalizing entries.

4. **Reimbursement is slow.** The approved report goes to accounting, which enters it as a bill in the accounting system, which cuts a check or initiates a transfer on the next pay cycle. Employees wait weeks for money they fronted on a personal card.

Each step is manageable. Together, they create a friction-filled process that employees avoid and finance teams dread. Automation targets each one.

## The Tool Stack

You need five capabilities: document capture, text extraction, workflow routing, approval tracking, and accounting integration. Here's the open source stack:

| Capability | Tool | What It Does |
|---|---|---|
| Document capture | **Paperless-ngx** | Scans, OCRs, and stores receipts and invoices |
| Text extraction | **Ollama** | Runs a local language model that parses receipt data into structured fields |
| Workflow engine | **n8n** | Orchestrates the flow from submission to approval to reimbursement |
| Expense management | **Odoo Community** (Expense module) or **Invoice Ninja** | Tracks expense entries, categories, and approval status |
| Notifications | **n8n + email/Matrix/Mattermost** | Alerts approvers and employees at each step |

All of these are open source and self-hostable. None of them send your financial data to a third-party cloud. Let's walk through how they connect.

## Step 1: Capture Receipts Automatically

The workflow starts when a receipt enters the system. There are three common entry points:

**Email forwarding.** Employees forward receipt emails (from airlines, hotels, online purchases, software vendors) to a dedicated address like `expenses@yourcompany.com`. An n8n workflow polls that inbox via IMAP, extracts attachments, and routes them to Paperless-ngx.

**Photo upload.** For paper receipts, employees snap a photo and upload it through a simple web form. You can build this form with **Opnform** (open source form builder) or a basic page in your existing intranet. The form submits the image to an n8n webhook, which forwards it to Paperless-ngx.

**Direct scan.** If you have a network scanner, configure it to send scanned PDFs to the same email address or a watched folder. Paperless-ngx's consume folder picks them up automatically.

Paperless-ngx applies OCR to every document the moment it arrives. This means the text on a receipt — vendor name, date, total, line items — becomes searchable and machine-readable. No manual data entry just to make the receipt findable.

## Step 2: Extract Structured Data with Local AI

Once Paperless-ngx has the receipt OCR'd, the next step is turning that unstructured text into structured fields: vendor, date, amount, tax, category. This is where Ollama comes in.

Ollama runs a language model locally on your own hardware. You don't send receipt data to OpenAI or any external API — the model runs on your server, processes the OCR text, and returns structured data that stays on your infrastructure.

Here's how to set it up:

1. **Install Ollama** on a server with at least 8GB of RAM (16GB recommended if you're running other services). Pull a model suited for structured extraction — Llama 3.2 (3B parameter) works well for receipt parsing and runs on modest hardware.

2. **Create an extraction prompt.** In n8n, build a workflow that takes the OCR text from Paperless-ngx and passes it to Ollama with a structured prompt:

   > "Extract the following fields from this receipt text and return as JSON: vendor_name, transaction_date, total_amount, tax_amount, currency, line_items (array of {description, amount}). If a field is not present, use null."

3. **Parse the response.** n8n receives JSON from Ollama and maps each field to the corresponding entry in your expense system.

This approach handles the messy reality of receipts. A hotel folio has the room rate, taxes, parking, and mini-bar on separate lines. A restaurant receipt has subtotal, tax, tip, and total. The language model can distinguish these and extract the right fields without you writing fragile regex patterns for every receipt format.

**Accuracy tip:** Start with a small batch of receipts (20–30), run them through the extraction, and manually verify the output. If the model confuses tax and tip, or misses the total on certain receipt layouts, refine the prompt. After a few iterations, you'll hit 90%+ accuracy on common receipt formats. The remaining 10% gets caught in the approval step before anything reaches accounting.

## Step 3: Route to the Right Approver

Not every expense needs the same approval path. A $12 parking receipt shouldn't require the same sign-off as a $3,000 client dinner. n8n handles this with conditional routing.

Here's a typical approval matrix you can encode in n8n:

- **Under $50, standard categories (meals, mileage, parking):** Auto-approve. Log the entry and notify the manager as a FYI.
- **$50–$500:** Route to the employee's direct manager. Send a notification via Mattermost, email, or whatever your team uses. The manager clicks an approve/reject link that triggers an n8n webhook.
- **Over $500:** Route to direct manager, then to finance. Two-step approval with a 48-hour timeout. If no action, n8n sends a reminder. If still no action after 72 hours, escalate to the business owner.

- **Client entertainment or travel over $200:** Always require two approvals regardless of amount, and flag for review against the company's entertainment policy.

n8n stores the approval state at each step. You always know who approved what, when, and how long it took. No more "I think Sarah approved that verbally" situations.

## Step 4: Track Expenses in a Central System

The structured data and approval status need to live somewhere queryable. You have two good open source options:

**Odoo Community Edition (Expense module).** Odoo has a dedicated expense management module that handles expense entries, categories, approval workflows, and reimbursement. If you're already running Odoo for CRM or accounting, this is the natural fit. The Expense module integrates with Odoo's Accounting module, so approved expenses automatically post to the right ledger accounts.

**Invoice Ninja.** If you use Invoice Ninja for invoicing, it handles expense tracking as a built-in feature. You can record expenses against clients or projects, categorize them, and pull expense reports. It doesn't have a dedicated approval workflow out of the box, but n8n can handle approval routing and push approved entries into Invoice Ninja via its API.

Either way, the n8n workflow writes the approved expense entry — vendor, date, amount, category, receipt image link — into the system via API. No human touches the data between receipt capture and the final entry. The bookkeeper reviews the entries at month-end, but they're reviewing clean, structured, pre-approved data instead of deciphering crumpled receipts.

## Step 5: Reimburse and Reconcile

The final step is getting money to the employee and making sure the books match.

**Reimbursement.** When an expense is approved, n8n can:
- Create a bill in your accounting system (Odoo, Invoice Ninja, or ERPNext) with the employee as the vendor
- Schedule the payment for the next reimbursement cycle
- Notify the employee: "Your expense report for $287.45 has been approved. Payment will be processed on [date]."

**Reconciliation.** Because every expense entry includes a link to the original receipt in Paperless-ngx, month-end reconciliation is a matter of spot-checking entries against receipts — not building them from scratch. The bookkeeper opens the expense report, clicks through to receipts as needed, and verifies totals.

**Reporting.** With all expense data in a structured system, you can build dashboards in **Metabase** (open source analytics) that show spending by category, by employee, by project, or by month. Trends become visible: "Travel spend is up 40% this quarter — is that expected?" You can't ask that question when expenses live in 15 individual spreadsheets.

## What This Looks Like in Practice

Here's the full workflow end to end:

1. Employee forwards a receipt email to `expenses@yourcompany.com` or uploads a photo through the web form.
2. n8n picks up the receipt and sends it to Paperless-ngx, which OCRs it and stores it.
3. n8n pulls the OCR text and sends it to Ollama, which extracts vendor, date, amount, tax, and line items as structured JSON.
4. n8n checks the amount and category against the approval matrix and routes accordingly.
5. The approver gets a notification with the receipt image, extracted data, and approve/reject buttons.
6. On approval, n8n creates an expense entry in Odoo or Invoice Ninja with all fields populated and a link to the receipt.
7. n8n schedules the reimbursement and notifies the employee.
8. At month-end, the bookkeeper reviews the pre-approved, pre-categorized entries and reconciles.

Total time from receipt submission to approved entry: under 10 minutes for auto-approved expenses, under 24 hours for expenses requiring manager sign-off. Compare that to the typical two-week cycle of collect, type, submit, wait, approve, enter, reconcile.

## What Not to Automate

A word of caution. Not every part of expense management should be automated:

- **Policy decisions.** Don't automate whether a category of spending is allowed. That's a policy question, not a workflow question. Define the policy clearly, then automate the enforcement.
- **Edge cases.** Receipts in foreign currencies, split expenses, or unusual vendor names will trip up the extraction model. Let these fall through to manual review rather than forcing bad data through.
- **Reimbursement timing.** Even with automation, give yourself a window to catch errors. Batch reimbursements weekly or biweekly rather than instantly — a 24-hour delay catches mistakes that instant payment locks in.

## The Cost Comparison

Let's talk numbers. Here's what this setup costs versus a SaaS expense platform:

**Self-hosted stack:**
- Paperless-ngx, n8n, Ollama, Odoo/Invoice Ninja: all free, open source
- Server: a VPS with 8GB RAM runs all of these for $20–$40/month (or use existing hardware)
- Total: $20–$40/month, flat — regardless of how many employees you have

**SaaS expense platform (Expensify, Concur, etc.):**
- $5–$9 per user per month
- 15 employees at $7/user = $105/month
- 50 employees at $7/user = $350/month
- Plus: your financial data lives on someone else's servers

The self-hosted stack pays for itself at around 3–4 employees and the savings scale linearly. More importantly, your expense data — vendor relationships, spending patterns, employee financial information — stays on infrastructure you control.

## Getting Started

You don't need to build the entire workflow at once. Start with the piece that hurts most:

1. **Week 1:** Set up Paperless-ngx and have employees start forwarding receipts to it. Even without automation, you've solved the "where do receipts live" problem.
2. **Week 2:** Add the n8n → Ollama extraction workflow. Start with one receipt format (e.g., restaurant receipts) and expand from there.
3. **Week 3:** Add approval routing for expenses over a threshold you choose.
4. **Week 4:** Connect to Odoo or Invoice Ninja for expense tracking and reporting.

Each week delivers immediate value on its own. You don't need the full pipeline running before you see benefits.

## Wrapping Up

Expense reports are the kind of process that's painful enough to complain about but not painful enough to fix — until you realize how much it's actually costing you in labor, delays, and errors. The tools to fix it are free, open source, and proven. The workflow is straightforward. The main investment is a few hours of setup and a commitment to changing how your team submits expenses.

If you want help building this workflow for your business — from standing up the tools to tuning the extraction model for your receipt types — [get in touch](/#contact). We specialize in practical automation for small businesses using open source tools that keep your data under your control.
