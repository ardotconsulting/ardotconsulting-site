---
layout: post
title: "Self-Hosting Chatwoot: An Open-Source Omnichannel Customer Support Platform"
date: 2027-01-02
author: "ARDOT Consulting"
tags: [chatwoot, customer-support, self-hosting, open-source, omnichannel, docker, n8n, ollama]
excerpt: "Customer support tools like Zendesk and Intercom charge per seat, per month, forever. Chatwoot gives you the same omnichannel inbox — live chat, email, WhatsApp, social — as open source you can self-host. Here's what it does, how to deploy it with Docker, and how to extend it with local AI."
---

# Self-Hosting Chatwoot: An Open-Source Omnichannel Customer Support Platform

If your support team has grown past the point where a shared inbox and a spreadsheet can keep things organized, you've probably looked at a customer support platform. Zendesk. Intercom. Salesforce Service Cloud. The feature lists look great. The pricing pages are where the enthusiasm fades.

A typical mid-size team — say 8 to 15 agents — will pay anywhere from $400 to $1,500 per month for a decent support desk, depending on features and add-ons. Every new agent you hire adds $50–$150 to the bill. Add WhatsApp or a second brand, and you're in enterprise pricing territory. Over three years, a 10-person team can easily spend $50,000–$80,000 on support software — software whose main job is to display conversations and let agents type replies.

Chatwoot is the open-source alternative. It's an omnichannel customer support platform that consolidates live chat, email, WhatsApp, Instagram, Facebook, Telegram, and SMS into a single shared inbox. Your agents work from one screen. Your data stays on your infrastructure. Your monthly cost is the server it runs on — typically $20–$40 for a modest VPS.

In this post, we'll cover what Chatwoot actually does, how to self-host it with Docker, how it compares to the SaaS incumbents, and how to extend it with local AI using n8n and Ollama. No per-seat fees, no vendor lock-in, no sending customer conversations to a third party.

---

## What Chatwoot Actually Does

Chatwoot's core promise is simple: one inbox for every channel your customers use to reach you. Let's break down the features that matter for a business owner evaluating it.

### Omnichannel Shared Inbox

This is the headline feature. Chatwoot connects to multiple communication channels and funnels every conversation into a single dashboard:

- **Website live chat** — a widget you embed on your site, styled to match your brand
- **Email** — connect a support address (support@yourcompany.com) and Chatwoot converts emails into tickets
- **WhatsApp** — via the WhatsApp Cloud API, so conversations sync automatically
- **Facebook and Instagram** — direct messages and page messages feed into the inbox
- **Telegram and Line** — for teams using these channels for support
- **SMS** — through supported integrations
- **API channel** — build your own channel integration if you need something custom

Your agents see a unified conversation view. A customer who emailed yesterday and used live chat today shows up as one contact with one conversation history. That continuity matters — customers hate repeating themselves, and agents waste time hunting for context.

### Help Center Portal

Chatwoot includes a built-in help center where you can publish FAQ articles, setup guides, and troubleshooting docs. Customers can search for answers before they contact you, which reduces ticket volume. The articles are hosted on your own domain (e.g., help.yourcompany.com), so they contribute to your SEO rather than driving traffic to a SaaS subdomain.

If you've used Zendesk's Help Center or Intercom's Articles, the concept is identical. The difference is you own the content and the platform.

### Team Collaboration Features

Support isn't just about answering messages — it's about coordinating behind the scenes. Chatwoot supports:

- **Private notes** — agents can add internal notes to a conversation that the customer can't see
- **@mentions** — pull a teammate into a conversation for a second opinion
- **Canned responses** — save common replies and insert them with a shortcut
- **Labels** — tag conversations by topic, priority, or status for filtering
- **Auto-assignment** — route conversations to agents based on availability and workload
- **Teams** — group agents (e.g., Sales, Billing, Technical) and route conversations accordingly
- **Business hours** — set when your team is available and use auto-responders outside those hours
- **Agent capacity management** — limit how many conversations an agent handles at once to prevent overload

### Contact Management

