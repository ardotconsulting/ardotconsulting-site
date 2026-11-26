---
layout: post
title: "Self-Hosting Gitea: Your Own Git Hosting for Private Code and Documents"
date: 2027-01-22
author: "ARDOT Consulting"
tags: [gitea, git, self-hosting, open-source, version-control, docker, github-alternative]
excerpt: "GitHub's per-seat pricing and private repository limits add up for small teams. Gitea is a lightweight, open source Git hosting platform you can self-host — unlimited private repos, full control, and no monthly subscription. Here's how to set it up and when it makes sense."
---

# Self-Hosting Gitea: Your Own Git Hosting for Private Code and Documents

If your business writes any kind of code — custom scripts, automation workflows, website templates, configuration files — you're probably using GitHub. And if you have more than a few collaborators, you're likely paying for it. GitHub's Team plan runs $4 per user per month, which sounds reasonable until you add contractors, part-time developers, and the operations manager who just needs read access to one repository. Suddenly you're paying $50–100/month for what is, at its core, file storage with version tracking.

There's also the matter of where your code lives. GitHub is a third-party service. Your private repositories — your custom business logic, your integration scripts, your internal tooling — sit on someone else's servers, governed by someone else's terms of service. For many businesses that's fine. But if you're in a regulated industry, if you're handling proprietary algorithms, or if you simply want full control over your infrastructure, it's worth knowing there's an alternative.

**Gitea** is a lightweight, open source Git hosting platform that you can run on your own server. It gives you a web interface for managing Git repositories, user accounts, pull requests, issues, and wiki pages — much of what GitHub offers, but on infrastructure you control, with unlimited private repositories and no per-seat fees.

Let's walk through what Gitea is, how it compares to GitHub, and how to get it running on your own infrastructure.

## What Is Gitea?

Gitea is a self-hosted Git service written in Go. It's a community-driven fork of Gogs, another open source Git platform, and it's been in active development since 2016. The project has over 45,000 stars on GitHub (yes, the irony is not lost on anyone) and a thriving community of contributors. It's licensed under the **MIT license**, one of the most permissive open source licenses available — you can use, modify, distribute, and even sell it without restriction.

Gitea is designed to be lightweight. The entire application is a single Go binary that runs in about 50–100 MB of RAM. Compare that to GitLab Community Edition, which needs 4+ GB of RAM and a fairly beefy server just to start up. If you've ever tried to self-host GitLab on a small VPS and watched it fall over, Gitea is the answer to that problem.

Key features include:

- **Repository management** — create, fork, and organize unlimited public and private repositories
- **Web interface** — browse code, view diffs, blame, commits, branches, and tags through a clean web UI
- **Issues and pull requests** — built-in issue tracker with labels, milestones, assignees, and Kanban-style project boards
- **Wiki pages** — each repository can have its own wiki for documentation
- **Code reviews** — comment on pull requests, request changes, approve merges
- **CI/CD integration** — native support for Gitea Actions (a GitHub Actions-compatible runner) or integration with external CI tools via webhooks
- **Organizations and teams** — group repositories under organizations with granular team-based permissions
- **OAuth2 provider** — use Gitea as an identity provider for your other self-hosted tools (Mattermost, BookStack, n8n, and others support OAuth2 login via Gitea)
- **Package registry** — host your own npm, PyPI, Docker, Composer, and other package types alongside your code
- **API** — full REST API and webhooks for automation

## Gitea vs GitHub: A Practical Comparison

Before you switch, let's be honest about what you're giving up and what you're gaining.

| Feature | GitHub (Team) | Gitea (Self-Hosted) |
|---------|---------------|---------------------|
| **Monthly cost** | $4/user/month | Server cost only (~$5–10/month) |
| **Private repositories** | Unlimited (paid plan) | Unlimited |
| **User limits** | Per-seat pricing | Unlimited |
| **Issue tracking** | Yes (advanced) | Yes (solid, simpler) |
| **Pull requests / code review** | Yes | Yes |
| **CI/CD** | GitHub Actions (generous free tier) | Gitea Actions (self-hosted runners) |
| **Package registry** | Yes | Yes |
| **Wiki** | Yes (GitHub Wikis) | Yes (per-repo wiki) |
| **Mobile app** | Yes | No (web UI works on mobile) |
| **Community / social features** | Large network effect | Your instance only |
| **Setup time** | Zero (signup) | ~30 minutes |
| **Maintenance** | Zero | Occasional updates (5 min/month) |
| **Data control** | Files on GitHub's servers | Files on your server |

