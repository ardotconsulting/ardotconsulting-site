---
layout: post
title: "Self-Hosting Nextcloud: Replace Google Workspace and Dropbox with Your Own Cloud Platform"
date: 2026-12-21
author: "ARDOT Consulting"
tags: [nextcloud, self-hosting, file-sharing, collaboration, open-source, cloud]
excerpt: "Replace Google Workspace and Dropbox with a self-hosted Nextcloud instance — file sharing, calendars, contacts, and document collaboration, all under your control."
---

Every small business hits the same wall eventually. You start with a free Google account, add a few shared folders in Dropbox, sign up for a calendar tool, maybe a separate contact manager — and before long you're paying three SaaS subscriptions, your files are scattered across platforms you don't control, and nobody knows where the latest version of anything lives.

It doesn't have to be that way.

**Nextcloud** is an open source cloud platform that combines file sharing, calendar, contacts, document editing, task management, and dozens of other features in a single self-hosted instance. Think of it as your own private Google Workspace — except you own the server, you control the data, and there's no monthly per-seat fee.

In this guide, we'll walk through what Nextcloud actually replaces, how to set it up with Docker, and what it costs compared to the SaaS alternatives it displaces.

---

## What Nextcloud Replaces

Before we get into the technical setup, let's be clear about the scope. Nextcloud isn't just a Dropbox clone — it's a full collaboration platform that grows through its app ecosystem. Here's what it can replace in a typical small business stack:

| SaaS Tool | What It Does | Nextcloud Replacement |
|-----------|-------------|----------------------|
| Google Drive / Dropbox | File storage and sharing | Nextcloud Files |
| Google Calendar | Shared calendaring | Nextcloud Calendar |
| Google Contacts | Contact management | Nextcloud Contacts |
| Google Docs / Sheets | Document collaboration | Nextcloud Office (Collabora) |
| Google Keep / Tasks | Notes and tasks | Nextcloud Tasks + Nextcloud Notes |
| Zoom (basic) | Video calls | Nextcloud Talk |
| Trello (basic) | Kanban boards | Nextcloud Deck |

Not every Nextcloud app is a perfect 1:1 replacement. Nextcloud Talk, for instance, works well for internal team calls but isn't trying to compete with Zoom's webinar features. Nextcloud Deck covers basic kanban workflows but won't replace a dedicated project management tool for complex teams. The point is that for a small business — say 5 to 50 people — Nextcloud can consolidate five or six separate subscriptions into one platform.

---

## Why Self-Host Instead of Using Nextcloud Cloud?

Nextcloud offers a hosted cloud option through their partners, so you could pay someone else to run it. But self-hosting gives you three things the hosted version can't:

1. **Full data sovereignty.** Your files never leave your server. For businesses handling client contracts, financial documents, or regulated data, this matters.
2. **No per-user pricing.** Whether you have 5 users or 500, the software cost is the same — zero. You only pay for the server hardware and electricity.
3. **Total control over apps and config.** You decide which apps are enabled, how authentication works, and what integrations you run. No vendor deciding to deprecate a feature you depend on.

The trade-off is that you're responsible for updates, backups, and security. We'll cover those in the setup guide below.

---

## Hardware Requirements

Nextcloud is not lightweight. It's a full web application with a database, a PHP backend, and optionally a document editing server. Here's what you need:

**Minimum (up to 15 users):**
- 2 CPU cores
- 4 GB RAM
- 50 GB storage (depends on your files)
- Ubuntu 22.04 or 24.04 LTS

**Recommended (15–50 users):**
- 4 CPU cores
- 8 GB RAM
- 500 GB+ storage (SSD preferred)
- Ubuntu 22.04 or 24.04 LTS

You can run this on a dedicated mini PC (like an Intel NUC or Beelink), a rented VPS (Hetzner, OVH, DigitalOcean), or a spare server you already have. If you're already running other self-hosted services — maybe you followed our guides on [self-hosting Invoice Ninja](https://www.ardotconsulting.com/blog/2026/11/07/self-hosting-invoice-ninja-replace-quickbooks-and-freshbooks-with-your-own-invoicing-platform/) or [ERPNext](https://www.ardotconsulting.com/blog/2026/12/05/self-hosting-erpnext-replace-netsuite-and-sap-with-your-own-open-source-erp/) — you can run Nextcloud alongside them on the same machine if you have the RAM.

