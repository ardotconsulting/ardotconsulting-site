---
layout: post
title: "Self-Hosting Penpot: Replace Figma With Your Own Design Platform"
date: 2027-01-08
author: "ARDOT Consulting"
tags: [penpot, design, self-hosting, open-source, figma, docker, mpl]
excerpt: "Figma's per-editor pricing adds up fast for small teams. Penpot is an open source design platform you can self-host — unlimited editors, full data control, and no monthly subscription. Here's how to set it up with Docker and when it makes sense."
---

# Self-Hosting Penpot: Replace Figma With Your Own Design Platform

If your business does any kind of visual design work — marketing mockups, UI prototypes, social media graphics, wireframes, brand assets — you're probably paying for Figma. And if you have more than a couple of people who need to edit files, the bill climbs fast. Figma's Professional plan runs $15 per editor per month. Add five designers, a marketing manager who occasionally tweaks a mockup, and a founder who wants to review and comment, and you're at $1,080+ per year. Scale to a team of ten editors and you're paying $1,800 annually for the privilege of storing your brand assets on someone else's servers.

That's the SaaS tax on design work. You pay per seat, forever, and your proprietary design files live in a vendor's cloud. If Figma raises prices — they already did in 2024 — you eat the increase. If you stop paying, you lose access to your own work.

There's an alternative. **Penpot** is an open source design platform that does much of what Figma does: vector editing, prototyping, real-time collaboration, components, and design systems. You can self-host it on your own server, with unlimited editors, unlimited files, and full control over your data. The cost is a VPS and about an hour of setup time.

Let's walk through what Penpot is, how it compares to Figma, and how to get it running on your own infrastructure.

## What Is Penpot?

Penpot is an open source design and prototyping platform developed by Kaleidos, a Spanish tech company. It's been in active development since 2021 and has grown into one of the most starred design tools on GitHub, with over 35,000 stars and a thriving community. The project is licensed under the **Mozilla Public License 2.0 (MPL-2.0)**, a permissive open source license that allows you to use, modify, and self-host it freely, including for commercial use.

Unlike many "open source" tools that are really just feature-limited teasers for a paid cloud version, Penpot's self-hosted edition is the full product. There's no artificial cap on editors, projects, or features. The same codebase that runs on penpot.app is what you deploy on your own server.

Key features include:

- **Vector design tools** — full vector editing with shapes, paths, boolean operations, masks, and gradients
- **Prototyping** — create interactive prototypes with transitions, flows, and screen linking
- **Real-time collaboration** — multiple editors working on the same file simultaneously, with live cursors and comments
- **Design systems** — reusable components, design tokens, and shared libraries across projects
- **Flexible layout** — Grid, Flex Layout, and absolute positioning (their Flex Layout implementation is a standout — it uses CSS Grid and Flexbox natively, so what you design maps directly to what developers build)
- **SVG-native** — every design is stored as SVG, meaning your files are in an open format that any tool can read
- **Open API** — integrate Penpot with your other tools via REST API and webhooks
- **Multi-platform** — runs in any modern browser, no desktop app required

## Penpot vs Figma: A Practical Comparison

Before you rip out Figma, let's be honest about where Penpot stands.

| Feature | Figma (Professional) | Penpot (Self-Hosted) |
|---------|----------------------|---------------------|
| **Monthly cost** | $15/editor/month | Server cost only (~$10–$24/month) |
| **Editor limits** | Per-seat pricing | Unlimited |
| **File limits** | Team storage tiers | Unlimited (disk space only) |
| **Real-time collaboration** | Yes | Yes |
| **Prototyping** | Yes (advanced) | Yes |
| **Components & design systems** | Yes | Yes |
| **Dev Mode (code inspection)** | Yes (paid add-on) | CSS/Grid export (built-in) |
| **Plugin ecosystem** | Large | Growing (open plugin API) |
| **File format** | Proprietary (.fig) | Open SVG |
| **API access** | Yes (higher tiers) | Yes, included |
| **Self-hosting** | No | Yes |
| **Data residency** | US/EU (vendor-controlled) | Wherever you deploy |
| **Offline access** | Limited | Full (local instance) |
| **Setup time** | 2 minutes (SaaS) | 30–60 minutes (Docker) |
| **Maintenance** | Zero | Periodic updates, backups |

The trade-off is the same one that applies to every self-hosted tool. Figma is zero-maintenance, has a richer plugin ecosystem, and offers polished features like Dev Mode and advanced auto-layout that Penpot is still catching up on. Penpot self-hosted gives you unlimited everything, full data control, an open file format, and no recurring per-editor fees — but you handle updates, backups, and security.

