---
layout: post
title: "Open Source Form Builders Compared: OpnForm vs NocoDB Forms vs Directus Forms"
date: 2026-11-20
author: "ARDOT Consulting"
tags: [opnform, nocodb, directus, forms, comparison, open-source, self-hosting, no-code]
excerpt: "Three self-hostable form builders, three different philosophies. Here's an honest comparison of OpnForm, NocoDB Forms, and Directus Forms for businesses that want to collect data without per-response pricing."
---

Every business collects data through forms. Customer feedback, job applications, event registrations, support tickets, lead capture, internal requests. The tools you use to build those forms determine how much you pay, where your data lives, and how easily you can connect submissions to the rest of your workflow.

Typeform charges $25/month for 100 responses. SurveyMonkey caps responses on lower tiers. Jotform locks file upload size behind higher plans. Every SaaS form builder eventually hits the same wall: you outgrow the limits, and the next tier doubles your cost.

If you're already self-hosting parts of your stack, you have three solid options for forms that don't charge per response. But they approach the problem from very different angles. Here's how OpnForm, NocoDB Forms, and Directus Forms compare.

## The Three Contenders

**OpnForm** is a dedicated form builder. It does one thing: create forms and collect submissions. Think of it as the Typeform replacement. It's built on Laravel and Vue, licensed under AGPLv3 (a genuine open source license), and has over 4,000 stars on GitHub.

**NocoDB** is a no-code database that happens to include form views. It's an Airtable alternative first, form builder second. You create a table, define columns, then generate a public form that writes directly into that table. It's licensed under the Sustainable Use License, which is source-available but not OSI-approved open source.

**Directus** is a headless CMS and backend platform that can build forms through its data collections and flow automations. It wraps any SQL database with an admin panel, REST/GraphQL APIs, and automation rules. Like NocoDB, it uses a source-available license (the Monospace Sustainable Core License). It's the most powerful of the three, but also the most complex.

## License Comparison: Open Source vs Source-Available

Before comparing features, it's worth understanding the license distinction because it matters for compliance-conscious businesses.

| Tool | License | OSI-Approved | Can Self-Host Free | Can Modify Source |
|------|---------|-------------|-------------------|-------------------|
| OpnForm | AGPLv3 | Yes | Yes | Yes |
| NocoDB | Sustainable Use License | No | Yes (internal use) | Yes (internal use) |
| Directus | MSCL 1.0 | No | Yes (internal use) | Yes (internal use) |

OpnForm's AGPLv3 license is the most permissive for self-hosting in the traditional open source sense. You can modify it, distribute it, and even offer it as a service to others, as long as you share your modifications under the same license.

NocoDB and Directus use source-available licenses that allow free self-hosting for internal business use. The main restriction is that you can't turn around and offer the software itself as a hosted product that competes with their cloud offerings. For most small businesses self-hosting internally, this distinction doesn't matter in practice. But if you're in a regulated industry with strict procurement requirements around OSI-approved licenses, it's a factor.

## Feature Comparison

| Feature | OpnForm | NocoDB Forms | Directus Forms |
|---------|---------|-------------|----------------|
| Drag-and-drop builder | Yes | Yes (form view) | Yes (layout builder) |
| Unlimited submissions | Yes | Yes | Yes |
| Conditional logic | Yes | Limited | Yes (via flows) |
| File uploads | Yes | Yes (attachment field) | Yes (file field) |
| Email notifications | Yes | Yes (webhook + automation) | Yes (flow + email) |
| Webhooks | Yes | Yes | Yes |
| Stripe payments | Yes | No | Yes (via flow) |
| Form analytics | Yes | No | No (use Plausible) |
| Custom branding | Paid tier | Yes | Yes |
| Embed anywhere | Yes | Yes (iframe) | Yes (iframe/API) |
| Public API | Yes | Yes (REST + GraphQL) | Yes (REST + GraphQL) |
| Multi-page forms | Yes | No | Yes |
| AI form generation | Yes (MCP server) | No | No |
| Database backend | MySQL/PostgreSQL | MySQL/PostgreSQL/SQLite | Any SQL database |
| Docker deployment | Yes | Yes | Yes |

## OpnForm: The Dedicated Form Builder

OpnForm is the most straightforward of the three. You install it, you build forms, you collect submissions. There's no database to design, no collections to configure, no API endpoints to wire up before you can start collecting data.

### What It Does Well

The form builder itself is polished. You get a visual editor with drag-and-drop fields, conditional logic, custom themes, and multi-page layouts. It supports both classic and conversational (Typeform-style) form designs. Submissions land in a dashboard where you can view, export, and route them.

