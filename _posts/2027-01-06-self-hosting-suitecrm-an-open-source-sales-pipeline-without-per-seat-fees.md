---
layout: post
title: "Self-Hosting SuiteCRM: An Open-Source Sales Pipeline Without Per-Seat Fees"
date: 2027-01-06
author: "ARDOT Consulting"
tags: [suitecrm, crm, sales-pipeline, self-hosting, open-source, docker, n8n, ollama, automation]
excerpt: "Commercial CRM platforms charge per seat — and the bill climbs fast as your sales team grows. SuiteCRM gives you the full feature set with zero per-seat licensing. Here's how to self-host it, configure a working sales pipeline, and automate lead routing with open-source tools."
---

# Self-Hosting SuiteCRM: An Open-Source Sales Pipeline Without Per-Seat Fees

Here's a familiar scenario: your sales team grows from three people to seven, and your CRM bill quietly triples. Most commercial CRM platforms — Salesforce, HubSpot, Zoho — charge per user, per month. Add a sales rep, add a license. Add an operations person who needs read access, add another license. Add a marketing coordinator who occasionally pulls a report, and yes, that's another license. Before long, you're paying $1,500–$5,000 a month for software that mostly stores contact records and tracks deal stages.

That's the tax on growth. The more successful your team gets, the more you pay — not because you're using more features, but because you have more people who need to log in.

SuiteCRM is the open-source alternative. It's a full-featured CRM — contact management, sales pipelines, lead routing, email integration, reporting, workflow automation — with no per-seat licensing. You install it once on your own server, and whether you have three users or thirty-three, the software cost is zero. The only cost is the server it runs on, which is typically $20–$60 a month for a VPS.

In this post, we'll walk through self-hosting SuiteCRM with Docker, configuring a practical sales pipeline, and connecting it to n8n and Ollama for automated lead routing and enrichment. No SaaS subscriptions required.

---

## What You Get With SuiteCRM

Before we get into installation, let's be clear about what SuiteCRM is and isn't, because there's a lot of misinformation floating around.

SuiteCRM is a fork of SugarCRM Community Edition, created in 2013 when SugarCRM stopped maintaining the open-source version. It's been actively developed since then, with a community of contributors and a commercial backing company (SalesAgility). The current version (as of writing) is 8.x, with a modern interface that's a significant improvement over the older 7.x series.

**What it includes out of the box:**

- **Accounts and Contacts** — Full contact management with relationships between companies and people
- **Leads and Opportunities** — Sales pipeline tracking from initial inquiry through closed deal
- **Activities** — Calls, meetings, tasks, and email tracking tied to records
- **Workflow engine** — Automated actions based on record changes (no external tools needed for basic automation)
- **Reporting** — Custom reports with filters, grouping, and charts
- **Quotes and Products** — Basic quoting and product catalog
- **Email integration** — Connect to IMAP/SMTP for email tracking and campaigns
- **Role-based access control** — Granular permissions for teams and individuals

**What it doesn't include (without add-ons):**

