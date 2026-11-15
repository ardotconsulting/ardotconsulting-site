# Umami Analytics — Self-Hosted Deployment

## Overview
Self-hosted [Umami](https://github.com/umami-software/umami) analytics on the ARDOT lab server via Coolify, managed by OpenTofu.

Replaces Plausible Cloud (paid SaaS) with a fully self-hosted, open source (MIT) alternative. Dog-fooding our own blog post: ["Self-Hosting Umami: Privacy-First Web Analytics Without Google Analytics"](https://www.ardotconsulting.com/blog/2026/12/11/self-hosting-umami-privacy-first-web-analytics-without-google-analytics/).

## Architecture
- **Coolify** deploys Umami from the official Docker image on `h-ac-web-p-001`
- **PostgreSQL** runs as a companion container (Umami requires a database)
- **DNS**: `analytics.ardotconsulting.com` → lab server IP (`167.233.115.58`)
- **Access**: `https://analytics.ardotconsulting.com` (TLS via Coolify/Traefik)

## Files
- `umami/main.tf` — OpenTofu config (Coolify project + application)
- `umami/dns-update.tf` — DNS record to add to `hetzner/dns.tf`

## Deployment steps (for Ryan)
1. Review this PR
2. Add the DNS record from `dns-update.tf` to `hetzner/dns.tf`
3. `tofu init` in `umami/`
4. `tofu apply` — creates the Coolify project and application
5. Umami deploys automatically via Coolify
6. Access `https://analytics.ardotconsulting.com`, log in (default: `admin` / `umami`)
7. Add website `ardotconsulting.com` in Umami dashboard
8. Get the tracking script URL from Umami
9. Replace Plausible script in `ardotconsulting-site/_includes/head.html` with the Umami tracking script
10. Verify analytics events are firing

## After deployment
- Update `PROJECT_TRACKER.md` with the setup details
- @ardot_researcher_bot to write a follow-up blog post: "How ARDOT Self-Hosted Its Own Analytics"

## Why
- We wrote the blog post telling others to self-host Umami — we should lead by example
- Eliminates Plausible Cloud subscription (paid SaaS)
- Full data ownership, no cookies, privacy-first, MIT licensed
