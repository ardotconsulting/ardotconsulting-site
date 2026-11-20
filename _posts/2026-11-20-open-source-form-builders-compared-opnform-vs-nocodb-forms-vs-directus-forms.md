---
layout: post
title: "Open Source Form Builders Compared: OpnForm vs NocoDB Forms vs Directus Forms"
date: 2026-11-20
author: "ARDOT Consulting"
tags: [opnform, nocodb, directus, forms, open-source, self-hosting, comparison, no-code, typeform-alternative]
excerpt: "Every business needs forms — contact forms, intake questionnaires, lead captures, feedback surveys. Three open source tools handle them differently. Here's an honest comparison of OpnForm, NocoDB Forms, and Directus, and which one fits your situation."
---

# Open Source Form Builders Compared: OpnForm vs NocoDB Forms vs Directus Forms

Every business collects information through forms. A contact form on your website. A client intake questionnaire. A lead capture page for a campaign. A vendor registration form. An internal equipment request. An event RSVP. A customer feedback survey.

The default move for most small businesses is to reach for a hosted form tool — Typeform, Jotform, Formstack — and pay $25 to $99 per month for the privilege of storing your respondents' data on someone else's servers, with per-response limits and feature gates that push you into higher tiers the moment your forms get useful.

We've covered the self-hosted alternative before: OpnForm is an excellent direct Typeform replacement. But it's not the only option, and depending on what else you're running, one of two other open source tools — NocoDB or Directus — might be the better fit. All three can collect form submissions on your own infrastructure. They just approach the problem from different angles.

This post compares them honestly so you can pick the one that matches your situation — not the one that's "best" in the abstract.

---

## The Three Approaches, In Plain Terms

Before we get into features, it helps to understand what each tool actually is, because that determines everything else.

**OpnForm is a form builder.** That's its entire job. You open a visual editor, drag fields onto a canvas, configure conditional logic and notifications, publish, and embed the form on your website or share a link. Submissions land in OpnForm's dashboard and can be sent to Slack, Discord, email, or a webhook. It is the closest drop-in replacement for Typeform. It does not try to be a database, a CRM, or an app builder — it collects form responses and gets out of the way.

**NocoDB is a no-code database with a form view.** It's an open source Airtable alternative: it connects to a real SQL database (Postgres, MySQL, SQLite) and presents it as a friendly spreadsheet-like interface with views — grid, Kanban, gallery, calendar, and **form**. The form view turns any table into a submission form. When someone fills it out, a new row is created in that table. This means your form submissions live alongside all your other business data — not in a separate forms tool. NocoDB's form is a feature of the database, not a standalone product.

**Directus is a data platform with form-like data entry and API submission.** Directus wraps any SQL database with instant REST/GraphQL APIs, a visual admin app (the Data Studio), and an automation engine (Flows). It doesn't ship a Typeform-style public form builder. Instead, you get two form-like capabilities: the admin app itself is a form-driven interface for creating and editing records (useful for internal forms like equipment requests or PTO), and Directus's public API endpoints let you build a custom external form — on your website, in n8n, or anywhere — that writes directly to your database. Flows then handle notifications, validation, and downstream automation the moment a submission arrives.

So the real question isn't "which form builder is best?" It's: **where do you want your form data to live, and what else is happening around it?**

---

## Feature Comparison

| Feature | OpnForm | NocoDB Forms | Directus |
|---------|---------|--------------|----------|
| Primary purpose | Form builder | No-code database (form is a view) | Data platform + APIs (form entry via admin/API) |
| Visual form designer | ✅ Drag-and-drop | ✅ Per-table form view config | ⚠️ Admin app forms (not a public form designer) |
| Embed on external website | ✅ iframe / link | ✅ Shared form link | ⚠️ Build your own via API |
| Conditional logic / field rules | ✅ | ✅ Show/hide fields | ✅ Via Flows + field validation |
| File uploads | ✅ | ✅ (attachment fields) | ✅ (file fields) |
| Email notifications on submit | ✅ | ✅ | ✅ (via Flows) |
| Webhooks | ✅ | ✅ (webhook automations) | ✅ (Flows webhook operation) |
| Slack / Discord integration | ✅ Native | Via webhook | Via Flows |
| Submissions stored in | OpnForm's own DB | Your SQL database table | Your SQL database collection |
| Submissions sit alongside other business data | ❌ Separate | ✅ Same workspace | ✅ Same workspace |
| API access to submissions | ✅ | ✅ (auto REST API) | ✅ (REST + GraphQL) |
| Built-in automation on submit | ⚠️ Webhook out | ✅ (automations) | ✅ (Flows — powerful) |
| User roles / access control on responses | Basic (workspace) | ✅ Per-table | ✅ Granular, per-collection |
| Public / anonymous submission | ✅ | ✅ | ⚠️ Requires public API config |
| Captcha | ✅ | ❌ (as of writing) | ⚠️ Add via custom form |
| GitHub stars | ~3,800 | ~65,600 | ~30,000 |
| License | AGPL v3 | AGPL v3 | BSL → Apache (source-available) |
| Self-host cost | ~$5/mo VPS | ~$5/mo VPS | ~$5/mo VPS |

---

## When To Pick OpnForm

OpnForm is the right choice when **forms are the job, and you don't need the submissions tied into a larger database right now.**

Use OpnForm if:

- You want a direct Typeform replacement — embeddable forms on a public website, shared links, conditional logic, file uploads, the works.
- Your main need is collecting contact form submissions, event registrations, job applications, or simple surveys, and getting notified (email/Slack/Discord) when they arrive.
- You don't want to think about database tables, relationships, or APIs. You want to build a form in 10 minutes and move on.
- You might pipe submissions into another tool later via webhook — but for now, "notify me when someone submits" is enough.

