---
layout: post
title: "AI Automation for Law Firms: Intake, Document Review, and Billing"
date: 2026-11-21
author: "ARDOT Consulting"
tags: [legal, law-firms, document-review, intake, billing, n8n, ollama, open-source, automation]
excerpt: "Small law firms lose billable hours to manual intake, document review, and billing workflows. Here's how to automate the repetitive work with open source tools — without sending confidential client data to a third-party AI service."
---

# AI Automation for Law Firms: Intake, Document Review, and Billing

If you run a small law firm, you already know the math. Every hour your attorneys spend on administrative work is an hour they're not billing. Every hour your paralegals spend sorting through discovery documents is an hour that could go to case strategy. And every prospective client who fills out an intake form on your website and waits three days for a response is a client who probably called another firm in the meantime.

The legal industry runs on time. Billable time, deadlines, statutes of limitations, court filing windows. Yet most small firms — solo practices to 20-attorney shops — still handle intake, document review, and billing with a patchwork of email, spreadsheets, and whatever practice management software they're paying for. The result is predictable: attorneys doing paralegal work, paralegals doing clerical work, and nobody doing the strategic work that actually grows the firm.

A typical small firm loses 15–25% of potential billable hours to administrative overhead. For a five-attorney firm billing $300/hour at 1,500 hours per attorney per year, that's $340,000 to $560,000 in lost revenue annually. Not because the work isn't there — because the workflow around the work is inefficient.

The standard fix is to hire more support staff. But that adds overhead, and it doesn't solve the core problem: the repetitive, pattern-based tasks that eat everyone's time are exactly the tasks software handles well. Intake screening, document sorting and indexing, time tracking, invoice generation — these follow predictable rules. They don't need a law degree. They need a workflow.

With open source tools — n8n for workflow automation and Ollama for local AI — you can automate the repetitive parts of your firm's operations while keeping confidential client data on your own server. No per-seat SaaS fees. No sending privileged information to a third-party AI API. No vendor lock-in.

In this post, we'll walk through three concrete automations for a small law firm: client intake and conflict checking, document review and organization, and automated time tracking and billing. Each is built with tools you can self-host, with real workflow examples you can adapt to your practice.

---

## The Problem in Detail

Before we talk about solutions, let's be precise about the pain points. These are based on patterns we see across small-to-mid-size firms:

### 1. Client intake is slow and inconsistent

A prospective client finds your website, fills out a contact form, and waits. Someone at the firm has to review the form, check for conflicts of interest, decide whether the case is worth taking, and respond — usually within 24–48 hours, often longer. During that window, the prospective client is shopping around. Studies show that law firms that respond to inquiries within the first hour are six times more likely to retain that client.

The bottleneck isn't that intake is complicated. It's that it's manual. Every intake form has to be read, categorized (practice area, urgency, potential value), checked against your existing client database for conflicts, and routed to the right attorney. That's 10–15 minutes of someone's time per inquiry — and if you get 20–50 inquiries per week, that's 3–12 hours of administrative work that follows the exact same pattern every time.

### 2. Document review is a time sink

Discovery in even a moderate case can produce thousands of pages — emails, contracts, financial records, correspondence. Someone has to read through all of it, identify what's relevant, flag what's privileged, and organize it for the attorneys to actually use. In small firms, this usually falls to paralegals or junior associates, and it's the single biggest consumer of non-billable time in litigation practice.

Document review isn't just slow — it's inconsistent. Different reviewers categorize things differently. Important documents get missed. Privileged communications slip through. And when a new attorney joins the case, they have to re-orient themselves to however the last person organized things.

The AI part of document review isn't about replacing legal judgment. It's about the first pass — sorting, categorizing, flagging, and indexing — so your attorneys start with an organized, searchable set of documents instead of a raw dump of files.

### 3. Time tracking and billing are afterthoughts

Most attorneys track their time the same way they have for decades: contemporaneous notes, end-of-day reconstruction, or "best estimate" at the end of the month when invoices go out. The result is lost time. Studies consistently show that attorneys under-bill by 5–15% simply because they can't accurately reconstruct what they did three weeks ago.

Then there's the invoice generation process itself. Time entries have to be reviewed, formatted, matched to client matters, and assembled into a professional invoice. For firms with 20–30 active matters, that's 8–15 hours of administrative work per month — time that no one is billing for.

---

## The Open Source Stack

Before we get into the workflows, here's what we're using and why:

- **n8n** — A self-hostable workflow automation tool. Think Zapier, but you run it on your own server and there are no per-task fees. n8n connects your practice management system, email, document storage, and AI models into automated workflows. Your data never leaves your infrastructure.

- **Ollama** — A tool for running large language models locally, on your own hardware. No client data ever leaves your server. For legal workflows, a model like Llama 3.1 (8B) or Qwen 2.5 (7B) running on a modest server handles the language tasks we need — categorizing intake responses, summarizing documents, generating time entry descriptions — without sending a single privileged word to a third-party API.

