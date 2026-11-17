---
layout: post
title: "Automating Proposals and Quotes: Turn Days Into Hours with Open Source Tools"
date: 2027-01-08
author: "ARDOT Consulting"
tags: [proposals, quotes, automation, n8n, ollama, odoo, invoice-ninja, open-source, workflow]
excerpt: "Stop burning days on proposals. Here's how to build an automated quote and proposal pipeline using open source tools you can self-host."
---

If your business sends proposals, you know the cycle. A potential client reaches out on Monday. By Wednesday, you've finally carved out time to write the proposal. Thursday is formatting and pricing. Friday you send it — and by then, the client has already talked to two competitors who responded faster.

Speed wins deals. But speed is hard when every proposal requires pulling pricing from a catalog, writing custom scope-of-work language, formatting a PDF, and getting someone to review it. For small businesses without a dedicated bid team, proposals eat the week.

Automation changes this. Not "AI writes your proposals while you sleep" — that produces garbage. What actually works is a pipeline where software handles the repetitive parts (data entry, formatting, pricing lookup, draft generation) and your team handles the judgment calls (reviewing, adjusting, approving). The result: proposals that used to take three days now take three hours.

Here's how to build that pipeline using open source tools you can self-host.

## The Proposal Problem

Before diving into tools, let's name what actually makes proposals slow:

1. **Intake is messy.** Clients describe what they want in emails, phone calls, or contact forms — rarely in a structured format. Someone has to read, interpret, and translate that into a scope.
2. **Pricing is scattered.** Your rates live in a spreadsheet, a catalog, or someone's head. Every proposal means manually looking up line items and calculating totals.
3. **Writing is from scratch.** Even with templates, most teams start each proposal as a blank document. The boilerplate gets retyped. The company overview gets pasted from the last proposal, with the wrong client name still in it.
4. **Approval is a bottleneck.** The proposal sits in someone's inbox waiting for review. You find out on Thursday that the pricing was wrong and start over.

Each step is individually manageable. Together, they create a multi-day drag. Automation targets each one.

## The Tool Stack

You don't need a single "proposal automation platform." You need a few open source tools that each handle one job well, connected by an automation engine.

### n8n — Workflow Orchestration

