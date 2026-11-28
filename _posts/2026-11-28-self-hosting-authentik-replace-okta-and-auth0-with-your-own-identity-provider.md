---
layout: post
title: "Self-Hosting Authentik: Replace Okta and Auth0 With Your Own Identity Provider"
date: 2026-11-28
author: "ARDOT Consulting"
tags: [authentik, identity-provider, sso, self-hosting, docker, open-source, security]
excerpt: "Centralize login for every app your team uses with Authentik — the open source identity provider that replaces Okta, Auth0, and Keycloak with a self-hosted SSO platform you fully control."
---

Every business reaches a point where managing logins becomes a problem. Your team uses a dozen tools — Mattermost for chat, Kimai for time tracking, NocoDB for databases, BookStack for documentation, Cal.com for scheduling — and each one has its own username and password. New hires need accounts created in every system. Departing employees need accounts deactivated in every system. Some tools support SAML, others only OAuth2, and a few legacy ones only do LDAP.

The commercial answer is an identity provider like Okta or Auth0. They solve the problem — but at $2–15 per user per month, with your most sensitive data (credentials, access policies, group memberships) hosted on someone else's infrastructure. For a 20-person team, that's $480–3,600 per year just for authentication. And you're locking your access control layer into a vendor whose pricing can change overnight.

