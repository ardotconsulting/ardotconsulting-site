---
layout: post
title: "AI Automation for Veterinary Clinics: Patient Records, Reminders, and Inventory"
date: 2027-01-24
author: "ARDOT Consulting"
tags: [veterinary, healthcare, appointments, patient-records, inventory, n8n, ollama, open-source, automation]
excerpt: "Veterinary clinics juggle patient records, appointment reminders, vaccine schedules, and medication inventory — mostly by hand. Here's how to automate the repetitive admin work with open source tools, without sending patient data to a third-party SaaS."
---

# AI Automation for Veterinary Clinics: Patient Records, Reminders, and Inventory

If you run a veterinary clinic, you already know the rhythm of a typical day. The phone rings at 8:15 with someone asking if you can squeeze in a cat with a swollen paw. Your technician is elbow-deep in a spay surgery. The front desk is trying to reconcile last week's inventory order against what actually arrived — two bottles of Metacam are missing and nobody can find them. A reminder email about next Tuesday's vaccine booster just bounced because the owner changed jobs and their old email address is dead. And somewhere in the middle of all that, you're supposed to be writing surgical notes into a patient record system that hasn't meaningfully changed since 2011.

This is what running a small veterinary practice actually looks like. The medicine is the rewarding part. The paperwork, the phone calls, the inventory spreadsheets, the "did you remember to bring a stool sample?" follow-ups — that's the part that eats your day and quietly costs you money.

A typical small animal clinic — one or two vets, two or three technicians, a couple of front desk staff — loses somewhere between $40,000 and $90,000 per year to administrative inefficiency. Missed reminders mean no-shows and gaps in the schedule. Inventory drift means expired medications and emergency reorders at a premium. Hand-written or partially-digitized records mean slower patient intake, duplicate data entry, and the occasional lost lab result. None of these are exotic problems. They're the same problems every clinic has, and they're the ones that open-source automation is uniquely well suited to solve — especially in a field where patient data privacy isn't optional.

Let's walk through the three areas where automation delivers the most value in a veterinary setting, the specific open source tools that fit, and how to put them together without sending a single patient record to a third-party cloud.

## Why Open Source Matters for Veterinary Data

Before we get into the workflows, it's worth being explicit about why this isn't just "buy a SaaS product and move on."

Veterinary clinics handle a mix of data: patient medical records, owner contact and payment information, controlled substance logs (DEA-required for anyone dispensing ketamine, tramadol, or other scheduled drugs), and business financials. Most of this is subject to state veterinary board regulations, and some clinics also handle livestock or equine work that touches USDA reporting. Sending all of that to a third-party practice management SaaS means trusting that company's security posture, their data residency, their breach notification timeline, and their pricing decisions for the next decade.

Open source tools you self-host flip that equation. Your data stays on your server (or your cloud account, which you control). You can audit the code. You can back it up however you want. And when a vendor raises prices 40% next year — because they always do — you don't have to do a panicked migration.

The tools we'll cover (n8n, Ollama, Directus, Kimai) are all mature, actively maintained, and run on a modest server you can rent for $20–40/month or keep on a small machine in your clinic's back office.

## Area 1: Patient Records and Intake

### The Problem

Most clinics still operate on a hybrid system: a practice management platform (often Covetrus, eVetPractice, or an aging on-premise install) that handles scheduling and billing, supplemented by paper intake forms, scanned lab results emailed from outside labs, and surgical notes typed into a free-text field that nobody ever goes back and structures.

The result is that finding a patient's complete history — vaccinations, past surgeries, lab trends, medication reactions — usually requires clicking through three screens and mentally stitching together a narrative. When a new technician starts, it takes them weeks to learn where everything lives. And when an owner calls asking whether their dog's last leptospirosis vaccine was the 4-way or the 2-way, the answer is buried in a free-text note from eleven months ago.

### The Automation

The goal isn't to replace your practice management system — that's a bigger conversation and often not worth the disruption. The goal is to layer automation on top of it, handling the parts that are currently manual.