For a team of 8 editors on Figma Professional at $15/editor/month, that's **$1,440 per year**. A self-hosted Penpot instance on a $24/month VPS costs **$288 per year**. The math speaks for itself, and the gap widens with every editor you add.

## When Self-Hosting Makes Sense (And When It Doesn't)

**Self-host Penpot if:**

- You have a design team of 3+ editors and per-seat fees are adding up
- You need full control over where design files are stored (client work under NDA, government contracts, regulated industries)
- You already self-host other tools (n8n, Nextcloud, Odoo) and have infrastructure in place
- You want your design files in an open format (SVG) rather than locked in a proprietary format
- You're comfortable with Docker and basic server administration

**Stick with Figma if:**

- You have only 1–2 editors and the monthly cost isn't a pain point
- You rely heavily on Figma's plugin ecosystem (Penpot's plugin system is newer and smaller)
- You need Figma's Dev Mode with its advanced code generation and inspection tools
- You need FigJam or other Figma-specific products that Penpot doesn't replicate
- You don't have anyone on your team who can maintain a server

## Prerequisites

To self-host Penpot, you'll need:

- A server running Linux (Ubuntu 22.04+ or Debian 12+) with at least 4GB RAM (Penpot is more resource-hungry than a simple static app — it runs a frontend, backend API, and database)
- Docker and Docker Compose installed
- A domain name (e.g., `design.yourcompany.com`)
- An SMTP server for sending email invitations and notifications (self-hosted Mailcow, Postmark, Resend, or similar)

## Step 1: Get the Penpot Configuration

Penpot provides an official Docker Compose configuration that handles all the services you need. The easiest way to get started is to download their configuration files directly:

```bash
mkdir penpot && cd penpot

# Download the official docker-compose file and config
wget https://raw.githubusercontent.com/penpot/penpot/main/docker/images/docker-compose.yaml

# Download the environment configuration template
wget https://raw.githubusercontent.com/penpot/penpot/main/docker/images/.env -O .env.example
```

Copy the environment template:

```bash
cp .env.example .env
```

## Step 2: Configure the Environment

Open the `.env` file and configure the key variables. Here's what a production setup looks like:

```bash
# Public URI — your domain
PENPOT_PUBLIC_URI=https://design.yourcompany.com

# Database credentials
PENPOT_DATABASE_URL=postgresql://penpot-postgres/penpot
PENPOT_DATABASE_USERNAME=penpot
PENPOT_DATABASE_PASSWORD=your_secure_password_here

# Redis for background jobs
PENPOT_REDIS_URI=redis://penpot-redis/0

# SMTP for email invitations
PENPOT_SMTP_HOST=smtp.yourprovider.com
PENPOT_SMTP_PORT=587
PENPOT_SMTP_USERNAME=your_username
PENPOT_SMTP_PASSWORD=your_password
PENPOT_SMTP_FROM=noreply@yourcompany.com
PENPOT_SMTP_SSL=false
PENPOT_SMTP_TLS=true

# Registration — set to false after initial setup to prevent open signups
PENPOT_REGISTRATION_ENABLED=true

# Demo users — disable in production
PENPOT_DEMO_WARNING=false
```

Generate secure passwords for the database:

```bash
openssl rand -base64 24
```

Use a different strong password for each service. Don't reuse the database password for anything else.

## Step 3: Deploy with Docker Compose

The official `docker-compose.yaml` defines all the services Penpot needs: the frontend, backend API, exporter (for rendering images), PostgreSQL database, and Redis. Start everything up:

```bash
docker compose up -d
```

Check that all services are running:

```bash
docker compose ps
```

You should see five services in the "Up" state:

- `penpot-frontend` (the web UI)
- `penpot-backend` (the API server)
- `penpot-exporter` (renders designs to images for export and thumbnails)
- `penpot-postgres` (the database)
- `penpot-redis` (background job queue)

Check the logs if anything isn't starting:

```bash
docker compose logs -f penpot-backend
```

The backend will run database migrations on first startup. Once you see a "Server started" message, Penpot is ready.

## Step 4: Reverse Proxy with SSL

Put a reverse proxy in front of Penpot to handle SSL and route traffic. If you followed our [Caddy self-hosting guide](/blog/2026/11/10/self-hosting-caddy-the-reverse-proxy-that-makes-https-effortless/), this is a two-line config:

Create or edit your Caddyfile:

```
design.yourcompany.com {
    reverse_proxy localhost:9001
}
```

Penpot's frontend listens on port 9001 by default. Restart Caddy:

```bash
sudo systemctl restart caddy
```

Caddy will automatically provision an SSL certificate from Let's Encrypt and redirect HTTP to HTTPS. Within a minute, your Penpot instance should be accessible at `https://design.yourcompany.com`.

If you prefer Nginx:

```nginx
server {
    listen 80;
    server_name design.yourcompany.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name design.yourcompany.com;

    ssl_certificate /etc/letsencrypt/live/design.yourcompany.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/design.yourcompany.com/privkey.pem;

    client_max_body_size 100m;

    location / {
        proxy_pass http://localhost:9001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

The `Upgrade` and `Connection` headers are important — Penpot uses WebSocket connections for real-time collaboration, and without them you'll lose live cursors and simultaneous editing.

Use `certbot --nginx -d design.yourcompany.com` to provision the SSL certificate.

## Step 5: Create Your First Project

Navigate to your Penpot domain and register an account. The first registered user becomes the administrator.

1. Click **Sign Up** and create your account
2. Click **New File** to create a design file
3. Give it a name (e.g., "Q1 Marketing Mockups")
4. Start designing — use the toolbar on the left for shapes, text, and images

To invite team members:

1. Go to your **Profile** → **Team Settings**
2. Click **Invite Members**
3. Enter email addresses and assign roles (Owner, Editor, or Viewer)
4. Invitees receive an email with a signup link

Set `PENPOT_REGISTRATION_ENABLED=false` in your `.env` file after you've created all the accounts you need. Restart the stack (`docker compose up -d`) to apply the change. This prevents random signups on your instance.

## Step 6: Set Up a Design System

If your team designs more than one-off graphics, a design system saves hours of rework. Penpot supports reusable components and design tokens:

1. Create a file called "Design System" or "Component Library"
2. Design your base components — buttons, cards, headers, form fields
3. Select a component and click **Create Component** in the right panel
4. In other files, use **File → Libraries** to link your design system file
5. Drag components from the library into your working file

When you update a component in the design system file, all linked files automatically receive the update. This is the same workflow as Figma's component libraries, and it works the same way.

## Step 7: Automate with the API

Penpot has a REST API that lets you programmatically access files, pages, and design data. This is where things get interesting for businesses that want design work integrated into their workflows.

A few practical automation ideas:

- **Export designs on a schedule** — use the API to export marketing graphics to a Nextcloud folder every week, so your content team always has the latest versions
- **Sync design assets to a CMS** — when a designer updates a banner mockup, automatically export the SVG and push it to your website
- **Generate design previews for project management** — pull thumbnail previews of Penpot files into your project management tool (Plane, OpenProject) so stakeholders can see progress without opening Penpot

Here's a simple Python example that lists all files in a Penpot project:

```python
import requests

PENPOT_URL = "https://design.yourcompany.com"
API_TOKEN = "your_api_token"  # Generate in Profile → API Tokens

response = requests.get(
    f"{PENPOT_URL}/api/rpc/command/get-all-files",
    headers={
        "Authorization": f"Token {API_TOKEN}",
        "Content-Type": "application/json",
    },
    json={"project-id": "your-project-id"},
)

files = response.json()
for f in files:
    print(f"File: {f['name']} (ID: {f['id']})")