OpnForm is the simplest of the three to set up for a pure forms use case. If you've ever used Typeform, the interface will feel familiar. The trade-off is that submissions live in OpnForm's own database, separate from the rest of your business data. You can export them or send them out via webhook, but there's no built-in "this form writes directly into my CRM table" story unless you wire that up yourself.

**Real example:** A small law firm wants a client intake form on their website — name, case type, brief description, document upload. They need email notification and a weekly digest of new submissions. OpnForm handles this in an afternoon, no database knowledge required.

---

## When To Pick NocoDB Forms

NocoDB Forms is the right choice when **your form submissions are part of a larger dataset you're already managing in NocoDB.**

Use NocoDB Forms if:

- You're already using (or planning to use) NocoDB as your team's no-code database — for tracking projects, customers, inventory, or anything else.
- You want form submissions to appear as rows in a table that sits next to your other tables, with relationships between them. A "New Lead" form creates a row in the Leads table, which links to the Companies table and the Campaigns table.
- You want non-technical staff to view, filter, and manage submissions in the same spreadsheet-like interface they use for everything else — not in a separate forms dashboard.
- You need built-in automations: when a form is submitted, update a related record, send a notification, or trigger a downstream process.

NocoDB's form view is less polished than OpnForm's dedicated designer — there are fewer layout customization options, and the form is generated from your table's fields rather than designed from a blank canvas. But that's the point: the form is a window into your database, not a standalone artifact. The submission doesn't need to be exported or synced — it's already where it belongs.

**Real example:** A property management company tracks tenants, units, and maintenance requests in NocoDB. They create a form view on the Maintenance Requests table and share the link with tenants. When a tenant submits "kitchen sink leaking," a row appears in the table, a webhook fires to n8n, and a work order is created and assigned. No data sync, no export step — it's one system.

---

## When To Pick Directus

Directus is the right choice when **forms are just the front door to a larger application or automation pipeline**, and you're comfortable (or working with someone comfortable) doing a little configuration.

Use Directus if:

- You're building a custom internal tool or customer portal on top of Directus — forms are one input method among several (admin app, API, n8n workflow, mobile app).
- You need granular access control: different teams see and edit different subsets of submissions; public users can submit but not view; managers can approve.
- You want powerful automation triggered by submissions — Directus Flows can run multi-step logic (validate, enrich with AI, create related records, send conditional notifications, call external APIs) the moment a form is submitted.
- You want your form data accessible via a clean REST or GraphQL API from day one, for integration with other systems.
- You're okay building the public-facing form yourself (on your website, or via a simple HTML form posting to a Directus endpoint) rather than using a visual designer — or using Directus's admin app for internal forms where a polished public page isn't needed.

Directus doesn't give you a Typeform-style embed. What it gives you is a **database-backed, API-first, automation-ready foundation** that forms plug into. For internal forms — equipment requests, PTO requests, internal change orders — the admin app's generated forms are perfectly good and require zero design work. For external public forms, you (or a developer) build the form and point it at a Directus endpoint; Flows handle the rest.

**Real example:** A distribution company runs its entire product catalog, orders, and customer database on Directus. A wholesale ordering form on their website posts to a public Directus endpoint. A Flow validates the order, checks inventory, applies the customer's pricing tier, creates the order record, and notifies the fulfillment team — all automatically. The "form" is a small piece of a much larger system.

---

## A Quick Decision Guide

Still unsure? Run through this:

1. **"I just need forms on my website, fast, with notifications."** → OpnForm. It's the most direct path.
2. **"I want form submissions to be rows in my team's database, alongside my other data."** → NocoDB Forms.
3. **"Forms are one input into a larger app or automated workflow with complex logic and access control."** → Directus.

None of these is the wrong choice. The wrong choice is paying Typeform $99/month to hold your data hostage because you didn't know there were three solid open source alternatives — each tuned to a different situation.

---

## Can You Use More Than One?

Yes, and many businesses do. A common stack:

- **OpnForm** for public-facing marketing forms (contact, lead capture, event RSVP) where speed and polish matter.
- **NocoDB** for team data management where form views let external people (clients, tenants, vendors) submit into a shared database.
- **Directus** for the core business application where forms are just one of several input methods and automation is the real value.

All three are self-hosted, so there's no per-submission cost regardless of how many forms you run or how many responses you collect. The only cost is the VPS they live on — typically a single $5–$20/month server handles all of them comfortably for a small business.

---

## Tool Stack Summary

| Tool | Role | License | Best For |
|------|------|---------|----------|
| [OpnForm](https://opnform.com) | Dedicated form builder | AGPL v3 | Public forms, fast deployment, Typeform replacement |
| [NocoDB](https://nocodb.com) | No-code database with form views | AGPL v3 | Submissions as rows in a shared business database |
| [Directus](https://directus.io) | Data platform + APIs + Flows | BSL → Apache | Forms as input to larger apps and automation pipelines |
| [n8n](https://n8n.io) | Workflow automation (connects to all three) | Sustainable Use | Routing submissions, notifications, downstream logic |
| [Ollama](https://ollama.ai) | Local AI model runner | MIT | Enriching submissions (summarize, classify, extract) |

All self-hostable. No per-seat fees. No per-submission fees. Your data stays on your infrastructure.

---

## Ready to Stop Paying Per Form Submission?

If you're tired of form SaaS pricing and want to move your forms — and the data they collect — onto infrastructure you control, we can help. We'll assess which of these three tools fits your business, set it up, connect it to your existing systems, and train your team to manage it.

[Get in touch](/#contact) and tell us what forms you're currently running and what they cost you. We'll show you the self-hosted alternative.