---

## Setting Up Nextcloud with Docker Compose

The cleanest way to run Nextcloud is with Docker Compose. This gives you Nextcloud itself, a MariaDB database, and Redis for caching — all in containers that are easy to update and back up.

### Step 1: Create the Docker Compose File

Create a directory for your Nextcloud deployment and add this `docker-compose.yml`:

```yaml
version: "3.8"

services:
  db:
    image: mariadb:10.11
    restart: unless-stopped
    command: --transaction-isolation=READ-COMMITTED --log-bin=binlog --binlog-format=ROW
    volumes:
      - ./db_data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=change_this_strong_password
      - MYSQL_PASSWORD=nextcloud_db_password
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
    networks:
      - nextcloud-net

  redis:
    image: redis:alpine
    restart: unless-stopped
    networks:
      - nextcloud-net

  app:
    image: nextcloud:apache
    restart: unless-stopped
    depends_on:
      - db
      - redis
    ports:
      - 8080:80
    volumes:
      - ./nextcloud_data:/var/www/html
    environment:
      - MYSQL_HOST=db
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_PASSWORD=nextcloud_db_password
      - REDIS_HOST=redis
      - NEXTCLOUD_ADMIN_USER=admin
      - NEXTCLOUD_ADMIN_PASSWORD=change_this_admin_password
      - NEXTCLOUD_TRUSTED_DOMAINS=cloud.yourdomain.com
    networks:
      - nextcloud-net

networks:
  nextcloud-net:
```

