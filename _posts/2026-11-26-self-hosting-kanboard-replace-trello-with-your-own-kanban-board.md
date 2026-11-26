---
layout: post
title: "Self-Hosting Kanboard: Replace Trello With Your Own Kanban Board"
date: 2026-11-26
author: "ARDOT Consulting"
tags: [kanboard, kanban, trello, self-hosting, project-management, open-source, docker]
excerpt: "Trello's per-seat pricing adds up fast. Kanboard gives you a lightweight, self-hosted Kanban board with WIP limits, automation, and an API, all under the MIT License."
---

If your team uses Trello, you've probably noticed the pricing creeping up. The free plan caps you at 10 collaborators. Standard costs $5 per user per month (billed annually), Premium is $10, and Enterprise hits $17.50. For a 20-person team on Premium, that's $2,400 a year just to move cards across columns.

Trello is a good product. The interface is polished, the mobile app works well, and most people already know how it works. But if your needs are straightforward — visual boards, drag-and-drop tasks, swimlanes, maybe some automation rules — you're paying a per-seat tax for features your team may not use.

Kanboard is the opposite approach. It's a self-hosted Kanban application that does the core job well and stops there. No AI features, no dashboards, no power-up marketplace. Just boards, columns, tasks, and the workflows you build around them. It's distributed under the MIT License, it's been running for over a decade, and it costs whatever you're already paying for a server.

## What Is Kanboard?

