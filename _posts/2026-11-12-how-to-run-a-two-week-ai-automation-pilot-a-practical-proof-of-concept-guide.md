---
layout: post
title: "How to Run a Two-Week AI Automation Pilot: A Practical Proof-of-Concept Guide"
date: 2026-11-12
author: "ARDOT Consulting"
tags: [ai-automation, pilot, proof-of-concept, poc, strategy, implementation, n8n, ollama, open-source]
excerpt: "Before you commit to automating a process, run a pilot. Here's a concrete two-week framework for testing AI automation on a single workflow — what to build, what to measure, and how to decide whether to scale up."
---

# How to Run a Two-Week AI Automation Pilot: A Practical Proof-of-Concept Guide

You've read the blog posts. You've audited your processes. You've identified three or four workflows that look like good automation candidates. Now what?

Most business owners do one of two things at this point. They either stall — reading more articles, attending more webinars, waiting for someone else in their industry to go first — or they overcommit, signing a year-long contract with a platform they haven't actually tested against their real data.

There's a middle path: a structured, two-week pilot. You pick one workflow, build a working prototype using open-source tools, run it against real (or realistic) data, measure the results, and make a go/no-go decision based on evidence instead of vendor demos.

This post is the playbook for that pilot. No theory — just the steps, the timeline, and the decision criteria.

---

## Why Two Weeks?

A pilot that's too short doesn't produce meaningful results. A pilot that's too long loses momentum, turns into a project, and accumulates scope creep. Two weeks is the sweet spot: long enough to build something real, run it for several days, and collect data — short enough to keep everyone focused.

Here's what two weeks gives you:

- **Days 1–3:** Scope, setup, and build the core automation
- **Days 4–6:** Connect data sources, handle edge cases, test with real inputs
- **Days 7–10:** Run the automation live alongside your manual process
- **Days 11–12:** Collect metrics, gather feedback, write up findings
- **Day 13–14:** Decision meeting — scale, iterate, or shelve

You're not building production software. You're building a proof-of-concept that answers one question: *does automating this workflow actually save time and produce acceptable results?*

---

## Week 1: Build

### Day 1: Pick the Right Workflow

You already have a shortlist. Now pick one. The ideal pilot workflow has these characteristics:

- **High volume** — it happens frequently enough that you'll see meaningful time savings in a week
- **Low complexity** — it involves moving data between 2–3 systems, not 10
- **Tolerant of imperfection** — if the automation makes a mistake, a human catches it before anything bad happens
- **Measurable** — you can quantify how long the manual version takes

Good pilot candidates: invoice data entry, email triage and routing, document extraction and filing, lead enrichment from web forms, appointment reminder generation.

Bad pilot candidates: anything involving payment authorization, legal document generation, customer-facing communication without review, or workflows that require integration with a system you can't easily access.

Write down the current process in 5–10 steps. Time yourself or a team member doing it manually. That's your baseline.

### Day 2: Set Up Your Tools

For the pilot, you need three things:

1. **An automation engine** — [n8n](https://n8n.io) is the practical choice. It's open-source, visual, and connects to most business tools. Self-host it on a small VPS ($10–20/month) or run it locally on a spare machine for the pilot.

2. **An AI model for any text/intelligence work** — [Ollama](https://ollama.ai) running locally gives you a private LLM (try Llama 3 or Qwen) without sending data to a third-party API. For document extraction, pair it with [Tesseract](https://tesseract.project) for OCR.

3. **Access to your data** — export a sample of real documents, emails, or records. 50–100 items is enough for a pilot. If your data is sensitive, anonymize names and account numbers before using them.

Get these running on Day 2. Don't spend more than a day on setup. If n8n takes longer than an afternoon to install, you're overcomplicating it — use the Docker one-liner and move on.

### Day 3: Build the Core Automation

This is where you build the happy path — the automation that works when everything goes right.

In n8n, this means creating a workflow with these stages:

- **Trigger:** How does the automation start? A new email arrives? A file lands in a folder? A form is submitted? Use a webhook, an IMAP node, or a file watcher.
- **Process:** What happens to the data? This is where AI comes in — extracting key information from an email, classifying a document, summarizing a record, or pulling structured data from unstructured text.
- **Output:** Where does the result go? Into a spreadsheet, a database (NocoDB works well), a notification in Mattermost, or a draft email for human review.

Keep it simple. The goal is a workflow that takes an input, does something useful with it, and produces an output you can evaluate. Resist the urge to handle every edge case on Day 3 — you'll do that tomorrow.

### Days 4–5: Handle Real Data and Edge Cases

Now feed your automation the 50–100 real samples you prepared. Watch what breaks.

Things that commonly go wrong:

- **Format variation** — invoices from different vendors have different layouts. Your extraction works on Vendor A but fails on Vendor B.
- **Missing fields** — some records don't have the data your automation expects (no phone number, no due date, no line items).
- **Ambiguity** — the AI extracts a value but you're not sure it's correct. An email mentions "the Johnson account" — which Johnson account?
- **Encoding issues** — PDFs with scanned images vs. text-based PDFs. CSV files with weird character encoding.

For each failure, decide: fix it now, or note it as a known limitation? In a pilot, you're not trying to achieve 100% accuracy. You're trying to understand what accuracy is achievable and what the failure modes look like. A workflow that handles 80% of cases correctly and flags the other 20% for human review is a perfectly good pilot result.

### Day 6: Add the Safety Net

Before you go live, build the review step. The automation should not silently make decisions. It should produce a draft, a recommendation, or a flag — and a human should approve the final action.

In practice, this usually means the automation writes its output to a shared spreadsheet or a NocoDB table with a "Status" column. A team member reviews each row, approves or rejects it, and only approved items proceed.

This is not a temporary hack. Human-in-the-loop is the correct architecture for most business automation. The pilot is testing whether the AI's drafts are good enough that reviewing them is faster than doing the work from scratch.

---

## Week 2: Run and Measure

### Days 7–10: Run It Live

This is the most important part of the pilot. Run the automation alongside your existing manual process for four full working days.

Here's what that looks like:

1. Every morning, the automation processes the day's inputs and produces its drafts/outputs in the review queue.
2. A team member reviews the automation's output, approves or corrects it, and records how long the review took.
3. The same team member also does a few items manually — the old way — and records how long that took.

You're collecting two parallel datasets: time-to-complete with automation + review, and time-to-complete manually. By the end of Day 10, you'll have enough data points to compare.

Also track: how many items the automation got right on the first try (no correction needed), how many needed minor corrections, and how many needed a full redo. This tells you the quality of the AI output, not just the speed.

### Day 11: Collect Feedback

Sit down with the person who's been reviewing the automation's output. Ask them:

- Did reviewing the automation's work feel faster than doing it yourself?
- What kinds of mistakes did the automation make? Were they predictable?
- Did you trust the automation's output, or did you feel the need to double-check everything?
- What would make the automation more useful?

Be honest about the feedback. If your team member says "it was faster to just do it manually," that's a valid pilot result. It means either the workflow wasn't a good automation candidate, or the automation needs more work before it's useful. Both are useful findings.

### Day 12: Write Up the Findings

Create a one-page summary with these sections:

**Workflow:** What you automated (e.g., "Invoice data entry from email attachments into accounting system")

**Baseline:** Average time per item manually (e.g., "4.5 minutes per invoice")

**Pilot result:** Average time per item with automation + review (e.g., "1.8 minutes per invoice")

**Accuracy:** Percentage of items that needed no correction, minor correction, or full redo (e.g., "65% correct, 25% minor fixes, 10% redone")

**Volume:** Number of items processed during the pilot (e.g., "87 invoices over 4 days")

**Estimated annual savings:** (Manual time − automated time) × daily volume × 250 working days. Be conservative. Round down.

**Failure modes:** The 2–3 most common things that went wrong.

**Team feedback:** One or two sentences from the person who reviewed the output.

This one-pager is the deliverable. It's what you'll use to make a decision.

---

## The Decision: Scale, Iterate, or Shelve

### Scale Up

**If the pilot shows meaningful time savings (30%+) and acceptable accuracy (80%+ correct with minor fixes),** the answer is likely to scale up. Scaling means:

- Moving from a pilot VPS to a proper server with backups
- Hardening the workflow (better error handling, logging, monitoring)
- Removing the parallel manual process and trusting the automation + review loop
- Identifying the next workflow to automate

Before scaling, estimate the production cost: server hosting ($20–50/month for a small business), occasional maintenance time (2–4 hours/month), and the one-time cost of hardening the workflow (a few days of development work). Compare this to the annual savings from your one-pager.

### Iterate

**If the pilot shows promise but the accuracy isn't there yet (60–80% correct),** the answer is to iterate. Common improvements:

- **Better prompts** — if you're using an LLM for extraction or classification, refining the prompt often improves accuracy dramatically. Be specific about the format you want, include examples, and tell the model what to do when it's uncertain.
- **Better OCR** — if document extraction is the bottleneck, try a different OCR engine or preprocess images (deskew, increase contrast) before extraction.
- **Narrower scope** — maybe the automation works well for 70% of your documents (the ones from regular vendors) and struggles with the rest. Automate the 70%, handle the rest manually. That's still a win.
- **Two-stage review** — have the AI flag low-confidence items for human review and auto-approve high-confidence ones. This reduces review time while maintaining accuracy.

Set a clear timeline for iteration — another two weeks, then re-evaluate. Don't let iteration become an open-ended project.

### Shelve

**If the pilot shows minimal time savings (under 20%) or unacceptable accuracy (under 60%),** the honest answer is to shelve it. This is not a failure. It's a successful pilot that saved you from committing to a bad automation project.

Common reasons pilots don't pan out:

- **The workflow is more complex than it appeared** — it involves judgment calls that are hard to encode
- **The data is too inconsistent** — every vendor, every document, every record is structured differently
- **The volume doesn't justify the effort** — automating something that happens 5 times a week saves minutes, not hours
- **The integration is too fragile** — the system you need to connect to doesn't have a stable API or export function

Shelving a pilot means you've learned something specific about your business: this workflow, at this volume, with these tools, isn't worth automating right now. File the findings. Revisit in a year if conditions change.

---

## What a Real Pilot Looks Like: An Example

A 12-person accounting firm wanted to automate invoice processing. Their manual process: a staff accountant opens each invoice PDF from email, types the vendor name, invoice number, date, and line items into their accounting system, then files the PDF. About 4 minutes per invoice, 40–60 invoices per day.

**Pilot setup:** n8n workflow triggered by email attachment. Tesseract + Ollama extract vendor name, invoice number, date, and total from the PDF. Output goes to a NocoDB table for review. Approved items get pushed to the accounting system via CSV export (API integration deferred to production).

**Week 1:** Built the workflow. Discovered that scanned PDFs needed image preprocessing before OCR would work. Discovered that invoice number formats vary wildly. Added a fallback: if OCR confidence was low, the item was flagged for manual entry instead of auto-extraction.

**Week 2:** Ran it for 4 days alongside the manual process. Results:

| Metric | Manual | Automated + Review |
|--------|--------|-------------------|
| Time per invoice | 4.2 min | 1.5 min |
| Daily time (50 invoices) | 3.5 hrs | 1.25 hrs |
| First-try accuracy | — | 72% |
| After minor corrections | — | 91% |
| Full redo needed | — | 9% |

**Decision:** Scale up. The 64% time reduction justified the investment in hardening the workflow and building a proper API integration. The 9% full-redo rate was acceptable — those were mostly illegible scanned invoices that would have been slow manually too.

**What they learned that they didn't expect:** The review step caught two invoices that had been manually entered incorrectly the week before (wrong vendor — two vendors with similar names). The AI flagged the mismatch. The human review step wasn't just a safety net — it was an improvement over the manual process.

---

## Common Pilot Mistakes

**Picking a workflow that's too complex.** If your first pilot involves integrating five systems and handling 12 document types, you'll spend two weeks on setup and never get to evaluation. Start with the simplest workflow on your shortlist.

**Skipping the manual baseline.** If you don't know how long the manual process takes, you can't measure improvement. "It feels faster" is not a pilot result.

**Building without a review step.** Fully autonomous automation is rarely appropriate for business workflows in a pilot. You need the review step both as a safety net and as a measurement tool — reviewing the AI's work is how you assess quality.

**Not using real data.** Testing with synthetic data hides the messiness of real-world inputs. Your pilot needs to choke on a badly-scanned invoice or an email with a weird format. That's the point.

**Treating the pilot as a commitment.** A pilot is an experiment. If you go into it assuming you'll deploy the result, you'll rationalize away bad findings. Be willing to shelve.

---

## The Tools, Summarized

| Tool | Role | Cost |
|------|------|------|
| n8n | Automation engine — connects systems, runs workflows | Free (self-hosted) |
| Ollama | Local AI model for extraction, classification, summarization | Free (self-hosted) |
| Tesseract | OCR for scanned documents and PDFs | Free (open source) |
| NocoDB | Review queue / database for pilot outputs | Free (self-hosted) |
| Small VPS | Hosting for the pilot | $10–20/month |

Total pilot cost: a VPS subscription and 10–14 days of focused effort. No software licenses. No per-seat fees. No vendor lock-in.

---

## What Comes After the Pilot

If the pilot succeeds, the next steps are:

1. **Harden the workflow** — add error handling, logging, and monitoring. Use Uptime Kuma to alert you if the automation stops running.
2. **Set up backups** — if the automation is processing business data, the data it touches needs to be backed up. (We covered this in our [disaster recovery guide](/blog/2026/11/17/backing-up-your-self-hosted-stack-a-practical-disaster-recovery-guide/).)
3. **Document it** — write down how the workflow works, where it fails, and who handles what. Future-you will thank present-you.
4. **Pick the next pilot** — take the second workflow from your original shortlist and run the same two-week process. Automation compounds: each successful workflow frees up time for the next one.

If the pilot fails, the next steps are:

1. **File the findings** — the one-pager is valuable. It tells you what didn't work and why.
2. **Pick a different workflow** — the failure was specific to that workflow, not to automation in general. Try a simpler one.
3. **Revisit in 6–12 months** — tools improve, data changes, volumes shift. What doesn't justify automation today might justify it next year.

---

## The Bottom Line

The biggest risk in AI automation isn't that you'll build something that doesn't work. It's that you'll either never start — paralyzed by the gap between "interested" and "committed" — or that you'll overcommit before you have evidence.

A two-week pilot closes that gap. It costs almost nothing, produces real data, and gives you a clear decision: this worked, this needs work, or this isn't worth it. All three are good outcomes.

The only bad outcome is not running the pilot at all.

---

*Want help scoping and running an AI automation pilot for your business? [Get in touch](/#contact) — we design and build proof-of-concept workflows with open-source tools, and we'll tell you honestly whether automation makes sense for your specific processes.*