**Structured intake with Directus.** [Directus](https://directus.io/) is an open source headless CMS that lets you build a custom database with a clean web interface in an afternoon. For a clinic, you can build a structured intake database that captures: owner info, patient info, presenting complaint, vital signs, and a checkbox list of common conditions. Technicians enter data on a tablet in the exam room instead of on paper. The data is structured, searchable, and exportable.

**AI-assisted record summarization with Ollama.** [Ollama](https://ollama.com/) lets you run a local language model on your own hardware — no data leaves your server. You can build a workflow that takes a patient's free-text history (pulled from your practice management system's export, or entered in Directus) and produces a one-paragraph summary: "7-year-old MC Labrador, last visit 2026-08 for annual exam, due for bordetella booster 2027-02, history of mild hip dysplasia, current on heartworm prevention (Heartgard, last dose 2027-01-15)." That summary gets attached to the patient record and displayed at the top of the chart.

**Lab result ingestion with n8n + Tesseract.** [n8n](https://n8n.io/) is an open source workflow automation tool (think Zapier, but self-hosted and far more capable). [Tesseract](https://github.com/tesseract-ocr/tesseract) is an open source OCR engine. Together: when an outside lab emails a PDF result, n8n catches the email, Tesseract extracts the text, Ollama parses out the structured fields (patient name, test type, result values, reference ranges, flags), and n8n writes a clean row into Directus and optionally pings the vet in your chat platform (more on that below).

Here's a sketch of what that workflow looks like in n8n:

```
[Email Trigger] → [Tesseract OCR node] → [Ollama node: extract fields]
  → [Directus: create record] → [Mattermost: notify doctor]
```

The vet gets a message like: *"Lab result received for Bella Johnson (Canine, 7yo). Complete blood count: all values within normal limits. Biochem: ALT 95 (ref 10–125), slightly elevated. Recommendation attached. Click to view full report."* Total time from lab email to structured record: under 60 seconds. Manual time previously: 5–10 minutes per result, plus the risk of it getting lost in an inbox.

### What This Costs

- Directus, Ollama, n8n, Tesseract: all free, open source
- Server to run them: $20–40/month (a 4-core, 8GB VPS handles all of it comfortably)
- Time to set up: one weekend, or one day if you've done it before

## Area 2: Appointment Reminders and Recall

### The Problem

The average veterinary clinic has a no-show rate of 11–18% for scheduled appointments and a recall compliance rate (patients returning for recommended follow-ups and annual exams) of 45–60%. Both numbers represent direct lost revenue and worse patient outcomes.

The standard approach to reminders is a front desk staff member manually calling or emailing the day before, when they have time, which they rarely do. Recall is even worse: most clinics generate a recall report from their PMS once a quarter, hand it to a technician who makes 40 calls in an afternoon, reaches 12 people, leaves voicemails for the rest, and never follows up again.

### The Automation

This is the single highest-ROI automation in a veterinary clinic. It's also the most straightforward to build.

**Multi-channel reminders with n8n.** Build a workflow that runs every morning at 7:00 AM, queries tomorrow's appointments (from your PMS export, a Directus mirror, or a scheduled CSV dump), and sends reminders through two channels:

1. **SMS** — via an open-source-friendly gateway. If you want fully self-hosted, [Poste.io](https://poste.io/) handles email and you can use a low-cost SMS API (Twilio is the common choice; if you want to avoid any US-centric vendor, [Plivo](https://www.plivo.com/) or [Vonage](https://www.vonage.com/) work). The reminder: *"This is a reminder for Bella's appointment tomorrow at 2:30 PM at Riverside Vet. Please bring any previous records. Reply C to confirm or R to reschedule."*
2. **Email** — via your self-hosted mail server or a transactional email service, with a richer message including pre-visit instructions (fasting requirements, what to bring, parking info).

**Recall automation with Ollama.** The recall problem is harder because it requires judgment: which patients are overdue, what's the right message for each one, and how do you prioritize? A scheduled n8n workflow can run weekly, query your patient database for overdue recalls (annual exams, vaccine boosters, dental cleanings, rechecks), and use Ollama to categorize and prioritize:

- **High priority:** overdue core vaccine (rabies, DA2PP) → immediate phone call + email
- **Medium priority:** overdue annual exam or non-core booster → email with a direct scheduling link
- **Low priority:** overdue dental cleaning → monthly email nudge

Each message includes a self-scheduling link. For self-hosted scheduling, [Cal.com](https://cal.com/) is an open source appointment booking tool that integrates cleanly with n8n and lets clients pick a time without calling the clinic.

**Confirmation handling.** When a client replies "C" to confirm, n8n catches the reply (via the SMS gateway's webhook), updates the appointment status in your system, and logs the confirmation. When they reply "R," n8n sends back a Cal.com link to reschedule. No human touches the routine cases.

### The Numbers

A clinic seeing 3,000 appointments per year with a 15% no-show rate loses roughly 450 appointments annually. At an average appointment value of $85 (exam) + $150–300 in services, that's $50,000–90,000 in lost revenue. Cutting the no-show rate from 15% to 7% with automated reminders recovers roughly half of that. The recall automation is pure incremental revenue — patients who weren't coming back at all now come back.

Total monthly cost of the automation stack: under $50. Total setup time: 2–3 days.

## Area 3: Medication and Supply Inventory

### The Problem

Veterinary inventory is genuinely difficult. You carry hundreds of SKUs — medications, surgical supplies, vaccines, consumables — many with expiration dates, many controlled, and many with usage patterns that swing based on season (heartworm prevention in spring, flea/tick in summer) or local outbreaks (parvo cluster means you burn through vaccine and IV fluids fast).

Most clinics track inventory in a spreadsheet updated manually, or in their PMS's inventory module, which is usually an afterthought feature bolted onto a billing system. The common failures:

- **Stockouts** of critical items (ketamine, certain antibiotics) that require emergency ordering at a premium or, worse, rescheduling surgeries
- **Overstock and expiration** — ordering defensively leads to expired medications, which for controlled substances means a DEA-compliant disposal process
- **Shrinkage** — the missing Metacam bottles, the boxes of syringes that walked out, the loose count on a busy Friday
- **No reorder automation** — someone has to notice you're low and place an order, and that someone is usually busy with a patient

### The Automation

**Inventory database in Directus.** Build a structured inventory table: item name, SKU, category (medication/surgical/consumable/vaccine), current quantity, reorder point, reorder quantity, unit cost, expiration date, lot number, controlled-substance flag. Technicians log dispenses and restocks through a simple tablet interface. For controlled substances, a two-person sign-off workflow mirrors what you're already doing on paper.

**Reorder automation with n8n.** A daily workflow checks the inventory table: for any item where `current_quantity <= reorder_point`, n8n generates a draft purchase order. It can email your distributor (most major veterinary distributors — MWI, Patterson, Henry Schein — accept emailed POs) or drop the draft into a shared folder for a manager to approve before sending. Either way, the cognitive load of "remembering to check inventory" disappears.

**Expiration tracking.** A weekly workflow scans for items expiring within 60 days and sends an alert: *"Alert: 3 bottles of Clavamox 250mg (lot AB1234) expire 2027-03-20. Consider returning to distributor if unopened, or prioritizing use."* This alone typically saves a clinic $2,000–5,000 per year in expired-medication write-offs.

**Usage forecasting with Ollama.** This is where it gets interesting. Feed Ollama 12–24 months of dispensing history (structured data from Directus), and ask it to produce a seasonal forecast: "Based on historical patterns, expect a 40% increase in heartworm prevention demand starting March. Recommend increasing reorder quantity for Heartgard Plus by 50% for February and March orders." You don't have to act on every recommendation, but having a forecast to sanity-check your ordering against is genuinely useful — and it's the kind of pattern recognition a busy clinic manager simply doesn't have time to do manually.

**Controlled substance logging.** For DEA compliance, every dispensing of a scheduled drug must be logged. A Directus form with a two-person sign-off (dispensing vet + witnessing technician) generates a compliant log entry automatically. Exportable as a CSV for the inevitable audit. No more hunting through paper logs.

## Putting It All Together

Here's what a fully assembled veterinary automation stack looks like:

| Function | Tool | What It Does |
|----------|------|--------------|
| Structured records | Directus | Patient/owner database, intake forms, inventory |
| Workflow engine | n8n | Reminders, recall, reorder, lab ingestion |
| Local AI | Ollama | Record summarization, recall prioritization, forecasting |
| OCR | Tesseract | Lab PDF extraction |
| Scheduling | Cal.com | Client self-scheduling, reschedule links |
| Team chat | Mattermost | Notifications to vets and technicians |
| Time tracking | Kimai | Track time per case for profitability analysis |

All of it runs on a single modest server. None of it sends patient data to a third party. All of it is open source, which means no per-seat fees, no vendor lock-in, and no surprise price hikes.

## A Realistic Implementation Plan

Don't try to build all of this at once. Start with reminders — it's the highest ROI and the simplest to build. A single n8n workflow sending SMS and email reminders can be live in a day. Once that's running and you've measured the no-show reduction, move to recall automation, then inventory, then record summarization.

A reasonable phased plan:

1. **Week 1:** Set up n8n, Directus, and Ollama on a server. Build the appointment reminder workflow. Measure no-show rate for 30 days.
2. **Week 2–3:** Build the recall automation with Cal.com scheduling links. Start with high-priority recalls only.
3. **Week 4–6:** Build the inventory database in Directus and migrate your current spreadsheet. Add the reorder and expiration workflows.
4. **Week 7–8:** Add lab result ingestion and AI record summarization. Train staff on the new intake forms.

Total elapsed time: about two months of part-time work, much of which can be done by an operations-minded technician or a consultant. Total software cost: zero. Total server cost: $20–40/month.

## The Bottom Line

Veterinary medicine is a business where the clinical work is demanding and the administrative work is relentless. Every hour your staff spends on manual reminders, inventory counts, and record transcription is an hour they're not spending with patients — and an hour of revenue that's leaking out through no-shows, expired stock, and patients who never come back for their follow-ups.

The open source tools to fix this exist today, they're mature, and they're inexpensive. The barrier isn't technology — it's finding a quiet weekend to set it up. If that's something you'd like help with, we build these systems for small practices. [Get in touch](/) and we'll walk you through what it would look like for your clinic.

*No patient data leaves your server. No per-seat fees. No vendor lock-in. Just your clinic, running the way it should.*