**Before you start:** change every password in this file. Use a password manager — we recommend [Vaultwarden](https://www.ardotconsulting.com/blog/2026/10/16/self-hosting-vaultwarden-replace-lastpass-with-your-own-password-manager/) — to generate and store strong passwords.

### Step 2: Start the Stack

```bash
cd /opt/nextcloud
docker compose up -d
```

After 30–60 seconds, Nextcloud will be running on port 8080 of your server. Open `http://YOUR_SERVER_IP:8080` in a browser and you should see the Nextcloud setup screen. If you used the environment variables above, the admin account is already configured.

### Step 3: Set Up HTTPS with a Reverse Proxy

Running Nextcloud over HTTP is fine for testing, but you should never expose it to the internet without TLS encryption. The easiest way to add HTTPS is with Caddy, which automatically provisions Let's Encrypt certificates.

Create a `Caddyfile`:

```
cloud.yourdomain.com {
    reverse_proxy localhost:8080
}
```

Then run Caddy in a container alongside your Nextcloud stack:

```bash
docker run -d --name caddy --restart unless-stopped \
  -p 80:80 -p 443:443 \
  -v /opt/nextcloud/Caddyfile:/etc/caddy/Caddyfile \
  -v caddy_data:/data \
  -v caddy_config:/config \
  caddy:latest
```

Point your domain's DNS A record to your server's IP address, and Caddy will handle the rest — certificate provisioning, HTTPS redirection, and proxying requests to Nextcloud.

### Step 4: Install the Apps You Need

Nextcloud ships with file sharing enabled by default. The other features — calendar, contacts, tasks, document editing — are apps you install through the web interface. Log in as admin, click your profile icon → **Apps**, and install:

- **Calendar** — shared calendars with CalDAV support
- **Contacts** — contact management with CardDAV support
- **Tasks** — task lists synced across devices
- **Deck** — kanban-style project boards
- **Nextcloud Office** (requires Collabora or OnlyOffice) — collaborative document editing

For Nextcloud Office, you'll need to run a separate Collabora CODE container. Add this to your `docker-compose.yml`:

```yaml
  collabora:
    image: collabora/code
    restart: unless-stopped
    ports:
      - 9980:9980
    environment:
      - aliasgroup1=https://cloud.yourdomain.com
      - extra_params=--o:ssl.termination=true --o:ssl.enable=false
    networks:
      - nextcloud-net
```

Then in Nextcloud, go to **Administration Settings → Nextcloud Office** and point it to `https://cloud.yourdomain.com:9980` (or through your reverse proxy).

---

## Cost Comparison: Self-Hosted Nextcloud vs SaaS

Let's put real numbers on this. Here's what a 15-person business might pay for the SaaS tools Nextcloud replaces:

| Service | Monthly Cost (15 users) |
|---------|------------------------|
| Google Workspace Business Starter | $107.85 ($7.19/user) |
| Dropbox Business Standard | $225.00 ($15/user) |
| Calendly Teams (basic scheduling) | $96.00 ($8/user) |
| **Total SaaS** | **~$429/month** |

And here's what self-hosted Nextcloud costs:

| Item | Monthly Cost |
|------|-------------|
| VPS (4 cores, 8 GB RAM, 500 GB SSD) | ~$20–$35 |
| Domain name (annual, amortized) | ~$1 |
| Electricity (if self-hosted on own hardware) | ~$5–$15 |
| Backup storage (e.g., S3-compatible or local NAS) | ~$5–$10 |
| **Total self-hosted** | **~$31–$61/month** |

That's a savings of roughly **$370–$400 per month**, or **$4,400–$4,800 per year** — and the savings scale. At 50 users, the SaaS costs triple while the self-hosted costs barely change (you might upgrade to a larger server for an extra $20/month).

These are back-of-the-envelope numbers. Your actual costs depend on your cloud provider, storage needs, and whether you already have hardware. But the pattern holds: SaaS pricing scales with headcount, and self-hosting doesn't.

---

## Keeping Nextcloud Secure and Updated

Self-hosting means you're the IT department. Here's a practical security checklist:

### Updates

Nextcloud releases updates roughly every few months. Update by pulling the new Docker image:

```bash
cd /opt/nextcloud
docker compose pull
docker compose up -d
docker compose exec app occ upgrade
```

The `occ upgrade` step runs the internal database migrations. Always back up before updating.

### Backups

Your Nextcloud data lives in two places: the `nextcloud_data` volume (files) and the `db_data` volume (database). Back up both:

```bash
# Back up the database
docker compose exec db mysqldump -u root -p nextcloud > nextcloud_db_backup.sql

# Back up the files
tar -czf nextcloud_files_backup.tar.gz ./nextcloud_data
```

Automate this with a cron job and send backups to off-site storage. We covered backup strategies in detail in our [disaster recovery guide](https://www.ardotconsulting.com/blog/2026/11/17/backing-up-your-self-hosted-stack-a-practical-disaster-recovery-guide/) — the same principles apply here.

### Access Control

- **Enable two-factor authentication.** Nextcloud supports TOTP apps out of the box. Go to **Settings → Personal → Security** and turn it on for the admin account, then require it for all users via **Administration Settings → Two-Factor TOTP**.
- **Restrict admin access.** Only give admin roles to people who need them. Nextcloud has fine-grained group and share permissions.
- **Use strong passwords.** Enforce minimum password lengths under **Administration Settings → Security**.
- **Keep the server updated.** Run `apt update && apt upgrade` on the host OS regularly.

### Network Security

- Don't expose the database or Redis ports to the internet. Only ports 80 and 443 (for the reverse proxy) should be public.
- Use a firewall (UFW on Ubuntu is simplest):

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

- Consider running Nextcloud behind a VPN for internal-only deployments. If your team is remote, something like WireGuard gives you a secure tunnel without exposing Nextcloud to the public internet at all.

---

## Migrating From Google Workspace or Dropbox

Moving your files is the most common migration path, and it's straightforward:

1. **Download your files** from Google Drive or Dropbox. Google Takeout lets you export everything as a zip archive. Dropbox has a similar export feature.
2. **Upload to Nextcloud.** You can drag and drop through the web interface for small batches, or use the Nextcloud desktop client (available for Windows, macOS, and Linux) to sync large directories.
3. **Migrate calendars.** Export your Google Calendars as `.ics` files, then import them into Nextcloud Calendar.
4. **Migrate contacts.** Export from Google Contacts as vCard (`.vcf`) and import into Nextcloud Contacts.

For large migrations (hundreds of GB), use the `occ` command-line tool to pre-seed files directly on the server, which avoids uploading through the browser:

```bash
docker compose exec app occ files:scan --all
```

This tells Nextcloud to scan its data directory and register any files you've copied there manually.

---

## When Nextcloud Is NOT the Right Choice

Self-hosting isn't always the answer. Here's when you might want to stick with SaaS:

- **You have fewer than 5 users and no technical staff.** The setup and maintenance time may exceed the subscription savings. Nextcloud's hosted plans or a simpler tool like [BookStack](https://www.ardotconsulting.com/blog/2026/10/04/building-an-internal-knowledge-base-with-bookstack-and-ai/) for document sharing might be a better fit.
- **You need advanced real-time collaboration.** If your team lives in shared spreadsheets with 20 people editing simultaneously, Google Sheets still handles that better than Nextcloud Office. Collabora is improving, but it's not there yet for heavy real-time use.
- **You have no one to manage backups.** If the server dies and there's no backup, you lose everything. If you can't commit to a backup routine, the managed SaaS version is safer.
- **You're subject to specific compliance certifications.** SaaS providers often have SOC 2, HIPAA, or ISO 27001 certifications. Self-hosted Nextcloud can be configured to meet these requirements, but the audit burden is on you.

For most small businesses with someone who can follow a Docker guide and run a backup script once a week, Nextcloud is a strong fit.

---

## Integrating Nextcloud with Your Automation Stack

Nextcloud doesn't exist in isolation. It plays well with other open source tools:

- **n8n** can connect to Nextcloud via its WebDAV API, enabling automated workflows like "when a form is submitted, save the attachment to a Nextcloud folder and notify the team in [Mattermost](https://www.ardotconsulting.com/blog/2026/10/08/self-hosting-mattermost-replace-slack-with-your-own-team-chat-platform/)."
- **Ollama** can process documents stored in Nextcloud — for example, summarizing uploaded contracts or extracting key terms from invoices.
- **ERPNext** and **Odoo** can store generated reports and exports in Nextcloud shared folders, giving your team a single place to find business documents.

Here's a simple n8n workflow snippet that uploads a file to Nextcloud when it arrives in an email attachment:

```
[Email Trigger] → [Extract Attachment] → [Nextcloud Upload Node]
                                          → [Mattermost Notification]
```

The Nextcloud node in n8n uses WebDAV credentials (username + app password), which you generate under **Settings → Personal → Security → Devices & sessions** in Nextcloud.

---

## Final Thoughts

Google Workspace and Dropbox are good products. They work, they're polished, and someone else handles the updates. But they come with a hidden cost: your data lives on someone else's servers, and the price goes up every time you add a team member.

Nextcloud gives you the same core capabilities — file sharing, calendars, contacts, document collaboration — on infrastructure you control, at a cost that doesn't scale with headcount. For a small business willing to invest a weekend in setup and an hour a month in maintenance, the payoff is substantial: lower costs, full data ownership, and a platform you can customize to fit your workflow instead of adapting your workflow to fit a SaaS product.

If you're already self-hosting other tools, Nextcloud is a natural addition. If this is your first self-hosted service, it's a good place to start — the Docker setup is well-documented, the community is large, and the payoff is immediate.

---

## Ready to Take Control of Your Business Data?

If you're tired of per-seat SaaS pricing and want to explore what a self-hosted collaboration platform could look like for your business, we can help. ARDOT Consulting specializes in open source automation and infrastructure for small businesses — from initial setup to ongoing maintenance.

[Contact us](https://www.ardotconsulting.com/#contact) to schedule a free consultation. We'll assess your current tool stack, identify what you can consolidate, and build a migration plan that fits your team and budget.