- Marketing automation (email campaigns are basic — use Mautic for serious marketing automation)
- Advanced AI features (we'll add these via Ollama integration)
- Native mobile app (the web interface is mobile-responsive, but there's no dedicated app)

Compared to Salesforce, SuiteCRM covers roughly 70–80% of what a small-to-mid-size business actually uses. The missing 20–30% is typically enterprise features — territory management, advanced forecasting, CPQ (configure-price-quote) — that most businesses don't need or can handle with a simple add-on.

---

## The Cost Comparison

Let's put real numbers on this. Here's what a 10-person sales team pays per year:

| Platform | Per-Seat Cost (Standard Tier) | 10 Users / Year | Self-Hosted SuiteCRM |
|----------|-------------------------------|-----------------|---------------------|
| Salesforce Starter | ~$25/user/month | $3,000 | — |
| Salesforce Professional | ~$80/user/month | $9,600 | — |
| HubSpot Professional | ~$90/user/month | $10,800 | — |
| SuiteCRM (self-hosted) | $0 | $0 | Server: $240–$720/yr |

Even at the cheapest commercial tier, you're paying $3,000 a year. At the tier most businesses actually need (Professional/Enterprise), it's $9,600–$15,000+. SuiteCRM's annual cost is whatever you pay for the server — call it $500 a year for a reasonably-sized VPS with daily backups.

Over three years, that's $9,000–$45,000 in CRM licensing you didn't spend. That's a salesperson's bonus, a trade show budget, or six months of marketing automation tooling.

---

## Installing SuiteCRM with Docker

SuiteCRM can be installed on bare metal, but Docker is the cleanest approach — it handles dependencies, makes upgrades easier, and keeps the installation reproducible.

### Prerequisites

- A VPS with at least 4GB RAM and 40GB disk (a $20–$40/month server from any provider)
- Docker and Docker Compose installed
- A domain name pointing to your server (e.g., `crm.yourcompany.com`)

### Docker Compose Setup

Create a directory for your SuiteCRM installation and add a `docker-compose.yml`:

```yaml
version: "3.8"

services:
  suitecrm-db:
    image: mariadb:10.11
    container_name: suitecrm-db
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: suitecrm
      MYSQL_USER: suitecrm
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - suitecrm-db-data:/var/lib/mysql
    networks:
      - suitecrm-net

  suitecrm:
    image: suitecrm/suitecrm:8.4
    container_name: suitecrm
    restart: unless-stopped
    depends_on:
      - suitecrm-db
    environment:
      DB_HOST: suitecrm-db
      DB_NAME: suitecrm
      DB_USER: suitecrm
      DB_PASSWORD: ${DB_PASSWORD}
      SITE_URL: https://crm.yourcompany.com
    volumes:
      - suitecrm-data:/var/www/html
    ports:
      - "8080:80"
    networks:
      - suitecrm-net

volumes:
  suitecrm-db-data:
  suitecrm-data:

networks:
  suitecrm-net:
    driver: bridge
```

Create a `.env` file in the same directory with strong passwords:

```
DB_ROOT_PASSWORD=change-this-to-a-strong-password
DB_PASSWORD=another-strong-password
```

### Starting the Stack

```bash
docker compose up -d
```

After 2–3 minutes, SuiteCRM will be available at `http://your-server-ip:8080`. The first-run wizard will walk you through initial configuration — admin user creation, locale settings, and an optional sample data load (useful for testing).

### Securing with a Reverse Proxy

For production, put a reverse proxy in front of SuiteCRM to handle HTTPS. If you're already running Caddy or Nginx on the server, add a site block:

**Caddy (simplest — automatic HTTPS):**

```
crm.yourcompany.com {
    reverse_proxy localhost:8080
}
```

That's it. Caddy handles the Let's Encrypt certificate automatically.

**Nginx:**

```nginx
server {
    listen 80;
    server_name crm.yourcompany.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name crm.yourcompany.com;

    ssl_certificate /etc/letsencrypt/live/crm.yourcompany.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/crm.yourcompany.com/privkey.pem;

    client_max_body_size 64M;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

With Nginx, you'll need to obtain the certificate manually with certbot.

---

## Configuring Your Sales Pipeline

Once SuiteCRM is running, the first thing to set up is your sales pipeline — the stages a deal moves through from first contact to close. SuiteCRM calls these "Sales Stages" and they're customizable.

### Default Sales Stages (customize to your process)

SuiteCRM ships with a set of default stages. Most businesses will want to adjust them to match their actual sales process. Here's a practical set for a B2B services company:

| Stage | Meaning | Typical Duration |
|-------|---------|-----------------|
| New | Lead just entered the pipeline | Day 0 |
| Qualified | Confirmed they're a fit and have budget | 1–3 days |
| Demo Scheduled | Meeting booked to show the product/service | 3–7 days |
| Demo Complete | Meeting happened, next steps agreed | 7–14 days |
| Proposal Sent | Quote or proposal delivered | 14–21 days |
| Negotiation | Discussing terms, scope, pricing | 21–35 days |
| Closed Won | Deal signed | — |
| Closed Lost | Deal didn't close | — |
| Dead — No Response | Lead went cold, no follow-up response | — |

To edit these, go to **Admin → Dropdown Editor → sales_stage_dom**. You can rename, add, or remove stages. The key is to match your actual sales process, not a template.

### Setting Up Lead Assignment Rules

By default, SuiteCRM assigns all leads to the admin user. For a team, you'll want automatic assignment. SuiteCRM's built-in workflow engine handles this without external tools.

Go to **Admin → Workflow → New Workflow**:

1. **Target module:** Leads
2. **Trigger:** On record creation
3. **Condition:** `Lead Source` equals `Website Form` (or whatever source you want to route)
4. **Action:** Assign to → Round-robin among specified users

For round-robin assignment (distributing leads evenly among reps), SuiteCRM's workflow engine supports this natively. You can also assign based on territory, industry, or deal size by adding conditions:

- If `Industry` equals `Healthcare` → assign to Jane
- If `State` equals `TX` → assign to Bob
- If `Account Name` contains `Enterprise` → assign to senior rep

This is the kind of routing logic that commercial CRMs charge extra for or require a paid add-on. In SuiteCRM, it's built in.

---

## Connecting n8n for Advanced Automation

SuiteCRM's built-in workflow engine handles record-based automation well, but for integrations with external systems — your website forms, email, Slack, document signing — you need a more flexible tool. That's where n8n comes in.

SuiteCRM has a REST API (v8, using OAuth2). n8n can authenticate against it and create, update, or query any record type.

### Enabling the API

1. In SuiteCRM, go to **Admin → OAuth2 Clients → New**
2. Create a "Password Client" with client ID and secret
3. Note the credentials — you'll use them in n8n

### n8n Workflow: Website Form → Lead Creation

Here's a practical workflow: a prospect fills out a form on your website (which could be Opnform, Formbricks, or any form tool that sends webhooks), and n8n creates a lead in SuiteCRM with AI-enriched data.

**The n8n workflow nodes:**

1. **Webhook node** — Receives form submission
2. **Ollama node** — Enriches the lead (categorizes industry, suggests deal size range, generates a summary)
3. **HTTP Request node** — Authenticates to SuiteCRM OAuth2 and creates the lead
4. **HTTP Request node** — (Optional) Posts a notification to Mattermost or your team chat

Here's the HTTP Request node configuration for creating a lead in SuiteCRM:

```json
{
  "method": "POST",
  "url": "https://crm.yourcompany.com/api/v8/modules/Leads",
  "headers": {
    "Authorization": "Bearer {{$node[\"Auth\"].json[\"access_token\"]}}",
    "Content-Type": "application/vnd.api+json"
  },
  "body": {
    "data": {
      "type": "Leads",
      "attributes": {
        "first_name": "{{$json[\"firstName\"]}}",
        "last_name": "{{$json[\"lastName\"]}}",
        "email1": "{{$json[\"email\"]}}",
        "phone_work": "{{$json[\"phone\"]}}",
        "lead_source": "Website Form",
        "description": "{{$node[\"Ollama\"].json[\"summary\"]}}",
        "account_name": "{{$json[\"company\"]}}",
        "industry": "{{$node[\"Ollama\"].json[\"industry\"]}}"
      }
    }
  }
}
```

### AI Enrichment with Ollama

The Ollama node does the interesting part. When a lead comes in, we send the form data to a local LLM and ask it to:

1. **Categorize the industry** — Based on the company name and description
2. **Estimate deal size** — Based on company size and use case mentioned
3. **Generate a summary** — A two-sentence summary for the sales rep to read at a glance
4. **Flag urgency** — Is this a "need it now" inquiry or a "just exploring" one?

Here's the prompt we pass to Ollama (using a model like Llama 3.1 8B):

```
You are a sales assistant. Analyze this inbound lead and provide:
1. Industry (pick one: Healthcare, Legal, Finance, Retail, Manufacturing, Technology, Education, Construction, Hospitality, Other)
2. Estimated deal size range (Small: <$10k, Medium: $10k-$50k, Large: $50k+)
3. Two-sentence summary of what they're looking for
4. Urgency (High/Medium/Low) based on language used

Lead information:
Name: {{firstName}} {{lastName}}
Company: {{company}}
Email: {{email}}
Message: {{message}}

Respond in this format:
Industry: [value]
Deal Size: [value]
Summary: [value]
Urgency: [value]
```

Ollama processes this locally — no lead data ever leaves your server. The enriched lead lands in SuiteCRM within seconds of the form submission, and the assigned rep gets a notification in team chat with the AI-generated summary.

This is the kind of workflow that commercial CRM platforms sell as an "AI add-on" for $50–$100 per user per month. You're getting it for the cost of the server.

---

## Automating Follow-Up Sequences

Leads that don't get a response within the first hour are 21x less likely to convert. Most small businesses know this and still fail at it, because follow-up is manual and reps are busy.

With SuiteCRM + n8n, you can build an automated follow-up sequence:

1. **Lead created in SuiteCRM** → n8n detects via scheduled API poll (every 5 minutes)
2. **If no activity logged after 2 hours** → n8n sends an automated email: "Hi {{firstName}}, I saw your inquiry about {{topic}}. Do you have 15 minutes this week to talk through what you need?"
3. **If no activity after 24 hours** → n8n sends a second email and creates a task in SuiteCRM assigned to the rep: "Follow up with {{leadName}} — 24 hours, no response"
4. **If no activity after 72 hours** → n8n adds the lead to a nurture sequence in Listmonk (your self-hosted email platform)

The key difference from commercial CRM sequences: you control the logic entirely. No per-email pricing, no sequence limits, no vendor-imposed restrictions. If you want to add a condition that says "skip the follow-up email if the lead came from a partner referral," you just add a branch in n8n. No "upgrade to Enterprise to unlock branching logic."

---

## Migrating From Another CRM

If you're coming from Salesforce, HubSpot, or Zoho, migration is the obvious question. Here's the practical reality:

**From HubSpot:** HubSpot allows CSV export of contacts, companies, and deals. Export each, map the fields to SuiteCRM's import templates (Admin → Import), and bulk import. Custom field mappings are needed — HubSpot's "Lifecycle Stage" maps to SuiteCRM's "Sales Stage," for example. Plan for a half-day of data cleaning.

**From Salesforce:** Salesforce's Data Export Service gives you CSV files. The field mapping is more complex because Salesforce uses a different data model (Accounts vs. SuiteCRM's Accounts, Opportunities vs. SuiteCRM's Opportunities). Use SuiteCRM's import wizard with custom field mapping. For large datasets (10,000+ records), use the SuiteCRM REST API via n8n for batch import.

**From Zoho:** Zoho allows CSV export. The mapping is fairly clean since Zoho's CRM model is similar to SuiteCRM's.

**From spreadsheets:** If you've been tracking sales in a Google Sheet or Excel file, SuiteCRM's CSV import handles this directly. Map columns to fields, run the import, and you're done.

For any migration, the golden rule is: clean your data before importing. Deduplicate contacts, standardize company names, and fill in missing fields. Bad data imported into a new CRM is still bad data — just in a nicer interface.

---

## Backup and Maintenance

A self-hosted CRM needs a backup strategy. This isn't optional — losing your sales pipeline data is a business-ending event for most companies.

**Daily database backup (automated via cron):**

```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
docker exec suitecrm-db mysqldump -u root -p${DB_ROOT_PASSWORD} suitecrm > /backups/suitecrm-db-${DATE}.sql
find /backups -name "suitecrm-db-*.sql" -mtime +30 -delete
```

Add this to your server's crontab to run nightly. For off-site backup, sync the `/backups` directory to an S3-compatible storage bucket using rclone, or to a remote server using rsync.

**Upgrades:** SuiteCRM releases updates every few months. The Docker approach makes this straightforward:

```bash
docker compose pull
docker compose up -d
```

Always test on a staging instance first. Pull the new image, run it against a copy of your database, verify that your workflows and customizations still work, then upgrade production.

---

## When SuiteCRM Is the Wrong Choice

Honesty matters here. SuiteCRM isn't the right answer for every business. Here's when you should look elsewhere:

- **You need deep marketing automation** — SuiteCRM's email campaign tools are basic. If marketing automation (lead scoring, behavioral triggers, multi-step nurture sequences) is your primary need, pair it with Mautic or use Mautic as your primary tool and sync contacts to SuiteCRM.

- **You have complex territory management** — If your sales organization has multiple territories with overlapping rules and quota management, SuiteCRM's territory features are limited compared to Salesforce. A larger enterprise with 50+ reps in multiple regions may find this a dealbreaker.

- **You need CPQ (Configure-Price-Quote)** — SuiteCRM has basic quoting. For complex product configuration (rules-based pricing, bundle dependencies, approval workflows), you'll need an add-on or a dedicated CPQ tool.

- **You have zero IT capacity** — Self-hosting requires someone to handle updates, backups, and troubleshooting. If you don't have a part-time IT person or a managed services provider, the convenience of a SaaS CRM may be worth the per-seat cost.

For most small-to-mid-size businesses (5–50 users) with standard sales processes, SuiteCRM handles everything you need. The question isn't "can SuiteCRM do what Salesforce does?" — it's "do we actually use the features we're paying $10,000 a year for?"

---

## The Bottom Line

SuiteCRM gives you a full CRM — contacts, leads, opportunities, workflow automation, reporting — with no per-seat licensing. Combined with n8n for external integrations and Ollama for AI-powered lead enrichment, you get a sales pipeline platform that rivals commercial offerings at a fraction of the cost.

The trade-off is the same as with any self-hosted tool: you're responsible for the server, backups, and upgrades. If you're already self-hosting other tools (and if you've been reading this blog, you probably are), adding SuiteCRM to the stack is a natural step.

The per-seat tax is optional. You don't have to pay it.

---

*Want help setting up SuiteCRM or building an automated sales pipeline with open-source tools? [Get in touch](/#contact) — we design and implement self-hosted automation stacks for small and mid-size businesses.*