OpnForm also has a few features the others lack:

- **Built-in form analytics** so you can see completion rates and drop-off points without wiring up a separate analytics tool
- **Stripe payment integration** directly in the form, so you can charge for event registrations, deposits, or paid submissions
- **An MCP server** that lets AI agents create and manage forms programmatically, which is useful if you're building automated workflows that generate forms dynamically

### Where It Falls Short

OpnForm is a form builder, not a database. Submissions are stored in its own database, and you access them through OpnForm's dashboard or API. If you want submissions to flow into a CRM, a project tracker, or a custom database, you'll need to set up webhooks or use n8n to route the data.

Custom branding (removing the OpnForm logo from forms) requires a paid plan even when self-hosting. The free self-hosted tier includes OpnForm branding.

### Self-Hosting OpnForm

```yaml
# docker-compose.yml (simplified)
version: "3.8"
services:
  opnform:
    image: jhumanj/opnform-api:latest
    ports:
      - "8080:80"
    environment:
      - APP_URL=https://forms.yourdomain.com
      - DB_HOST=db
      - DB_DATABASE=opnform
      - DB_USERNAME=opnform
      - DB_PASSWORD=your-password
    depends_on:
      - db
  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=opnform
      - POSTGRES_USER=opnform
      - POSTGRES_PASSWORD=your-password
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
```

OpnForm requires PHP, PostgreSQL or MySQL, and Redis for queues. The Docker setup is straightforward but heavier than a single-container deployment.

## NocoDB Forms: The Database-First Approach

NocoDB flips the form builder concept. Instead of starting with a form, you start with a database table. You define columns (text, number, date, select, attachment), set up views (grid, Kanban, calendar, form), and then share the form view publicly.

### What It Does Well

The strength of this approach is that your form submissions land directly in a structured database that you control. No webhooks needed, no data routing. The form is a view of the table, and the table is where the data lives.

NocoDB also gives you:

- **Multiple view types** for the same data. A customer feedback table can have a form view for public submissions, a grid view for internal review, and a Kanban view for tracking status.
- **REST and GraphQL APIs** automatically generated for every table, so other tools can read and write to the same data.
- **A spreadsheet-like interface** that non-technical team members can use to manage submissions without learning a database tool.

### Where It Falls Short

NocoDB's form views are basic compared to a dedicated form builder. There's no multi-page form support, limited conditional logic (showing/hiding fields based on previous answers), and no built-in form analytics. The form design options are minimal compared to OpnForm's themed, branded layouts.

If you need payment collection through the form, NocoDB doesn't have native Stripe integration. You'd need to build that with webhooks and n8n or a custom script.

### Self-Hosting NocoDB

```bash
# Simplest possible setup: Docker with SQLite
docker run -d \
  --name noco \
  -v "$(pwd)/nocodb:/usr/app/data/" \
  -p 8080:8080 \
  nocodb/nocodb:latest
```

NocoDB is the easiest to deploy of the three. A single Docker container with SQLite gets you a working instance in under a minute. For production, use PostgreSQL as the metadata database.

## Directus Forms: The Backend Powerhouse

Directus is the most flexible and the most complex. It's a headless CMS that wraps any SQL database with an admin panel, APIs, and automation flows. Forms in Directus are built by creating a collection (table), defining fields, and then either using the admin panel as an internal form, embedding a public form via the API, or building a custom form frontend that posts to the Directus API.

### What It Does Well

Directus gives you the most control:

- **Connect to an existing database.** If you already have a PostgreSQL or MySQL database, Directus wraps it without migrating your data. Your form submissions can land in the same database as your CRM, inventory, or any other system.
- **Flow automations** that trigger on form submission. A new submission can send an email, post to a Slack channel, create a task in another collection, or call an external API. No need for n8n if your automation is simple.
- **Role-based access control** that's granular enough for enterprise use. You can control who sees which submissions, which fields they can edit, and which API endpoints they can access.
- **REST and GraphQL APIs** with authentication, so you can build custom form frontends in any framework and post submissions to Directus.

### Where It Falls Short

Directus does not have a built-in public form builder with a drag-and-drop interface. The admin panel works for internal forms, but if you want a public-facing form, you need to either embed it via an iframe (limited) or build a custom frontend that posts to the API (requires development work).

The learning curve is steeper. Directus assumes you understand databases, collections, relationships, and flows. For a business that just wants to put up a contact form, it's overkill.

### Self-Hosting Directus