[n8n](https://n8n.io) is an open source workflow automation tool (licensed under the Sustainable Use License) that connects your apps and services. Think of it as the conductor: it receives the client inquiry, routes it to the right tools, assembles the pieces, and delivers the finished proposal. You build workflows visually — no code required, though you can add custom logic when needed.

If you've used Zapier or Make, n8n does the same thing but runs on your own server. Your data never leaves your infrastructure.

### Ollama — Local AI for Draft Generation

[Ollama](https://ollama.ai) (MIT licensed) runs large language models locally on your hardware. For proposal automation, it handles the writing-heavy parts: taking a client's unstructured request and generating a first-draft scope of work, pulling relevant case studies from your knowledge base, and personalizing boilerplate language for the specific client.

Because it runs locally, you're not sending client information to a third-party API. This matters for confidentiality, especially if you're bidding on contracts with NDAs.

### Odoo or Invoice Ninja — CRM and Pricing

Your pricing catalog and client data need a structured home. Two strong open source options:

- **Odoo Community Edition** (LGPLv3) — a full ERP with CRM, sales, and quoting modules. If you already use Odoo for operations, its built-in quotation system is the natural anchor for your proposal pipeline. You can define product templates, pricing tiers, and reusable quote lines.
- **Invoice Ninja** (licensed under their terms, self-hostable) — lighter weight, focused on invoicing and quotes. Good if you don't need a full ERP but want structured quote management with line items, discounts, and tax handling.

Either gives you a database of products, services, and rates that your automation can query programmatically.

### OpnForm — Structured Intake

[OpnForm](https://opnform.com) (AGPL-3.0) is an open source form builder you can self-host. Instead of relying on free-text emails, you create structured intake forms that capture exactly what you need: project type, budget range, timeline, scope details. The form responses feed directly into your automation workflow.

You can still accept email inquiries — n8n can parse those too — but a well-designed form front-loads the structure and saves interpretation time.

### Cal.com — Follow-Up Scheduling

[Cal.com](https://cal.com) (MIT licensed) handles the back end of the proposal cycle: scheduling the follow-up call, demo, or contract review. Your automation can include a Cal.com booking link in the proposal email so the client can immediately schedule a next step.

## Building the Pipeline: Step by Step

Let's walk through how these tools connect to form a working proposal pipeline.

### Step 1: Capture the Inquiry

Create an intake form with OpnForm (or embed one on your website). Ask for:

- Company name and contact info
- Project type (dropdown: consulting, implementation, audit, training, etc.)
- Brief description (free text)
- Budget range (dropdown)
- Timeline (dropdown: ASAP, 1-3 months, 3-6 months, exploring)
- How they heard about you

When the form is submitted, OpnForm sends a webhook to n8n. If you also want to handle email inquiries, n8n's IMAP node can poll an inbox and pass new messages into the same workflow.

### Step 2: Extract and Structure with AI

The workflow's first job is turning the client's description into structured requirements. n8n sends the form submission (or parsed email) to Ollama with a prompt like:

```
You are a proposal analyst. Read this client inquiry and extract:
1. Project type and category
2. Key deliverables (list)
3. Estimated effort level (small, medium, large)
4. Any special requirements or constraints
5. Suggested services from our catalog that match

Client inquiry: [insert inquiry text]
```

Ollama returns structured JSON. n8n parses it and stores the extracted data alongside the original submission. This takes seconds — what would take a human 15-20 minutes of reading and note-taking.

### Step 3: Generate the Pricing

Using the extracted project type and effort level, n8n queries your Odoo or Invoice Ninja instance via API. It pulls the relevant service catalog items, applies your standard rates, and calculates a price range.

For example, if the inquiry is tagged as "medium implementation project," n8n might pull:
- Discovery and scoping: $2,500
- Implementation: $8,000-$12,000
- Training: $1,500
- 30-day post-launch support: included

The pricing stays in your CRM as a draft quote, which means it's traceable and editable by your team.

### Step 4: Draft the Proposal

Now n8n calls Ollama again with a richer prompt that combines the client's original request, the extracted requirements, and the pricing data:

```
You are a proposal writer for [your company]. Write a first-draft proposal
using this structure:
1. Executive summary (2-3 paragraphs referencing the client's specific needs)
2. Scope of work (based on the extracted deliverables)
3. Investment (using the pricing data provided)
4. Timeline (based on the client's stated timeline)
5. About us (use this boilerplate: [your standard company description])
6. Next steps

Client: [company name]
Inquiry: [original text]
Extracted requirements: [structured data]
Pricing: [catalog items and rates]
```

Ollama generates a complete first draft. It won't be perfect — but it will be 80% there. The right sections, the right structure, the client's name spelled correctly, and pricing that matches your actual catalog.

### Step 5: Human Review and Approval

This is where many "AI proposal" pitches go wrong. The draft should not go to the client automatically. It should go to your team for review.

n8n creates the draft in your CRM (Odoo or Invoice Ninja) and sends a notification to the assigned salesperson or manager: "New proposal draft ready for review: [Client Name], [Project Type]." The notification can go via email, Mattermost, or any channel n8n supports.

Your reviewer opens the draft, adjusts the scope language, tweaks pricing if needed, and approves it. This takes 15-30 minutes for a straightforward proposal — compared to 3-5 hours starting from scratch.

### Step 6: Deliver to the Client

Once approved, n8n generates a PDF from the approved quote (both Odoo and Invoice Ninja can produce polished PDF quotes natively), attaches it to a personalized email, and sends it to the client. The email includes:

- The proposal PDF
- A Cal.com link to schedule a follow-up call
- A brief personalized note (drafted by Ollama, reviewed by your team)

The client gets a professional, accurate proposal within hours of their inquiry — not days.

## What This Looks Like in Practice

A marketing agency implemented a version of this pipeline. Before automation, their average proposal turnaround was four business days. After: same-day for standard projects, next-day for complex ones.

The key insight from their experience: the automation didn't replace their proposal writer. It replaced the *busywork* — the data entry, the catalog lookups, the formatting, the "start from the last proposal and hope you changed all the names" approach. Their writer now spends their time on the parts that actually win deals: tailoring the strategy section, adding relevant case studies, and crafting a compelling executive summary.

Their win rate went up, too. Not because the proposals were dramatically better written, but because they arrived faster. Clients had less time to talk to competitors.

## Common Pitfalls

**Don't skip the human review step.** It's tempting to fully automate — client submits form, AI writes proposal, system sends email. Resist this. AI-generated proposals that haven't been reviewed will eventually contain an embarrassing error: a wrong client name, a pricing mismatch, a scope that doesn't make sense. One bad proposal costs you more than the time you saved on ten good ones.

**Keep your catalog clean.** The automation is only as good as the data it pulls from. If your Odoo catalog has outdated prices or services you no longer offer, your proposals will reflect that. Assign someone to review the catalog monthly.

**Start with one project type.** Don't try to automate every kind of proposal on day one. Pick your most common project type — the one where you send the most proposals and where the scope is most predictable. Build the pipeline for that. Once it's working, expand to other types.

**Use good intake forms.** The more structure you capture upfront, the less AI has to guess. A well-designed OpnForm with dropdowns and guided fields produces far better automation results than parsing a rambling email.

## What It Costs

All the tools in this stack are free to self-host:

- **n8n**: Free self-hosted (Sustainable Use License). Their cloud option starts at $20/month if you don't want to host it.
- **Ollama**: Free (MIT). Runs on any machine with enough RAM — 8GB minimum for smaller models, 16GB+ for better quality.
- **Odoo Community**: Free self-hosted (LGPLv3). The CRM and sales modules are included.
- **Invoice Ninja**: Free self-hosted. Cloud plans start at $30/year if you prefer managed.
- **OpnForm**: Free self-hosted (AGPL-3.0). Cloud plans from $19/month.
- **Cal.com**: Free self-hosted (MIT). Cloud plans from $12/month.

The real cost is setup time — expect a weekend to get the workflow built and tested, plus a week of tweaking once you run real proposals through it. If you'd rather not build it yourself, that's where we come in.

## Getting Started

You don't need to build the whole pipeline at once. Start here:

1. **Install n8n** on a server (a $10/month VPS is plenty). Docker is the easiest method.
2. **Create one intake form** with OpnForm for your most common project type.
3. **Build a simple n8n workflow** that takes form submissions and creates a draft quote in Odoo or Invoice Ninja.
4. **Add Ollama** for draft generation once the basic data flow is working.
5. **Run five real proposals** through the pipeline and note what needs adjusting.
6. **Expand** to additional project types and add the Cal.com follow-up scheduling.

The first proposal that goes out the same day the inquiry comes in is the moment you'll see the value. Not because the AI wrote something brilliant — but because your team spent 30 minutes reviewing instead of 4 hours writing, and the client got their answer before they started looking elsewhere.

---

*Want help building an automated proposal pipeline for your business? ARDOT Consulting designs and implements open source automation systems tailored to your workflow. [Get in touch](/#contact) — we'll map your proposal process and show you exactly where automation saves time.*