- **Cal.com** — Open-source appointment scheduling (MIT licensed). Used for self-service consultation booking. Prospective clients can book a consultation directly from your website, and the booking drops into your attorneys' calendars automatically.

- **Kimai** — Open-source time tracking (AGPL-3.0 licensed). Your attorneys track time against client matters, and the data feeds directly into automated invoice generation. No per-user SaaS fees.

- **Documenso** — Open-source document signing (AGPL-3.0 licensed). For engagement letters, retainer agreements, and any document that needs a client signature. Replaces DocuSign without the per-envelope fees.

- **Outline** — A self-hostable team knowledge base. Useful for storing matter templates, standard form documents, and internal procedures so your team isn't reinventing the wheel every time.

---

## Automation 1: Client Intake and Conflict Checking

Here's what this workflow looks like in practice.

**The trigger:** A prospective client fills out the intake form on your website.

**Step 1 — Categorization.** n8n sends the intake form content to Ollama, which runs a local language model to categorize the inquiry: practice area (family law, personal injury, business litigation, estate planning, etc.), urgency (statute of limitations concern, emergency filing, general inquiry), and estimated case value range. This takes seconds and gives you a structured assessment before any human looks at it.

**Step 2 — Conflict check.** n8n queries your practice management system's client database — searching for the prospective client's name, opposing party names, and any related entities mentioned in the intake form. If there's a potential conflict, the workflow flags it immediately and routes it to your managing partner for manual review. No conflict, and it proceeds.

**Step 3 — Routing.** Based on the practice area identified in Step 1, n8n routes the intake to the appropriate attorney's inbox. If it's a high-urgency matter (statute of limitations expiring within 30 days), it's flagged as priority and the attorney gets both an email and an immediate notification.

**Step 4 — Auto-response.** The prospect receives an automated acknowledgment within minutes — not days — confirming their inquiry was received, naming the attorney who will follow up, and offering a link to book a consultation directly via Cal.com. The prospect picks a time slot that works for them, and it lands on the attorney's calendar without any back-and-forth.

**Step 5 — Engagement letter.** Once the attorney decides to take the case, they trigger the engagement workflow. n8n generates a retainer agreement from your standard template, populates it with the client's information, and sends it via Documenso for e-signature. The client signs on their phone. The signed agreement is filed automatically to the matter folder.

**What you save:** The intake-to-engagement process that previously took 2–4 days of elapsed time and 30–45 minutes of staff time per client now takes minutes of human attention. Your first response to a prospect happens automatically within minutes of them submitting the form — which, based on the data, means you retain more of them.

---

## Automation 2: Document Review and Organization

This is where local AI delivers the most value — and where the privacy advantage of self-hosting matters most. Sending privileged client documents to a third-party AI API is a non-starter for most firms. Running the model on your own server eliminates that concern entirely.

**The trigger:** New documents are uploaded to a matter folder — either by your staff, by clients through a secure portal, or by n8n pulling from an email attachment.

**Step 1 — Classification.** Ollama reads each document and classifies it by type: contract, correspondence, financial record, court filing, medical record, police report, etc. This is a task that a language model does well and consistently — and far faster than a paralegal reading each document to figure out what it is.

**Step 2 — Key information extraction.** For each document, the model extracts the key metadata: dates, parties, amounts, key terms, and a one-paragraph summary. This metadata is stored alongside the document, making the entire document set searchable by content rather than just filename.

**Step 3 — Privilege flagging.** The model flags documents that may contain attorney-client privileged communications — anything involving your firm's email domain, correspondence with attorneys, or draft documents. These are separated into a privileged folder for attorney review. The model isn't making privilege determinations — it's flagging candidates so attorneys can review them efficiently.

**Step 4 — Relevance scoring.** Based on the case parameters (which you define once per matter — key dates, key parties, key issues), the model assigns a relevance score to each document. High-relevance documents are flagged for attorney priority review. Low-relevance documents are still indexed and searchable but don't clutter the priority queue.

**Step 5 — Chronological timeline.** n8n assembles a chronological timeline of all documents in the matter, sorted by date, with the summary and key parties for each entry. This gives attorneys an immediate overview of the document set — useful for case strategy, deposition preparation, and trial prep.

**What you save:** For a matter with 500 documents, the first-pass review — classification, summarization, privilege flagging, and organization — that would take a paralegal 20–30 hours is handled in under an hour of processing time. Your attorneys start with an organized, searchable, summarized document set instead of a folder full of raw files. The legal judgment — what matters, what to use, what to argue — still belongs to your attorneys. The model just gets them to the starting line faster.

---

## Automation 3: Time Tracking and Automated Billing

This automation addresses the two billing problems: lost time and invoice overhead.

**The trigger:** Attorneys track time in Kimai throughout the day — either through the web interface, a desktop widget, or a mobile app. Each time entry is tagged with the client matter and a brief description.

**Step 1 — Time entry cleanup.** At the end of each day, n8n pulls the day's time entries from Kimai and sends them to Ollama. The model reviews each entry for clarity and completeness — is the description specific enough for a client invoice? Does it reference the right matter? Are there any entries that look like duplicates? The model suggests improvements and flags anything ambiguous for the attorney to review before approving.