Every conversation is tied to a contact profile. Chatwoot stores the customer's name, email, phone number, location, and interaction history. You can add custom attributes — like a customer ID, plan tier, or account manager — and segment contacts for targeted campaigns.

### Reporting

Chatwoot provides reports on conversation volume, agent performance, inbox-level metrics, and CSAT (customer satisfaction) scores. You can see which channels generate the most volume, which agents are most responsive, and how satisfaction trends over time. Reports are downloadable for offline analysis.

### Captain — AI Agent

Chatwoot recently added an AI agent feature called Captain. It can handle common queries automatically, suggest responses to agents, and reduce the load on your team during peak hours. We'll cover an open-source approach to this later in the post using Ollama and n8n, which gives you more control over the AI and keeps the data on your infrastructure.

---

## Chatwoot vs the SaaS Incumbents

Let's be honest about the comparison. Here's how Chatwoot stacks up against the most popular SaaS alternatives.

| Feature | Chatwoot (Self-Hosted) | Zendesk | Intercom |
|---------|----------------------|---------|----------|
| Monthly cost (10 agents) | ~$40 (server) | ~$500–$1,500 | ~$400–$1,200 |
| Omnichannel inbox | Yes | Yes | Yes |
| Live chat widget | Yes | Yes | Yes |
| Email tickets | Yes | Yes | Yes |
| WhatsApp | Yes | Yes (add-on) | Yes (add-on) |
| Help center | Yes | Yes | Yes |
| Data ownership | Full | Vendor-hosted | Vendor-hosted |
| Customization | Source code access | Limited | Limited |
| AI features | Captain + open extensibility | Zendesk AI (add-on) | Fin AI (add-on) |
| Setup effort | Moderate (Docker) | None (SaaS) | None (SaaS) |
| Ongoing maintenance | You handle updates | Automatic | Automatic |

The tradeoff is clear. SaaS tools are faster to start with — you sign up, configure, and go. Chatwoot requires you to deploy and maintain it. But the cost difference is dramatic: a self-hosted Chatwoot instance costs roughly the same per year as one month of Zendesk for a 10-person team.

There's also the data question. If you're in healthcare, legal, or finance, sending customer conversations to a third-party SaaS may create compliance concerns. Self-hosting puts the data on infrastructure you control, behind your firewall, subject to your backup and retention policies.

---

## Self-Hosting Chatwoot with Docker

Chatwoot is a Ruby on Rails application with a Vue.js frontend and a PostgreSQL database. The easiest way to self-host is with Docker Compose. Here's a practical deployment guide.

### What You'll Need

- A Linux server (Ubuntu 22.04 or 24.04 LTS recommended) with at least 4 GB RAM and 2 CPU cores. A $20–$40/month VPS from most providers will handle a small-to-mid team comfortably.
- Docker and Docker Compose installed
- A domain name (e.g., support.yourcompany.com) with DNS pointing to your server
- SSL certificates — we'll use the Chatwoot-provided setup with Let's Encrypt

### Step 1: Clone and Configure

```bash
git clone https://github.com/chatwoot/chatwoot.git
cd chatwoot
```

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit the `.env` file and set these critical values:

```bash
# Your domain
FRONTEND_URL=https://support.yourcompany.com

# Generate a secret key
SECRET_KEY_BASE=replace_with_secure_random_string

# Database settings
RAILS_ENV=production
DATABASE_URL=postgresql://chatwoot:yourpassword@db:5432/chatwoot_production

# Redis (for background jobs)
REDIS_URL=redis://redis:6379

# Mail settings (use your SMTP provider)
SMTP_ADDRESS=smtp.yourprovider.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
```

### Step 2: Build and Launch

Chatwoot provides a Docker Compose file for production. Build and start the services:

```bash
docker compose -f docker-compose.production.yaml up -d --build
```

This launches the Chatwoot web service, a PostgreSQL database, a Redis server, and background workers (Sidekiq) for processing jobs like email parsing and report generation.

### Step 3: Initialize the Database

Run the database migration and seed the initial admin account:

```bash
docker compose -f docker-compose.production.yaml exec web bundle exec rails db:reset
```

This creates the database schema and a default admin account. You'll get credentials to log in for the first time. Change the password immediately.

### Step 4: Set Up SSL and Reverse Proxy

The Chatwoot repository includes a setup script that configures Nginx as a reverse proxy and provisions SSL certificates via Let's Encrypt:

```bash
# The repo provides a setup script for this
# Follow the official docs for your specific setup:
# https://www.chatwoot.com/docs/self-hosted/deployment/docker-compose
```

Alternatively, if you already run a reverse proxy like Caddy or Traefik, you can point it at the Chatwoot container's port (typically 3000) and let it handle SSL automatically.

### Step 5: Connect Your Channels

Once Chatwoot is running, log in as admin and start connecting channels:

1. **Live chat** — Create a website inbox, customize the widget's color and position, and embed the script on your site
2. **Email** — Connect a support email address via SMTP/IMAP. Chatwoot will poll the inbox and convert emails into conversations
3. **WhatsApp** — Connect via the WhatsApp Cloud API (requires a Meta Business account). This is the most involved setup but works reliably once configured
4. **Social channels** — Connect Facebook Pages and Instagram business accounts via OAuth

Test each channel by sending a message from a customer perspective and verifying it appears in the Chatwoot inbox.

---

## Extending Chatwoot with Local AI

Chatwoot's Captain feature is convenient, but it routes conversations through Chatwoot's cloud AI. If you want AI-powered responses without sending customer data to a third party, you can build your own integration using n8n and Ollama.

### The Architecture

Here's the pattern:

1. **Chatwoot webhook** — When a new message arrives, Chatwoot sends a webhook to n8n
2. **n8n workflow** — n8n receives the webhook, extracts the message content and conversation context
3. **Ollama inference** — n8n sends the message to a local Ollama instance running a model like Llama 3 or Mistral, with a system prompt that includes your help center articles and product documentation
4. **Reply or suggestion** — Ollama generates a response. n8n either posts it directly back to Chatwoot (full automation) or saves it as a private note for an agent to review (suggested reply)

### Setting Up the n8n Workflow

In n8n, create a workflow triggered by a Chatwoot webhook:

```
[Chatwoot Webhook] → [Extract Message & Context] → [Ollama Node] → [Chatwoot API: Reply]
```

The Ollama node configuration:

