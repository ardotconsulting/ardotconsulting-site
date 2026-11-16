---
layout: post
title: "Self-Hosting Flame Dashboard: Centralize Access to All Your Self-Hosted Tools"
date: 2027-01-16
author: "ARDOT Consulting"
tags: [flame, dashboard, startpage, self-hosting, docker, open-source]
excerpt: "Flame is a lightweight open-source startpage that turns your growing collection of self-hosted tools into one clean, searchable dashboard — here's how to deploy it with Docker."
---

So you've been on the self-hosting journey. You've got n8n handling your automations, Plausible tracking your website analytics, Odoo running your CRM, and maybe Metabase for business dashboards. That's great — but now you have fifteen browser bookmarks, half of them with IP addresses and port numbers you can never remember, and your team keeps asking "what was the URL for the time tracker again?"

This is the problem Flame solves. It's a self-hosted startpage — a single dashboard that lives on your server and gives you a clean, visual hub for every tool and service you run. No more bookmark sprawl. No more texting a colleague the link to Cal.com at 9 PM. One page, all your apps, searchable and organized.

## What Is Flame?

[Flame](https://github.com/pawelmalak/flame) is an open-source startpage for your server, created by Pawel Malak and licensed under the MIT license. It's built with React and Node.js, uses SQLite for data storage (no external database required), and runs in a single Docker container. With over 6,700 stars on GitHub, it's one of the most popular self-hosted dashboard options available.

Think of it as a personal landing page for your infrastructure. When you open your browser, instead of a blank tab or a search engine, you see a grid of icons — each one linking directly to one of your self-hosted services. Click the n8n icon, you're in n8n. Click the Plausible icon, you're looking at your analytics. It's that simple.

### Key Features

- **Built-in GUI editors**: Add, edit, and delete applications and bookmarks directly from the interface — no config file editing required
- **Pin favorites**: Keep your most-used tools front and center on the homescreen
- **Integrated search bar**: Search through your apps and bookmarks locally, or use one of 11 built-in web search providers (including DuckDuckGo, Brave, and Startpage)
- **Authentication**: Password-protect your dashboard so only authorized users can see and modify your service links
- **Custom themes**: 15 built-in color themes, a custom theme builder, and support for custom CSS
- **Weather widget**: Optional widget showing current temperature and conditions
- **Docker integration**: Automatically discovers and adds containers based on Docker labels — no manual entry needed
- **Kubernetes integration**: Same auto-discovery for K8s ingress resources

## Why a Dashboard Matters for Small Business

If you're running two or three self-hosted tools, you might think a dashboard is overkill. But self-hosting has a way of growing. You start with one tool, discover the benefits, add another, and before long you're managing a stack of services across multiple ports and subdomains.

Here's what happens without a central dashboard:

| Problem | Impact |
|---------|--------|
| Bookmark sprawl | Team members can't find service URLs |
| Onboarding friction | New employees need a guided tour of "where everything lives" |
| Port confusion | `:3000` for n8n, `:8080` for Odoo, `:5005` for Flame itself — nobody remembers |
| No visual overview | You forget which tools you even have running |

A dashboard like Flame solves all of these. It's also useful as a browser homepage — set it as the default new-tab page across your organization, and everyone starts from the same place every time.

## Flame vs Other Self-Hosted Dashboards

Flame isn't the only option in this space. Here's how it compares to two popular alternatives:

| Feature | Flame | Heimdall | Homer |
|---------|-------|----------|-------|
| License | MIT | MIT | Apache 2.0 |
| Data storage | SQLite | SQLite/MySQL | YAML config file |
| GUI editor | Yes (built-in) | Yes (built-in) | No (edit YAML) |
| Docker auto-discovery | Yes | Yes | No |
| Authentication | Yes | Yes | No (basic auth via reverse proxy) |
| Custom themes | 15 built-in + builder | Yes | CSS customization |
| Search bar | Yes (11 providers) | No | No |
| Resource footprint | Very light | Light | Very light |
| Kubernetes support | Yes | No | No |

Flame hits a sweet spot: it's lightweight enough to run alongside everything else, but feature-complete enough that you don't feel like you're missing out. The built-in search bar is a standout feature — it means your dashboard doubles as a quick-launch command bar.

## Prerequisites

Before you start, you'll need:

- A server running Docker and Docker Compose (any Linux VPS works — even a $5/month instance)
- A domain or subdomain pointing to your server (optional but recommended — use a reverse proxy like [Caddy](https://caddyserver.com/) for HTTPS)
- About 10 minutes

## Step 1: Create the Docker Compose File

Create a directory for Flame and add a `docker-compose.yml` file:

```bash
mkdir -p ~/flame
cd ~/flame
```

Now create `docker-compose.yml`:

```yaml
version: '3.6'

services:
  flame:
    image: pawelmalak/flame
    container_name: flame
    volumes:
      - ./data:/app/data
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - 5005:5005
    environment:
      - PASSWORD=your_secure_password_here
    restart: unless-stopped
```

A few things to note about this configuration:

- **`./data:/app/data`**: This mounts a local directory for persistent storage. Flame stores all its data — apps, bookmarks, themes, settings — in SQLite. If you ever need to update or recreate the container, your data survives.
- **`/var/run/docker.sock:/var/run/docker.sock`**: This gives Flame access to the Docker API so it can auto-discover your other containers. This is optional but highly recommended — it's what makes Flame feel magical.
- **`PASSWORD`**: Sets the authentication password. Anyone accessing the dashboard will need this to view and edit your apps. You can also use Docker secrets (`PASSWORD_FILE`) for a more secure setup.

### Using Docker Secrets (More Secure)

If you prefer not to put your password in plaintext in the compose file:

```yaml
version: '3.6'

services:
  flame:
    image: pawelmalak/flame
    container_name: flame
    volumes:
      - ./data:/app/data
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - 5005:5005
    secrets:
      - password
    environment:
      - PASSWORD_FILE=/run/secrets/password
    restart: unless-stopped

secrets:
  password:
    file: ./secrets/flame_password
```

Then create the secrets file:

```bash
mkdir -p ./secrets
echo "your_secure_password_here" > ./secrets/flame_password
chmod 600 ./secrets/flame_password
```

## Step 2: Start Flame

```bash
docker compose up -d
```

That's it. Flame is now running on port 5005. Open `http://your-server-ip:5005` in your browser, and you'll see the Flame startpage.

You'll be prompted to authenticate. Use the password you set in the compose file. Once logged in, you can start adding your apps and bookmarks.

## Step 3: Add Your Applications Manually

Click the toggle button in the top right corner to enter edit mode, then click "Add Application." For each app, you'll provide:

- **Name**: e.g., "n8n Automation"
- **URL**: e.g., `https://n8n.yourdomain.com` or `http://your-server-ip:5678`
- **Icon**: Choose from Flame's built-in icon library (it includes icons for most popular self-hosted tools)
- **Description**: Optional, but helpful for your team

Organize apps into categories (Flame calls them "categories" — think of them as folders on your dashboard). For example:

| Category | Apps |
|----------|------|
| Automation | n8n, Huginn |
| Analytics | Plausible, Metabase |
| CRM & ERP | Odoo, ERPNext |
| Communication | Mattermost, Listmonk |
| Productivity | Cal.com, BookStack |
| Infrastructure | Uptime Kuma, Grafana |

You can also pin your most-used apps to the homescreen so they appear at the top, above the categorized grid.

## Step 4: Enable Docker Auto-Discovery (The Magic Feature)

Here's where Flame shines. If you mounted the Docker socket (as in our compose file above), Flame can automatically discover your running containers and add them as applications — no manual entry needed.

To make a container appear in Flame, add these labels to any service in its `docker-compose.yml`:

```yaml
labels:
  - flame.type=application
  - flame.name=My Automation Server
  - flame.url=https://n8n.yourdomain.com
  - flame.icon=n8n
```

When Flame detects a container with these labels, it automatically creates an entry on your dashboard. If you stop or remove the container, Flame keeps the entry (it doesn't auto-delete) so you maintain control.

You can even register multiple apps from a single container using semicolons:

```yaml
labels:
  - flame.type=application
  - flame.name=Odoo CRM;Odoo Website
  - flame.url=https://odoo.yourdomain.com;https://site.yourdomain.com
  - flame.icon=odoo;odoo
```

To enable this feature, go to **Settings > Docker** in Flame and toggle on "Use Docker API." Flame will scan your running containers and import anything with the right labels.

## Step 5: Add HTTPS with a Reverse Proxy

Running Flame on a raw port is fine for internal use, but if you want to access it from outside your network (or just want proper HTTPS), put it behind a reverse proxy. [Caddy](https://caddyserver.com/) is the easiest option — it handles TLS certificates automatically.

Here's a minimal `Caddyfile` for Flame:

```caddyfile
dashboard.yourdomain.com {
    reverse_proxy localhost:5005
}
```

That's the entire configuration. Caddy obtains and renews the Let's Encrypt certificate automatically. No manual certbot, no cron jobs, no renewal scripts.

If you already have Caddy managing other services, just add this block to your existing `Caddyfile` and reload:

```bash
caddy reload --config /path/to/Caddyfile
```

Now you can access your dashboard at `https://dashboard.yourdomain.com`.

## Step 6: Set Flame as Your Browser Homepage

The whole point of a startpage is, well, starting there. Set Flame as your browser's homepage or new-tab page:

- **Firefox**: Settings > Home > Homepage and new windows > Custom URL > `https://dashboard.yourdomain.com`
- **Brave/Chromium**: Settings > On startup > Open a specific page > `https://dashboard.yourdomain.com`

For team-wide deployment, configure this via your organization's device management policy so every browser starts at the dashboard.

## Customizing the Look

Flame ships with 15 built-in color themes, and you can create your own with the custom theme builder. Go to **Settings > Other > Theme** to pick one, or use **Settings > Custom CSS** to override anything you don't like.

You can also reorder categories, rename them, and choose which apps are pinned to the homescreen. The goal is a dashboard that matches how your team actually thinks about your tools.

## The Search Bar: More Than Just App Search

Flame's search bar does double duty. By default, it filters your apps and bookmarks as you type — start typing "n8" and the n8n icon highlights. But you can also use it as a web search launcher with prefixes:

| Prefix | Engine |
|--------|--------|
| `/dd` | DuckDuckGo |
| `/b` | Brave Search |
| `/sp` | Startpage |
| `/yt` | YouTube |
| `/gh` | GitHub |

Type `/dd self-hosted accounting tools` and you're searching DuckDuckGo. You can add custom search providers in the settings too.

## Backing Up Flame

Since Flame stores everything in SQLite inside the `./data` volume, backing up is trivial:

```bash
# Simple backup
cp -r ~/flame/data ~/backups/flame-$(date +%Y%m%d)

# Or add it to your existing backup cron job
0 2 * * * tar czf /backups/flame-$(date +\%Y\%m\%d).tar.gz /home/user/flame/data
```

If you ever need to restore, just copy the `data` directory back and restart the container.

## Resource Usage

Flame is remarkably lightweight. In typical usage, the container uses:

- **RAM**: ~50-80 MB
- **CPU**: Negligible (near 0% when idle)
- **Disk**: < 50 MB for the container image, negligible for data

For comparison, running Flame alongside your other tools adds less overhead than a single browser tab. There's no reason not to run it.

## When Flame Is (and Isn't) the Right Choice

**Flame is right for you if:**

- You run 3+ self-hosted services and want a central hub
- You want a visual, searchable dashboard without editing config files
- You use Docker and want auto-discovery of your containers
- You need authentication to protect your service list

**Consider alternatives if:**

- You want a dashboard that also monitors service health (look at [Uptime Kuma](https://github.com/louislam/uptime-kuma) for monitoring, and use Flame alongside it)
- You need multi-user roles and permissions (Flame has a single password, not user accounts)
- You prefer YAML config over a GUI (check out [Homer](https://github.com/bastienwirtz/homer))

For most small businesses building a self-hosted stack, Flame is the simplest way to bring order to the chaos of URLs and port numbers.

## The Bigger Picture: Self-Hosted Infrastructure as a Strategy

Flame is a small tool, but it represents something important about the self-hosting approach: when you own your infrastructure, you can build exactly the workflow you need. A SaaS dashboard product would charge per user, limit customization, and add another subscription to your monthly bill. Flame costs nothing, runs on hardware you already have, and gives you complete control over how your tools are organized.

This is the same philosophy behind every tool we've covered in this series — from n8n for automation to Plausible for analytics to Odoo for CRM. Each one replaces a SaaS subscription with a self-hosted alternative that you control. Flame is the glue that holds it all together, the launchpad that makes your self-hosted stack feel like a cohesive platform instead of a scattered collection of services.

## Getting Started

If you've been following along with our self-hosting guides, adding Flame takes about 10 minutes and immediately makes your entire stack more usable. If you're new to self-hosting and wondering where to start, that's exactly what we help with.

**Ready to centralize your self-hosted infrastructure?** [Get in touch with ARDOT Consulting](/) — we help small businesses design, deploy, and manage open-source tool stacks that replace expensive SaaS subscriptions with tools you own and control.