[Kanboard](https://kanboard.org/) is a free and open source Kanban project management application. It was created by Frédéric Guillot (also known for creating Miniflux, the self-hosted RSS reader) and has accumulated contributions from over 334 people. The project lives on [GitHub](https://github.com/kanboard/kanboard) with roughly 10,000 stars and 4,800 commits.

The design philosophy is deliberately minimal. The website says it plainly: "There is no fancy user interface, Kanboard focuses on simplicity and minimalism. The number of features is voluntarily limited."

That sounds like a drawback until you've managed a team that spent more time configuring Trello power-ups than doing actual work. Kanboard gives you the essentials and gets out of the way.

### A note on maintenance mode

Kanboard's README states that the application is in maintenance mode. The original author is not actively developing new major features, but community pull requests are accepted and releases continue with bug fixes and community contributions.

For some teams, this is a dealbreaker. For others, it's a feature. A project in maintenance mode means the software is stable, it's not going to redesign its interface next quarter, and your workflows won't break when you update. If you want a kanban board that quietly works for years without churning, Kanboard fits. If you want active feature development, look at Wekan (21,000+ stars, actively developed, MIT-licensed, but heavier on server resources).

## Why Self-Host Your Kanban Board?

**No per-seat pricing.** Trello charges per user. Kanboard charges nothing. Whether you have 5 users or 500, the cost is your server. A $6/month VPS can run Kanboard for a small team. Your existing self-hosted infrastructure can run it alongside everything else for zero additional cost.

**Your data stays on your server.** Trello stores your project data on Atlassian's servers. Kanboard stores everything on yours. For teams handling client projects, internal roadmaps, or anything competitive, keeping that data in-house matters.

**Full control over access.** Kanboard supports LDAP and Active Directory authentication natively. You can connect it to your existing identity infrastructure instead of managing yet another set of logins. OAuth2 is also supported if you'd rather authenticate through GitHub, GitLab, or another provider.

## Feature Comparison: Kanboard vs Trello

| Feature | Kanboard | Trello (Premium) |
|---------|----------|-------------------|
| License | MIT (open source) | Proprietary |
| Kanban boards | Yes | Yes |
| Swimlanes | Yes | Yes |
| WIP limits | Yes (built-in) | Yes (Power-Up required) |
| Drag and drop | Yes | Yes |
| Subtasks | Yes | Yes (checklists) |
| Task attachments | Yes | Yes |
| Comments | Yes (Markdown) | Yes |
| Search and filter | Yes (query language) | Yes |
| Automatic actions | Yes (built-in) | Yes (Butler automation) |
| API | Yes (JSON-RPC) | Yes (REST) |
| Webhooks | Yes | Yes |
| LDAP/AD auth | Yes | No (enterprise SSO only) |
| Self-hosted | Yes | No |
| Per-seat pricing | No | Yes ($5-$17.50/user/month) |
| Mobile app | No (web responsive) | Yes (native iOS/Android) |
| Dashboard/analytics | Limited | Yes |
| AI features | No | Yes |
| Plugin system | Yes | Yes (Power-Ups) |
| Languages | 30+ | 20+ |

The gaps are real. Kanboard doesn't have a native mobile app (the web interface is responsive but not an app). There are no AI features. The analytics are basic. If your team relies on Trello's mobile app or Butler automation heavily, that's worth weighing.

But the core kanban functionality — boards, columns, tasks, swimlanes, WIP limits, search, subtasks, comments, attachments — is all there, and it's all self-hosted.

## Hardware Requirements

Kanboard is lightweight. It's a PHP application with minimal dependencies.

| Team Size | Server Specs | Monthly Cost |
|-----------|-------------|--------------|
| 1-10 users | 1 vCPU, 512MB RAM, SQLite | ~$4-6 |
| 10-50 users | 1 vCPU, 1GB RAM, PostgreSQL | ~$6-12 |
| 50+ users | 2 vCPU, 2GB RAM, PostgreSQL | ~$12-24 |

With SQLite, a $4 VPS is plenty. PostgreSQL adds modest overhead but is still lighter than Wekan, which runs on Node.js and MongoDB.

## Docker Setup: Step by Step

The official Docker image is available on both Docker Hub (`kanboard/kanboard`) and the GitHub Container Registry (`ghcr.io/kanboard/kanboard`). It supports amd64, arm64, arm/v7, and arm/v6 architectures, so it runs on everything from standard x86 servers to Raspberry Pis.

### Step 1: Create the project directory

```bash
mkdir ~/kanboard && cd ~/kanboard
```

### Step 2: Create docker-compose.yml (SQLite)

For small teams, SQLite is the simplest option. No separate database container to manage.

```yaml
version: "3"
services:
  kanboard:
    image: kanboard/kanboard:latest
    container_name: kanboard
    restart: always
    ports:
      - "8080:80"
    volumes:
      - data:/var/www/app/data
      - plugins:/var/www/app/plugins
    environment:
      - PLUGIN_INSTALLER=true

volumes:
  data:
  plugins:
```

### Step 3: Start the container

```bash
docker compose up -d
```

### Step 4: Access the web interface

Open `http://your-server-ip:8080` in your browser. The default credentials are:

- Username: `admin`
- Password: `admin`

**Change the admin password immediately** after logging in. This is the first thing you see in the settings.

### Step 5: Configure a reverse proxy with Caddy

If you're already running [Caddy as your reverse proxy](https://www.ardotconsulting.com/blog/2026/11/10/self-hosting-caddy-the-reverse-proxy-that-makes-https-effortless/), adding Kanboard is one Caddyfile block:

```
kanban.yourdomain.com {
    reverse_proxy localhost:8080
}
```

Reload Caddy and you've got HTTPS automatically. No certbot, no manual certificate management.

### Step 6: Using PostgreSQL instead of SQLite

For teams above 10 users or if you prefer a real database, switch to PostgreSQL:

```yaml
version: "3"
services:
  kanboard:
    image: kanboard/kanboard:latest
    container_name: kanboard
    restart: always
    ports:
      - "8080:80"
    volumes:
      - data:/var/www/app/data
      - plugins:/var/www/app/plugins
    environment:
      DATABASE_URL: postgres://kanboard:kanboard-secret@db/kanboard
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    restart: always
    environment:
      POSTGRES_USER: kanboard
      POSTGRES_PASSWORD: kanboard-secret
      POSTGRES_DB: kanboard
    volumes:
      - db:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "kanboard"]
      interval: 10s
      timeout: 5s

volumes:
  data:
  plugins:
  db:
```

Change the password to something strong before deploying.

## Key Features in Practice

### Work-in-Progress Limits

WIP limits are Kanboard's strongest feature for teams that struggle with context switching. Set a column limit of 3, and when a fourth task enters the column, the entire column highlights in red. It's a simple visual cue that someone needs to finish work before starting more.

This is built into Kanboard natively. In Trello, you need a Power-Up for the same functionality.

### Automatic Actions

Kanboard has a built-in rule engine for automating repetitive actions. No scripting required. You define triggers and actions through the web UI:

- When a task moves to "Done" → automatically assign it to the reporter
- When a task is created in "Backlog" → set priority to low
- When a task is overdue → move it to "Urgent"
- When a task is closed → send an email notification

These are simple if-then rules, but they cover most of the repetitive actions teams want to automate. The interface is a form, not a scripting language, so non-technical team members can create rules.

### Search and Filter

Kanboard includes a query language for finding tasks. You can filter by assignee, category, due date, priority, status, or any combination:

```
assignee:me AND status:open AND due:<tomorrow
```

This shows all tasks assigned to you that are open and due before tomorrow. The query syntax is documented in the [official docs](https://docs.kanboard.org/). It's more powerful than Trello's basic search, though less flexible than a full database query.

### JSON-RPC API

Kanboard exposes a [JSON-RPC API](https://docs.kanboard.org/v1/api/) that covers nearly every operation: creating tasks, moving tasks, managing projects, listing users, adding comments. The API uses token-based authentication.

This is where Kanboard fits into the broader self-hosted automation stack. You can connect it to n8n to build workflows that go beyond the built-in automatic actions.

## Connecting Kanboard to n8n

Kanboard's JSON-RPC API lets you integrate it with [n8n](https://www.ardotconsulting.com/blog/2026/08/17/how-to-build-your-first-ai-automation-workflow-with-n8n/) for more complex automation. Some practical examples:

**New client → new project board.** When a new client signs on (captured via [OpnForm](https://www.ardotconsulting.com/blog/2026/11/01/self-hosting-opnform-replace-typeform-with-your-own-form-builder/)), an n8n workflow calls the Kanboard API to create a project, sets up columns, and adds team members.

**Overdue task → Mattermost alert.** An n8n workflow runs hourly, queries Kanboard for overdue tasks, and posts a summary in a dedicated [Mattermost](https://www.ardotconsulting.com/blog/2026/10/08/self-hosting-mattermost-replace-slack-with-your-own-team-chat-platform/) channel.

**Completed task → time log.** When a task moves to Done, n8n reads subtask time estimates and logs them in [Kimai](https://www.ardotconsulting.com/blog/2026/11/27/self-hosting-kimai-replace-toggl-and-harvest-with-your-own-time-tracking-platform/) for client billing.

Here's a basic API call from n8n using the HTTP Request node:

```
POST http://your-kanboard-url/jsonrpc.php
Content-Type: application/json
X-API-Auth: your-api-token

{
  "jsonrpc": "2.0",
  "method": "createTask",
  "id": 1,
  "params": {
    "project_id": 1,
    "title": "Review Q4 proposal",
    "column_id": 1,
    "owner_id": 2
  }
}
```

The API documentation lists every available method. Authentication uses a personal API token generated from your user profile.

## Security Checklist

- [ ] Change the default admin password immediately after first login
- [ ] Enable HTTPS via Caddy or another reverse proxy (never expose port 80 directly)
- [ ] Restrict access with a firewall (only allow your VPN or office IP range)
- [ ] Use a strong database password if running PostgreSQL
- [ ] Disable user registration if you don't need public sign-up
- [ ] Enable LDAP or OAuth2 authentication instead of local accounts for larger teams
- [ ] Set up regular database backups (see our [disaster recovery guide](https://www.ardotconsulting.com/blog/2026/11/17/backing-up-your-self-hosted-stack-a-practical-disaster-recovery-guide/))
- [ ] Pin your Docker image to a specific version (e.g., `kanboard/kanboard:v1.2.40`) instead of `latest` to avoid unexpected updates

## Cost Comparison

| Tool | 10 users | 20 users | 50 users | Annual (20 users) |
|------|----------|----------|----------|-------------------|
| Trello Free | $0 | $0 | Not available | $0 |
| Trello Standard | $50/mo | $100/mo | $250/mo | $1,200 |
| Trello Premium | $100/mo | $200/mo | $500/mo | $2,400 |
| Trello Enterprise | $175/mo | $350/mo | $875/mo | $4,200 |
| Kanboard (self-hosted) | ~$6/mo | ~$6/mo | ~$12/mo | $72-$144 |

The Trello Free plan caps at 10 collaborators, so any team larger than that is on a paid plan. For a 20-person team on Trello Premium, switching to Kanboard saves over $2,200 per year. Even compared to Standard, the savings are around $1,100 annually.

The trade-off is that someone needs to maintain the Kanboard instance. Updates, backups, and occasional troubleshooting are on you. If you value your time at $50/hour and spend 2 hours per month on maintenance, that's $100/month in labor. Kanboard still comes out ahead, but the calculation isn't zero.

**You need a native mobile app.** Kanboard's web interface is responsive and works on mobile browsers, but it's not a native app. If your team works primarily from phones, this is a real limitation. Trello's mobile app is genuinely good.

**You need rich reporting.** Kanboard has basic analytics (cumulative flow diagram, task distribution). If your stakeholders need burndown charts, velocity tracking, or custom dashboards, you'll need to export data and build those elsewhere. Tools like [Metabase](https://www.ardotconsulting.com/blog/2026/09/30/self-hosting-metabase-open-source-business-analytics-without-saas/) can fill this gap by querying Kanboard's PostgreSQL database directly.

**You want actively developed software.** Kanboard is in maintenance mode. It works, it's stable, bugs get fixed, but new features are rare. If your team wants a product that's continuously evolving, [Wekan](https://github.com/wekan/wekan) (MIT-licensed, 21,000+ stars, actively developed) is the better choice, though it needs more server resources (Node.js + MongoDB vs. PHP + SQLite).

**You need Gantt charts or timeline views.** Kanboard is kanban-only. No Gantt charts, no calendar view (beyond iCalendar export), no timeline. If your projects need multiple visualizations, consider [OpenProject](https://www.ardotconsulting.com/blog/2026/10/14/open-source-project-management-tools-that-replace-asana/) which covers kanban, Gantt, and time tracking in one tool.

## Integrations With Other Self-Hosted Tools

Kanboard fits naturally into a self-hosted stack:

- **Kanboard + n8n**: API-driven automation for complex workflows that go beyond the built-in rules
- **Kanboard + Mattermost**: Webhook notifications when tasks move between columns
- **Kanboard + Kimai**: Log time spent on tasks for client billing
- **Kanboard + Caddy**: Automatic HTTPS with a simple reverse proxy config
- **Kanboard + Metabase**: Query the Kanboard database for custom analytics and reporting
- **Kanboard + Vaultwarden**: Share API tokens and credentials securely across your team

## Migration From Trello

If you're moving from Trello to Kanboard, here's a practical transition plan:

1. **Export your Trello boards.** Trello supports JSON export from the board menu.
2. **Recreate board structures in Kanboard.** Create projects with matching column names. There's no direct Trello import, so this is manual for a few boards.
3. **Use the API for bulk task creation.** Write a script or n8n workflow that reads your Trello JSON export and creates tasks via the Kanboard JSON-RPC API.
4. **Set up authentication.** Connect Kanboard to your LDAP/AD or OAuth2 provider so users keep their existing credentials.
5. **Run both in parallel for a week.** Keep Trello active during the transition, then archive boards and cancel the subscription.

For small teams with 2-3 boards, the migration takes about an hour. For larger setups with dozens of boards, the API approach is worth the investment.

## Wrapping Up

Kanboard isn't trying to compete with Trello on features. It's trying to do the opposite: provide a stable, minimal kanban board that you host yourself, with no per-seat pricing, no vendor lock-in, and no feature bloat. For teams that have outgrown Trello's free tier and don't need the premium features, it's a clean replacement.

The worst case is that you spend an hour setting it up, realize your team needs native mobile apps or AI features, and go back to Trello. The best case is that you stop paying $100+ per month for a tool whose core functionality — moving cards across columns — Kanboard provides for free.

Start with one board, invite a few team members, and see if the simplicity works for your workflow. If it does, you've just removed another SaaS subscription from your monthly bill.

---

*Want help setting up Kanboard or migrating from Trello? [Get in touch](https://www.ardotconsulting.com/#contact) — we help small businesses replace SaaS subscriptions with self-hosted open source alternatives.*