The biggest trade-off is the **network effect**. GitHub is where the open source world lives. If your team contributes to public open source projects, you'll still need a GitHub account for that. Gitea isn't trying to replace GitHub for public open source collaboration — it's replacing it for your private, internal code hosting where the network effect doesn't matter.

The second trade-off is **maintenance**. With GitHub, updates and security patches are someone else's problem. With Gitea, you're responsible for updating the software. In practice, this means running a single Docker command every few months. It's not hard, but it's a task that needs an owner.

## When Gitea Makes Sense (and When It Doesn't)

**Gitea is a good fit if:**

- You have a small team (2–50 people) writing code, scripts, or configuration files
- You want unlimited private repositories without per-seat costs
- You're already self-hosting other tools (Nextcloud, Mattermost, n8n) and want to consolidate
- You're in a regulated industry and need full control over where your code is stored
- You want a single sign-on identity provider for your self-hosted stack (Gitea's OAuth2)
- You're comfortable with basic Docker and server administration

**Stick with GitHub if:**

- Your team actively contributes to public open source projects and relies on GitHub's social features
- You have zero appetite for server maintenance, even minimal
- You heavily depend on GitHub-specific features like GitHub Copilot, GitHub Codespaces, or Advanced Security
- Your team is very small (1–2 people) and the free tier covers your needs

## What You'll Need

A Gitea deployment is refreshingly minimal:

- **A Linux server** — any VPS with 1 GB RAM and 10 GB disk space. Gitea runs fine on a $5/month VPS from Hetzner, OVH, or DigitalOcean.
- **Docker and Docker Compose** — for easy installation and updates
- **A domain name** — something like `git.yourcompany.com`
- **An SSL certificate** — handled automatically by Caddy or Traefik (see our [Caddy setup guide](https://www.ardotconsulting.com/blog/2026/11/10/self-hosting-caddy-the-reverse-proxy-that-makes-https-effortless/))

If you're already running a self-hosted stack, you likely have all of this already. Gitea fits neatly alongside Nextcloud, Mattermost, and the rest.

## Setting Up Gitea with Docker

Here's a practical setup using Docker Compose. This assumes you have Docker installed and a reverse proxy (Caddy, Traefik, or Nginx) handling SSL for your domain.

### Step 1: Create the Docker Compose File

Create a directory for Gitea and add a `docker-compose.yml` file:

```yaml
version: "3"

networks:
  gitea:
    external: false

services:
  gitea:
    image: gitea/gitea:latest
    container_name: gitea
    environment:
      - USER_UID=1000
      - USER_GID=1000
      - GITEA__server__DOMAIN=git.yourcompany.com
      - GITEA__server__ROOT_URL=https://git.yourcompany.com/
      - GITEA__database__DB_TYPE=postgres
      - GITEA__database__HOST=gitea-db:5432
      - GITEA__database__NAME=gitea
      - GITEA__database__USER=gitea
      - GITEA__database__PASSWD=change_this_to_a_strong_password
    volumes:
      - ./gitea-data:/data
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    ports:
      - "3000:3000"   # Web UI
      - "2222:22"     # SSH for git operations
    networks:
      - gitea
    depends_on:
      - gitea-db
    restart: unless-stopped

  gitea-db:
    image: postgres:16
    container_name: gitea-db
    environment:
      - POSTGRES_USER=gitea
      - POSTGRES_PASSWORD=change_this_to_a_strong_password
      - POSTGRES_DB=gitea
    volumes:
      - ./postgres-data:/var/lib/postgresql/data
    networks:
      - gitea
    restart: unless-stopped
```

A few things worth noting:

- **The `2222:22` port mapping** maps Gitea's internal SSH port to port 2222 on your host. This avoids conflicts with your server's own SSH daemon (which runs on port 22). Your team will clone repositories using `git clone ssh://git@git.yourcompany.com:2222/org/repo.git`.
- **PostgreSQL** is used here instead of SQLite. Gitea supports SQLite for small setups, but PostgreSQL is more robust for teams. If you're just testing, you can switch to SQLite by removing the `gitea-db` service and changing `DB_TYPE` to `sqlite3`.
- **The `gitea-data` volume** stores your repositories, configuration, and uploaded files. Back this up regularly (see our [disaster recovery guide](https://www.ardotconsulting.com/blog/2026/11/17/backing-up-your-self-hosted-stack-a-practical-disaster-recovery-guide/)).

### Step 2: Start Gitea

```bash
docker compose up -d
```

Wait about 30 seconds for the database to initialize. Then visit `https://git.yourcompany.com` (assuming your reverse proxy is configured) and you'll see Gitea's setup page.

### Step 3: Complete the Web Setup

The first time you visit Gitea, it shows an installation page. Most settings are pre-filled from your environment variables. The key things to configure:

1. **Database settings** — should already be filled in from your `docker-compose.yml`
2. **General settings** — confirm the domain and root URL are correct
3. **Administrator account** — create your admin user. This is the account you'll use to manage organizations, teams, and system settings.

Click **Install Gitea**, and you're done. You now have a fully functional Git hosting platform.

### Step 4: Configure Your Reverse Proxy

If you're using **Caddy**, add this to your Caddyfile:

```
git.yourcompany.com {
    reverse_proxy localhost:3000
}
```

Caddy automatically provisions and renews SSL certificates. Reload Caddy (`caddy reload`), and your Gitea instance is accessible over HTTPS.

If you're using **Nginx**, a basic server block looks like:

```nginx
server {
    listen 80;
    server_name git.yourcompany.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name git.yourcompany.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

For SSH access (cloning over SSH), make sure port 2222 is open on your server's firewall.

## Migrating from GitHub

If you already have repositories on GitHub and want to move them to Gitea, the process is straightforward. Gitea has a built-in migration tool.

1. **Create a personal access token** on GitHub (Settings → Developer settings → Personal access tokens) with `repo` scope.
2. In Gitea, click the **+** icon (top right) → **New Migration** → **GitHub**.
3. Enter the GitHub repository URL and your access token.
4. Gitea pulls the repository, including issues, labels, milestones, and pull requests.

You can migrate repositories one at a time or use Gitea's API to batch-migrate an entire organization. The migration preserves commit history, branches, tags, and issues.

One thing that doesn't migrate cleanly: **pull request reviews and comments**. Gitea imports the pull requests themselves, but review threads may not transfer perfectly. For most small teams, this is a minor issue — you're migrating internal code, not a public project with years of discussion history.

## Setting Up Organizations and Teams

Once Gitea is running, organize your repositories with organizations and teams. This mirrors how GitHub Organizations work.

**Create an organization** (e.g., `yourcompany`) and group repositories under it. Then create teams within that organization:

- **Developers** — read/write access to all repositories
- **Operations** — read access to infrastructure repos, write access to deployment scripts
- **Contractors** — read access to specific repositories only
- **Managers** — read access to everything, no write access

This gives you fine-grained control over who can see and modify what. When a contractor leaves, you remove them from the team. When a new employee joins, you add them to the appropriate teams. No per-seat billing, no license management.

## Using Gitea as an OAuth2 Provider

One of Gitea's most valuable features for a self-hosted stack is its **OAuth2 provider**. Instead of managing separate logins for Mattermost, BookStack, n8n, and every other tool you self-host, you can use Gitea as a central identity provider.

Here's the pattern:

1. Users have one account in Gitea.
2. Each self-hosted tool (Mattermost, BookStack, n8n, Outline, etc.) is configured to use Gitea OAuth2 for login.
3. When a user visits any tool, they're redirected to Gitea to authenticate.
4. Gitea sends back a token confirming their identity.
5. The tool logs them in.

When someone leaves the company, you disable their Gitea account. They instantly lose access to every connected tool. No hunting through five different admin panels.

To set this up, go to **Site Administration → OAuth2 Applications** in Gitea and create a new OAuth2 application for each tool. Gitea gives you a client ID and client secret, which you plug into the tool's authentication settings.

## Automating Gitea with n8n

Gitea has a full REST API, which means you can automate it with n8n. Here are practical workflows:

**Auto-create repositories for new projects.** When a new project is created in your project management tool (Odoo, NocoDB, or even a form submission in OpnForm), an n8n workflow calls the Gitea API to create a repository, sets up default labels, creates an initial README, and adds the project team.

**Sync issue labels across repositories.** If you want consistent labels (bug, feature, priority-high) across all repositories, an n8n workflow can enforce that. When a label is added or renamed in your "template" repository, the workflow syncs the change to every other repo.

**Notify on pull requests.** When a pull request is opened in Gitea, a webhook triggers an n8n workflow that posts a summary to your Mattermost channel, assigns a reviewer based on the repository's team configuration, and creates a calendar entry for review.

**Archive stale repositories.** A scheduled n8n workflow checks for repositories with no commits in 6 months, opens an issue suggesting archival, and after 30 days of no response, archives the repository to keep your organization clean.

Here's a simple n8n HTTP Request node for creating a repository via the Gitea API:

```json
{
  "method": "POST",
  "url": "https://git.yourcompany.com/api/v1/orgs/yourcompany/repos",
  "headers": {
    "Authorization": "token YOUR_GITEA_API_TOKEN",
    "Content-Type": "application/json"
  },
  "body": {
    "name": "new-project-website",
    "description": "Marketing website for the Q1 product launch",
    "private": true,
    "auto_init": true,
    "default_branch": "main"
  }
}
```

## Backing Up Gitea

Gitea stores everything — repositories, database, configuration, uploaded attachments — in its data directory and database. A complete backup requires both.

**For the data directory**, back up the `./gitea-data` folder (or wherever you mounted `/data`). This contains your Git repositories in plain `.git` format, so even if Gitea itself breaks, you can always access your code directly with standard Git tools.

**For the database**, use `pg_dump`:

```bash
docker exec gitea-db pg_dump -U gitea gitea > gitea-db-backup.sql
```

Store both backups off-site. Our [disaster recovery guide](https://www.ardotconsulting.com/blog/2026/11/17/backing-up-your-self-hosted-stack-a-practical-disaster-recovery-guide/) covers a complete backup strategy using restic and off-site storage.

## Keeping Gitea Updated

Gitea releases new versions roughly every 3–4 months. Updates are straightforward:

```bash
docker compose pull
docker compose up -d
```

Docker pulls the latest image and restarts the container. Gitea handles database migrations automatically on startup. The whole process takes about 60 seconds.

Before updating, take a backup. After updating, verify the web UI loads and you can clone a repository. If something breaks, you can roll back by specifying the previous version tag in your `docker-compose.yml` (e.g., `gitea/gitea:1.21` instead of `latest`).

## The Cost Picture

Let's talk numbers. Here's what a year of Gitea looks like compared to GitHub Teams:

| Item | GitHub (10 users) | Gitea (self-hosted) |
|------|-------------------|---------------------|
| Subscription | $480/year ($4 × 10 × 12) | $0 |
| VPS (1 GB RAM) | — | $60–120/year |
| SSL certificate | Included | Free (Let's Encrypt) |
| Backups | — | ~$12/year (storage) |
| Maintenance time | 0 | ~1 hour/year |
| **Total** | **$480/year** | **$72–132/year** |

For 10 users, Gitea saves you $350–400/year. The savings scale with team size — at 50 users, GitHub Teams costs $2,400/year while Gitea still costs the same $72–132/year. The break-even point is around 2–3 users; beyond that, self-hosting is cheaper.

But cost isn't the only factor. The real value of Gitea is **control**. Your code stays on your server. Your access policies are yours. Your uptime depends on your infrastructure, not on GitHub's status page. For businesses that take data sovereignty seriously, that's worth more than the subscription savings.

## Common Questions

**Can I still use GitHub for public projects?** Absolutely. Many teams run Gitea for internal code and maintain GitHub accounts for open source contributions. They're not mutually exclusive. You can even mirror repositories between the two — push to Gitea and automatically mirror to GitHub for public visibility.

**Does Gitea support GitHub Actions?** Yes, through **Gitea Actions**, which is compatible with GitHub Actions syntax. If you have existing `.github/workflows` files, most of them will work in Gitea with minimal changes. You'll need to set up a self-hosted runner, but the workflow YAML is largely portable.

**What about GitLab?** GitLab Community Edition is a more feature-rich alternative — it includes built-in CI/CD, container registry, and more advanced project management. But it's also significantly heavier, requiring 4+ GB of RAM and a more powerful server. If you want an all-in-one DevOps platform and have the hardware, GitLab is worth considering. If you want lightweight Git hosting that runs on a $5 VPS, Gitea is the better choice.

**Can I use Gitea for non-code files?** Yes. Git works for any text-based files — documentation, configuration templates, policy documents, even contracts. Some businesses use Gitea as a version-controlled document store for files that need an audit trail. It's not a replacement for a proper document management system like Paperless-ngx for scanned documents, but for text files that change over time, it's excellent.

## Getting Started

If you're already self-hosting tools like Nextcloud or Mattermost, adding Gitea to your stack is a natural next step. It's one of the lightest, most reliable self-hosted applications you can run, and it gives you a foundation for version control and identity management that ties the rest of your stack together.

Start small: set up Gitea, migrate one internal repository, and get your team comfortable with the workflow. Once it's running, explore the OAuth2 integration to centralize logins across your self-hosted tools. Then automate with n8n and the Gitea API.

The whole setup takes about an hour. The payoff — unlimited private repositories, full data control, no per-seat fees, and a central identity provider — lasts as long as you run it.

If you want help setting up Gitea or migrating from GitHub, [get in touch](/#contact). We help businesses build self-hosted infrastructure that's practical, documented, and maintainable — no hype, just tools that work.