[Authentik](https://goauthentik.io/) is an open source identity provider and single sign-on (SSO) platform that you self-host. It supports every major authentication protocol — OAuth2, SAML, LDAP, SCIM, and RADIUS — so you can connect virtually any application. It handles user management, group-based access policies, multi-factor authentication, and automated offboarding. And because it runs on your own server, your credentials never leave your infrastructure.

In this guide, we'll walk through what Authentik does, how it compares to the commercial alternatives, and how to get it running with Docker Compose.

## What Authentik Actually Does

Authentik sits between your users and your applications. Instead of each app managing its own authentication, users log in once through Authentik, and Authentik vouches for their identity to every connected application. Here's what that looks like in practice:

### Single Sign-On (SSO)

A user opens Mattermost. Instead of Mattermost asking for a password, it redirects to Authentik. The user logs in (if they haven't already this session), Authentik sends a token back to Mattermost, and they're in. Open Kimai next — already logged in. Open BookStack — already logged in. One login, every app.

Authentik supports the protocols that make this work across different tools:

| Protocol | Common Use Case | Example Applications |
|----------|----------------|---------------------|
| OAuth2 / OIDC | Modern web apps, cloud-native tools | n8n, Gitea, Grafana, Metabase |
| SAML 2.0 | Enterprise apps, older web platforms | Odoo, SuiteCRM, Nextcloud |
| LDAP | Legacy apps, self-hosted tools | BookStack, Kimai, Mailcow |
| SCIM | Automated user provisioning | Slack, GitHub Enterprise |
| RADIUS | Network equipment, VPNs | WireGuard, OpenVPN, Wi-Fi access points |

### Flows: Visual Authentication Workflows

Authentik's standout feature is **Flows** — a visual builder for designing login processes. Instead of a fixed login form, you chain together stages:

1. **Identification** — User enters username or email
2. **Password** — User enters password
3. **MFA** — User enters a TOTP code, inserts a WebAuthn passkey, or approves a push notification
4. **Consent** — User agrees to share specific data with the application
5. **Redirect** — User is sent back to the application with a token

You can customize this flow per application. Internal tools might skip MFA for users on the office network. Customer-facing portals might add a registration stage. Admin tools might require a hardware security key. The flexibility is in your hands.

### Conditional Access Policies

Authentik lets you write policies that control who can access what, and under what conditions:

- **Group-based access**: Only members of the "Finance" group can access Invoice Ninja
- **IP restrictions**: Admin panel only accessible from the office network
- **GeoIP filtering**: Block logins from countries where you have no employees
- **Impossible travel detection**: Flag logins from New York and Tokyo within the same hour
- **Time-based rules**: Contractor access limited to business hours

These policies are evaluated at login time, so changes take effect immediately without restarting services.

### Application Proxy

Some legacy applications don't support any SSO protocol at all — they just serve a web page with no built-in authentication. Authentik's **Outpost** feature acts as a reverse proxy in front of these applications, handling authentication before traffic even reaches the app. The application never sees an unauthenticated request.

This is particularly useful for internal tools — dashboards, admin panels, monitoring interfaces — that were never designed with SSO in mind.

### User Lifecycle Management

When a new employee joins, you create them once in Authentik. When they depart, you deactivate them once in Authentik. SCIM provisioning automatically propagates those changes to connected applications — creating accounts on day one, and suspending them on the last day.

For businesses that have been burned by departed contractors retaining access to critical systems, this alone justifies the migration.

## Authentik vs. Commercial Identity Providers

| Feature | Authentik (Self-Hosted) | Okta | Auth0 | Keycloak |
|---------|------------------------|------|-------|----------|
| Pricing | Free (self-hosted) | $2–15/user/mo | $23–240/mo (tiered) | Free (self-hosted) |
| Data ownership | Full — your server | Vendor-hosted | Vendor-hosted | Full — your server |
| OAuth2 / OIDC | Yes | Yes | Yes | Yes |
| SAML 2.0 | Yes | Yes | Yes (add-on) | Yes |
| LDAP | Yes | Yes | Limited | Yes |
| SCIM provisioning | Yes | Yes | Enterprise only | Limited |
| RADIUS | Yes | Enterprise | No | No |
| WebAuthn / Passkeys | Yes | Yes | Yes | Yes |
| GeoIP / Impossible travel | Yes | Enterprise | Enterprise | No (plugin) |
| Application proxy | Yes | No | No | No |
| Visual flow builder | Yes | No | No (Actions) | No |
| License | MIT (open source) | Proprietary | Proprietary | Apache-2.0 |

Authentik and Keycloak are the two main open source options. Keycloak is older and more widely deployed, but Authentik's visual flow builder, application proxy, and conditional access policies give it an edge for businesses that want fine-grained control without writing custom code. Keycloak requires more configuration through XML files and admin CLI commands; Authentik exposes most of its power through a web interface.

## Hardware Requirements

Authentik needs a modest server to run:

- **2 CPU cores** minimum
- **2 GB RAM** minimum (4 GB recommended for production with 50+ users)
- **20 GB disk** for the database, Redis cache, and application

A $6–12/month VPS handles this comfortably. If you're already self-hosting other tools, Authentik can share the same server — it runs alongside Docker Compose stacks without conflict.

## Installation with Docker Compose

Authentik provides an official `compose.yml` file that includes the server, worker, PostgreSQL, and Redis. Here's how to set it up.

### Step 1: Download the Compose File

```bash
mkdir -p /opt/authentik && cd /opt/authentik
wget https://docs.goauthentik.io/compose.yml
```

### Step 2: Generate Secrets

Authentik needs a PostgreSQL password and a secret key. Generate them with OpenSSL and write them to a `.env` file:

```bash
echo "PG_PASS=$(openssl rand -base64 36 | tr -d '\n')" >> .env
echo "AUTHENTIK_SECRET_KEY=$(openssl rand -base64 60 | tr -d '\n')" >> .env
```

Keep the `.env` file secure — these credentials protect your entire identity system. Back them up somewhere safe.

### Step 3: Configure Ports (Optional)

By default, Authentik listens internally on ports 9000 (HTTP) and 9443 (HTTPS). If you want to expose it directly on standard ports, add this to your `.env`:

```bash
echo "COMPOSE_PORT_HTTP=80" >> .env
echo "COMPOSE_PORT_HTTPS=443" >> .env
```

If you're already running a reverse proxy like Caddy or Nginx Proxy Manager (recommended), leave the defaults and proxy traffic to port 9000.

### Step 4: Start Authentik

```bash
docker compose pull
docker compose up -d
```

The first startup takes 1–2 minutes as Authentik runs database migrations. Once it's up, navigate to `http://your-server-ip:9000` (or your reverse proxy URL) and you'll see the setup wizard.

### Step 5: Complete Initial Setup

The setup wizard asks you to create an admin account and configure your default tenant. Set:

- **Admin email and password** — Your master credentials
- **Tenant name** — Your organization name (shown on the login page)

That's it. Authentik is running.

## Connecting Your First Application

Let's walk through connecting n8n as an example — since n8n is one of the most common tools in a self-hosted stack.

### In Authentik

1. Go to **Admin Interface → Applications → Applications**
2. Click **Create** and fill in:
   - **Name**: n8n
   - **Slug**: n8n
3. Select **OAuth2/OpenID Provider** and configure:
   - **Authorization flow**: default-authentication-flow
   - **Redirect URI**: `https://n8n.yourdomain.com/rest/oauth2-redirect`
4. Save and note the **Client ID** and **Client Secret**

### In n8n

Set these environment variables in your n8n Docker configuration:

```bash
N8N_USER_MANAGEMENT_JWT_AUTH_ENABLED=true
N8N_SSO_OIDC_LOGIN_ENABLED=true
N8N_SSO_OIDC_ISSUER=https://auth.yourdomain.com/application/o/n8n/
N8N_SSO_OIDC_CLIENT_ID=your-client-id
N8N_SSO_OIDC_CLIENT_SECRET=your-client-secret
```

Restart n8n. When users visit the n8n login page, they'll see a "Sign in with SSO" button that redirects to Authentik. After authenticating, they're redirected back to n8n — logged in and ready to work.

The process is similar for other applications. Most modern self-hosted tools (Gitea, Grafana, Metabase, Outline, BookStack, Nextcloud) support OAuth2 or SAML, and Authentik's documentation includes provider-specific guides for dozens of applications.

## Setting Up Multi-Factor Authentication

Authentik supports several MFA methods:

- **TOTP** — Time-based one-time passwords (Google Authenticator, Authy, FreeOTP)
- **WebAuthn / Passkeys** — Hardware security keys (YubiKey, Titan) and platform authenticators (Touch ID, Windows Hello)
- **Duo** — Push-based authentication via Duo Security
- **SMS** — Text-based codes (requires an SMS gateway)

To require MFA for a specific application, add a TOTP or WebAuthn stage to the authentication flow used by that application. Users will be prompted to enroll their MFA device on their next login.

For passkeys specifically — which are increasingly replacing passwords entirely — Authentik's WebAuthn support lets you create passwordless login flows. Users authenticate with a fingerprint, face scan, or hardware key, no password required.

## Automating Offboarding

One of the highest-value features for growing teams is automated offboarding. Here's how to set it up:

1. **Create groups** for each department or role (e.g., "Engineering", "Sales", "Contractors")
2. **Assign applications** to groups — Engineering gets Gitea, Sales gets SuiteCRM, everyone gets Mattermost
3. **Set expiration dates** for contractor accounts — Authentik automatically deactivates them on the specified date
4. **Configure SCIM** where supported — deactivating a user in Authentik automatically suspends their account in connected apps

When someone leaves, you deactivate their Authentik account. Every connected application immediately rejects their token. If they had a session open in Mattermost, their next API call fails. No more chasing down accounts across a dozen tools.

## Backup and Recovery

Your identity provider is a single point of failure — if Authentik goes down, nobody can log into anything. Treat it accordingly:

**Database backups**: The PostgreSQL database stores all users, groups, policies, and application configurations. Back it up daily:

```bash
docker exec authentik-postgres pg_dump -U authentik authentik | gzip > /backups/authentik-$(date +%Y%m%d).sql.gz
```

**Secret backup**: Store your `.env` file (containing `PG_PASS` and `AUTHENTIK_SECRET_KEY`) in a password manager or encrypted backup. Without the secret key, encrypted data in the database is unrecoverable.

**High availability**: For production deployments with downtime intolerance, Authentik supports high-availability configurations with multiple server replicas and a shared PostgreSQL cluster. For most small businesses, a single instance with daily backups is sufficient — the service is lightweight and rarely fails.

## Integrating with Your Existing Stack

Authentik connects to the tools you're already self-hosting:

| Tool | Protocol | Use Case |
|------|----------|----------|
| n8n | OAuth2 | Workflow automation with SSO |
| Gitea | OAuth2 / SAML | Code hosting with team login |
| Mattermost | OAuth2 / SAML | Team chat with centralized auth |
| Nextcloud | SAML / OAuth2 | File sharing with enterprise SSO |
| BookStack | SAML | Documentation with group-based access |
| Kimai | SAML / LDAP | Time tracking with department controls |
| Grafana | OAuth2 | Monitoring dashboards with admin roles |
| Metabase | SAML | Analytics with data team access |
| Outline | OIDC | Knowledge base with team login |
| Vaultwarden | (acts as its own IdP) | Password manager — can federate through Authentik for admin access |

The pattern is the same: create an application in Authentik, configure the provider (OAuth2, SAML, or LDAP), paste the credentials into your tool's SSO settings, and you're done.

## Cost Comparison

Let's quantify the savings for a 20-person team:

| Solution | Monthly Cost | Annual Cost |
|----------|-------------|-------------|
| Okta (Workforce Essentials) | $80 ($4/user × 20) | $960 |
| Okta (Workforce Plus) | $300 ($15/user × 20) | $3,600 |
| Auth0 (Essentials) | $23 (up to 7,500 MAU) | $276 |
| Auth0 (Plus) | $240/month | $2,880 |
| Authentik (self-hosted) | $6–12 VPS | $72–144 |

Even compared to the cheapest commercial tier, Authentik saves $130+ per year. Compared to Okta's mid-tier, the savings exceed $3,400 annually. For a 50-person team, the gap widens dramatically — Okta Plus costs $9,000/year versus Authentik's ~$120 VPS cost.

The trade-off is operational: you maintain the server, apply updates, and manage backups. If you're already self-hosting other tools, Authentik fits naturally into your existing Docker Compose stack with minimal additional overhead.

## When to Choose Authentik

Authentik is the right choice if:

- You're self-hosting 3+ applications and managing separate logins for each
- You need SSO across tools that use different protocols (OAuth2 + SAML + LDAP)
- You want conditional access policies (IP restrictions, geo-fencing, group-based access)
- You need automated user provisioning and offboarding
- You want passkey/WebAuthn support without enterprise pricing
- Your team is growing and manual account management is becoming unsustainable

It may be overkill if you only use 1–2 self-hosted applications — in that case, each tool's built-in authentication is probably sufficient.

## Getting Started

The quickest way to evaluate Authentik is to spin it up on a test server with Docker Compose, connect one application (n8n is a good first choice), and walk through the login flow yourself. The whole setup takes about 30 minutes, and you'll have a working SSO system you can expand one application at a time.

Authentik's [documentation](https://docs.goauthentik.io/) includes installation guides, provider-specific setup tutorials for dozens of applications, and a community Discord for troubleshooting.

If you'd like help setting up Authentik or migrating from Okta, Auth0, or Keycloak, [get in touch with ARDOT Consulting](/). We specialize in open source infrastructure for small businesses — from identity management to workflow automation, all on your own servers, all under your control.