This step alone addresses the under-billing problem. Instead of reconstructing time entries at the end of the month from cryptic notes like "phone call" or "review docs," attorneys get a daily prompt to clean up their entries while the work is still fresh. The model doesn't add time — it helps attorneys capture time they actually worked but would have forgotten.

**Step 2 — Invoice generation.** At the end of the billing cycle (monthly for most firms), n8n pulls all approved time entries for each client matter, groups them by date and activity type, and generates a formatted invoice using your firm's template. Each line item includes the date, the activity description (cleaned up in Step 1), the time in tenths of an hour, the rate, and the total.

**Step 3 — Review and send.** Draft invoices are routed to the responsible attorney for review. The attorney can adjust line items, write off time, or add narrative descriptions for the client. Once approved, n8n sends the invoice via email — or via Documenso if you want a delivery receipt — and records the invoice in your accounting system.

**Step 4 — Follow-up.** For unpaid invoices past their due date, n8n sends automated, professional reminder emails at 15, 30, and 45 days. Each reminder is templated but can be customized per client. At 60 days, the workflow flags the matter for the managing partner to decide on further collection action.

**What you save:** The end-of-month invoice generation process that takes 8–15 hours of administrative time is reduced to 1–2 hours of attorney review. More importantly, the daily time entry cleanup typically recovers 5–10% in billable time that would otherwise be lost to vague entries and forgotten tasks. For a five-attorney firm, that's $50,000–$100,000 per year in recovered billings.

---

## Getting Started: What to Automate First

If you're reading this and thinking "this all sounds great but I don't know where to start," here's our recommendation: start with intake.

Intake is the lowest-risk automation to implement. It doesn't touch privileged documents, it doesn't change how your attorneys work, and the ROI is immediately measurable — you'll know within a month whether your response time and retention rate have improved. It's also the automation that prospective clients notice first. A firm that responds in minutes instead of days feels different from the client's perspective, and that difference shows up in your retention numbers.

Document review is the second priority if you do litigation work. The time savings are significant, and the privacy advantage of local AI means you're not creating a new risk by sending client documents to a third party. Start with a single matter — run the automated classification and organization alongside your manual process, and compare the results. Once your attorneys trust the output, you can make it the default.

Billing automation is the third priority. It's the most straightforward technically — time tracking, invoice generation, and follow-up are all well-defined processes — but it requires your attorneys to change their habits around daily time entry. That's a change management challenge more than a technical one.

---

## The Privacy Question

If you've looked at AI tools for your firm, you've probably encountered the privacy concern: most commercial AI services process your data on their servers. For a law firm, that's a serious issue. Client confidentiality, attorney-client privilege, and data security obligations make sending privileged information to a third-party AI API a risk that many firms aren't willing to take.

This is exactly why we recommend the open source, self-hosted approach. With Ollama running on your own server, the language model processes your documents locally. No data leaves your infrastructure. You control the hardware, the model, the retention. You can air-gap the server if you want to. The same confidentiality protections you already have for your client files extend naturally to the AI tools running alongside them.

This isn't a theoretical advantage. It's the difference between being able to use AI for document review and not being able to. For many firms, self-hosted AI is the only path that's ethically and practically viable.

---

## What This Costs

A self-hosted setup running n8n, Ollama, and the supporting tools typically requires:

- A server with 16–32 GB RAM and a modest GPU (or even a recent CPU — the 7B–8B models we recommend run acceptably on CPU for the workloads described here). If you already have an on-premises server, you may be able to use it. Cloud hosting runs $50–$150/month depending on specs.
- n8n, Ollama, Kimai, Cal.com, Documenso, and Outline are all free to self-host. No per-user or per-task fees.
- Setup and configuration: 20–40 hours of initial setup if you're technical, or a few days with a consultant.

Compare that to the cost of commercial legal AI tools, which typically run $50–$200 per user per month, plus document processing fees, plus the privacy risk of sending client data off-premises. For a five-attorney firm, self-hosting saves $3,000–$12,000 per year in subscription fees alone — and that's before counting the recovered billable time.

---

## The Bottom Line

Legal work requires judgment, strategy, and expertise that no software can replace. But the administrative work surrounding it — intake, document organization, time tracking, billing — is repetitive, predictable, and exactly the kind of work that automation handles well.

Every hour your attorneys spend on tasks that software could do is an hour they're not billing, not strategizing, and not serving clients. Every prospective client who waits days for a response is a client you might lose. Every time entry that's reconstructed from memory at the end of the month is billable revenue you're leaving on the table.

Open source tools let you fix these problems without creating new ones. Your data stays on your server. Your costs are predictable. Your workflows match how your firm actually works — not how a software vendor thinks it should work.

If you want help implementing any of these automations in your firm, [get in touch](/#contact). We specialize in open source, self-hosted AI solutions for small businesses — and we'll never ask you to send your client data to someone else's server.