- **Model:** `llama3` (or whichever model you've pulled)
- **System prompt:** Include your FAQs, return policy, shipping times, and common troubleshooting steps. For example:

```
You are a customer support assistant for [Your Company].
Use this knowledge base to answer questions:
- Return policy: 30 days, original packaging required
- Shipping: Free over $50, 3-5 business days
- Warranty: 1 year on all electronics
- Support hours: Mon-Fri 9am-6pm EST

If you're unsure, say so. Never invent information.
Keep responses under 150 words. Be friendly and direct.
```

- **Temperature:** 0.3 (low — you want consistent, factual answers, not creative ones)

### Full Automation vs Suggested Replies

Start with suggested replies. Have n8n post the AI response as a **private note** on the conversation. The agent reviews it, edits if needed, and sends it as the reply. This catches errors early and builds trust in the AI before you fully automate.

After a few weeks of reviewing suggestions, you'll see which types of questions the AI handles well. Route those to full automation (n8n posts the reply directly) and keep the rest as suggestions. This hybrid approach typically handles 30–50% of common questions automatically while keeping human oversight for anything complex.

### Connecting Ollama

If you've followed our previous guide on running local LLMs with Ollama, you already have the foundation. Just make sure the Ollama instance is accessible from n8n (same Docker network or accessible IP):

```bash
# Pull a model suitable for customer support
ollama pull llama3

# Test it
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "What is your return policy?",
  "stream": false
}'
```

---

## What This Costs

Let's put real numbers on the table for a 10-person support team over three years.

| Item | Self-Hosted Chatwoot | Zendesk (Suite Team) |
|------|---------------------|---------------------|
| Software license | $0 | $55/agent/month ($6,600/year) |
| Server (4 GB VPS) | ~$40/month ($480/year) | $0 (vendor-hosted) |
| AI (Ollama on existing server) | $0 (already running) | $50/agent/month add-on ($6,000/year) |
| Backups | ~$10/month | $0 |
| IT time for maintenance | ~2 hrs/month (~$200/month) | $0 |
| **3-year total** | **~$24,480** | **~$37,800** |

The savings compound as you add agents. With Chatwoot, adding an 11th agent costs nothing. With Zendesk, it's another $105/month (base + AI). By year three, a 15-person team would spend roughly $56,700/year on Zendesk versus $8,160/year on self-hosted Chatwoot — a $48,540 annual difference.

The catch is the maintenance. Someone needs to update Chatwoot when new versions ship, monitor the server, and handle backups. If you don't have anyone comfortable with Docker and a Linux command line, the SaaS convenience may be worth the premium. But if you're already self-hosting other tools — n8n, Ollama, Nextcloud — adding Chatwoot to the same server or a companion VPS adds minimal overhead.

---

## When Chatwoot Is (and Isn't) the Right Choice

**Chatwoot is a good fit if:**

- You're spending more than $200/month on support software and want to cut that cost
- You need omnichannel support (live chat + email + WhatsApp + social) in one inbox
- You're in a regulated industry where keeping customer data on your own infrastructure matters
- You already have Docker infrastructure and a team comfortable maintaining it
- You want to integrate AI-powered support without sending conversations to a third-party API

**Chatwoot may not be the right fit if:**

- Your team is very small (1–2 people) and a shared Gmail inbox is working fine
- You have zero infrastructure and no one to maintain a server — the SaaS convenience is worth the cost in this case
- You need highly specialized features that Chatwoot doesn't offer yet (advanced custom SLA management, complex multi-brand routing with distinct knowledge bases per brand)
- Your support volume is very low and doesn't justify any dedicated platform

The honest answer: Chatwoot shines in the middle — teams of 3 to 50 agents who need a real support platform but are tired of the SaaS pricing treadmill. Below that, a shared inbox works. Above that, you may need features that require a more enterprise-focused solution (though many of those have open-source alternatives too).

---

## Migration Tips

If you're moving from Zendesk or Intercom to Chatwoot, here's how to approach the transition:

1. **Export your data.** Most SaaS platforms let you export tickets and contacts as CSV or JSON. Do this before you cancel your subscription.
2. **Start with one channel.** Connect live chat first, get your team comfortable with the interface, then add email, then WhatsApp. Don't migrate everything on day one.
3. **Rebuild canned responses.** Copy your saved replies into Chatwoot manually. It's tedious but ensures they work in the new format.
4. **Run parallel for two weeks.** Keep the SaaS account active while your team uses Chatwoot. If something breaks, you have a fallback. Once the team is confident, cancel the SaaS subscription.
5. **Back up before updates.** Before updating Chatwoot to a new version, back up the database volume. `docker compose exec db pg_dump chatwoot_production > backup.sql` takes 30 seconds and saves you from bad updates.

---

## Wrapping Up

Customer support software shouldn't be one of your largest monthly expenses. Chatwoot gives you a full omnichannel support platform — live chat, email, WhatsApp, social, help center, reporting — as open source you host on your own infrastructure. For a 10-person team, the three-year savings over Zendesk typically run $13,000–$15,000, and the gap widens with every agent you add.

The tradeoff is operational: you deploy and maintain it. But if you're already running Docker-based infrastructure or self-hosting other tools, Chatwoot fits naturally alongside them. And when you extend it with n8n and Ollama for AI-powered suggested replies, you get the same automation benefits as the SaaS AI add-ons — without the per-seat fees or the data leaving your network.

If you're evaluating a move away from Zendesk or Intercom, or setting up customer support for the first time and want to avoid the SaaS trap from the start, Chatwoot is worth a serious look. **[Get in touch](/#contact)** — we help businesses deploy and configure self-hosted support platforms, set up AI-powered response workflows, and migrate off expensive SaaS subscriptions without losing a single conversation.