```yaml
# docker-compose.yml (simplified)
version: "3.8"
services:
  directus:
    image: directus/directus:latest
    ports:
      - "8055:8055"
    environment:
      - KEY=your-random-key
      - SECRET=your-random-secret
      - ADMIN_EMAIL=admin@yourdomain.com
      - ADMIN_PASSWORD=your-admin-password
      - DB_CLIENT=pg
      - DB_HOST=db
      - DB_PORT=5432
      - DB_NAME=directus
      - DB_USER=directus
      - DB_PASSWORD=your-password
    depends_on:
      - db
  db:
    image: postgis/postgis:16-3.4
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=directus
      - POSTGRES_USER=directus
      - POSTGRES_PASSWORD=your-password
volumes:
  pgdata:
```

## Which One Should You Pick?

The answer depends on what you're trying to do.

**Choose OpnForm if** you need a dedicated form builder with polished public-facing forms, payment collection, and form analytics. It's the best direct replacement for Typeform or Jotform. If forms are your primary data collection method and you want them to look professional without custom development, this is the right choice.

**Choose NocoDB Forms if** you want form submissions to flow directly into a database you manage, and you want to view that data in spreadsheets, Kanban boards, and calendars. It's ideal if you're already using NocoDB as your Airtable replacement and just need to add public data collection to your existing tables.

**Choose Directus if** you need form submissions to integrate deeply with an existing database, you want built-in automation (flows) triggered by submissions, and you have someone on your team who can build a custom form frontend. It's the most powerful option but requires the most setup.

## A Practical Combined Approach

These tools aren't mutually exclusive. A common pattern in self-hosted stacks is:

1. **OpnForm** for public-facing forms (contact, registration, feedback) where design and UX matter
2. **Webhook from OpnForm to n8n** that routes the submission
3. **NocoDB or Directus** as the database where submissions land and get managed by the team

This gives you the best of both worlds: beautiful forms for respondents, structured data storage for your team, and automation in between.

## Docker Compose for the Combined Stack

```yaml
version: "3.8"
services:
  opnform:
    image: jhumanj/opnform-api:latest
    ports:
      - "8080:80"
    environment:
      - APP_URL=https://forms.yourdomain.com
      - DB_HOST=opnform-db
      - DB_DATABASE=opnform
      - DB_USERNAME=opnform
      - DB_PASSWORD=secure-password
    depends_on:
      - opnform-db

  opnform-db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=opnform
      - POSTGRES_USER=opnform
      - POSTGRES_PASSWORD=secure-password
    volumes:
      - opnform-pgdata:/var/lib/postgresql/data

  nocodb:
    image: nocodb/nocodb:latest
    ports:
      - "8081:8080"
    volumes:
      - nocodb-data:/usr/app/data

  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=n8n.yourdomain.com
      - WEBHOOK_URL=https://n8n.yourdomain.com
    volumes:
      - n8n-data:/home/node/.n8n

volumes:
  opnform-pgdata:
  nocodb-data:
  n8n-data:
```

With this setup, an OpnForm submission triggers a webhook to n8n, which formats the data and writes it to a NocoDB table via its REST API. Your team reviews submissions in NocoDB's grid view, moves them through a Kanban pipeline, and exports reports when needed.

## Cost Comparison

All three tools can be self-hosted for free. The real cost is infrastructure:

| Component | Minimum Cost | Notes |
|-----------|-------------|-------|
| VPS (2GB RAM) | ~$6-12/month | Enough for OpnForm + NocoDB |
| VPS (4GB RAM) | ~$12-24/month | Add Directus + n8n |
| Domain + SSL | ~$10/year | Use Caddy for free SSL |
| Maintenance time | 1-2 hours/month | Updates, backups, monitoring |

Compare that to Typeform ($25-83/month), Airtable ($20-45/seat/month), and a separate automation tool ($20-50/month). The self-hosted stack pays for itself within the first month, and there are no per-response charges.

## Wrapping Up

The "best" form builder depends on your starting point. If you're replacing Typeform and want beautiful forms fast, OpnForm is the clear choice. If you're already running NocoDB as a database and just need to collect data into it, use NocoDB's form views. If you have an existing SQL database and want to build a comprehensive backend with forms, automations, and APIs, Directus is the most capable option.

All three are self-hostable, all three eliminate per-response pricing, and all three give you ownership of your data. The question isn't which is "best" in the abstract, but which fits your stack and your team's skills.

If you want help setting up any of these tools or designing a form-to-database workflow for your business, [reach out through our contact form](https://www.ardotconsulting.com/#contact). We specialize in open source automation for small businesses, and we can have you collecting data on your own infrastructure within a week.