```

Pair this with **n8n** and you can build automated design pipelines:

```
[Trigger: New Penpot file published]
    → [HTTP Request: Export file as SVG via Penpot API]
    → [HTTP Request: Upload SVG to Nextcloud]
    → [Send Mattermost notification to #marketing]
```

## Backup and Maintenance

Self-hosting means you own the backups. Don't skip this.

**Database backups** — set up a daily cron job:

```bash
#!/bin/bash
# /opt/penpot-backup.sh
DATE=$(date +%Y%m%d)
docker exec penpot-penpot-postgres-1 pg_dump -U penpot penpot > /backups/penpot-db-$DATE.sql
# Keep last 30 days
find /backups -name "penpot-db-*.sql" -mtime +30 -delete
```

Add to crontab:

```bash
0 2 * * * /opt/penpot-backup.sh
```

**Asset storage** — Penpot stores uploaded images and rendered exports on disk (in the backend container's data volume). Back up the Docker volume:

```bash
docker run --rm -v penpot_penpot-assets:/data -v /backups:/backup alpine \
  tar czf /backup/penpot-assets-$DATE.tar.gz /data
```

For production, consider using S3-compatible storage (MinIO, Backblaze B2) for off-site backups. We covered a practical disaster recovery approach in our [backup guide for self-hosted stacks](/blog/2026/11/17/backing-up-your-self-hosted-stack-a-practical-disaster-recovery-guide/).

**Updates** — Penpot releases new versions frequently. To update:

```bash
cd penpot
docker compose pull
docker compose up -d
```

Check the [release notes](https://github.com/penpot/penpot/releases) before updating. Always back up the database before applying updates to production.

## Security Checklist

Before going live, run through this list:

- [ ] **SSL/TLS enabled** — use Caddy or Nginx with Let's Encrypt
- [ ] **Firewall configured** — only expose ports 80/443; keep PostgreSQL (5432) and Redis (6379) internal
- [ ] **Strong database password** — at least 24 characters, randomly generated
- [ ] **Registration disabled after setup** — set `PENPOT_REGISTRATION_ENABLED=false`
- [ ] **Demo users removed** — set `PENPOT_DEMO_WARNING=false`
- [ ] **Regular database backups** — automated daily, tested monthly
- [ ] **Asset storage backed up** — S3 or regular volume snapshots
- [ ] **Access restricted** — consider IP allowlisting or VPN for internal-only instances
- [ ] **Updates scheduled** — check for new releases monthly, update quarterly at minimum
- [ ] **User management** — remove inactive users, review team membership regularly

## The Business Case

Let's put real numbers on this. Say you're a 10-person team where 6 people need editor access to design files — three designers, two marketers who create social media graphics, and a product manager who prototypes features.

**Figma Professional** at $15/editor/month for 6 editors = **$1,080/year**

**Self-hosted Penpot:**
- VPS (4GB RAM): $24/month = $288/year
- Domain: $12/year
- Backblaze B2 storage (5GB of design assets): ~$0.25/month = $3/year
- Setup time (one-time): ~2 hours at $100/hour = $200
- Maintenance (4 hours/year): $400
- **Total year 1: $903**
- **Total year 2+: $703/year**

**Annual savings: ~$377 (year 1), ~$377/year ongoing**

The savings look modest at 6 editors, but they scale. At 15 editors (Figma: $2,700/year), Penpot's $703/year cost is the same. At 30 editors (Figma: $5,400/year), you're saving nearly $4,700 annually. And unlike Figma, adding a new editor doesn't increase your bill — it's the same server whether you have 5 editors or 50.

## Integrations Worth Knowing About

Penpot fits naturally into a self-hosted stack:

- **n8n** — automate design exports, file syncing, and notifications via the REST API
- **Nextcloud** — sync exported SVGs and PNGs into shared folders for your whole team
- **Mattermost** — notify channels when designs are updated or commented on
- **BookStack** — embed Penpot prototypes in your internal documentation
- **Gitea** — store SVG design files in a Git repository for version control (since Penpot files are SVG-native, this actually works well)
- **Directus** — use Penpot's API to pull design assets into a headless CMS for your website

## Limitations to Be Aware Of

Penpot is excellent and improving rapidly, but it's not a 1:1 Figma replacement in every scenario:

1. **Plugin ecosystem** — Figma has thousands of plugins for everything from icon libraries to accessibility testing. Penpot has a plugin system, but the library is much smaller. If your workflow depends on specific Figma plugins, check whether Penpot has equivalents before switching.

2. **Dev Mode** — Figma's Dev Mode provides detailed CSS, iOS, and Android code snippets from designs, plus advanced inspection tools. Penpot exports CSS Grid and Flexbox layouts (which is arguably better for web developers), but the overall developer handoff experience isn't as polished.

3. **FigJam** — Figma's whiteboarding tool (FigJam) has no direct Penpot equivalent. If your team relies on collaborative whiteboarding, you'd need a separate tool for that.

4. **Performance on large files** — Figma's rendering engine is highly optimized for files with hundreds of frames. Penpot handles large files well but can feel slower on very complex files with thousands of layers, especially on lower-spec servers.

5. **Learning curve** — Penpot's interface is similar to Figma but not identical. Expect a day or two of adjustment for your team. The core concepts (frames, components, auto-layout) map over, but keyboard shortcuts and some workflows differ.

## Wrapping Up

Penpot has matured into a genuine design platform alternative for businesses that want to escape per-editor SaaS pricing. The self-hosted edition gives you unlimited editors, unlimited files, an open SVG file format, and full data control — all for the cost of a modest VPS.

If you're already self-hosting other tools, adding Penpot to your stack is a natural extension. The Docker setup is well-documented, the resource requirements are reasonable, and the savings compound with every editor you add. And because Penpot stores designs as SVG — an open, human-readable format — your design files are portable in a way that proprietary formats will never be.

The question isn't whether Penpot can replace Figma for every team. It can't, at least not yet. The question is whether the specific features your team actually uses exist in Penpot, and whether the $1,000–$5,000 you're paying Figma every year is buying you capabilities you can't get for free.

For most small and mid-size businesses doing marketing design, prototyping, and brand asset management, the answer is: probably not.

---

*Want help setting up Penpot or integrating it with your existing self-hosted stack? [Contact ARDOT Consulting](/#contact) — we specialize in open source automation for small and mid-size businesses. No hype, no vendor lock-in, just practical solutions that save you money.*
