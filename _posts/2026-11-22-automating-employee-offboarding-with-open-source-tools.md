---
layout: post
title: "Automating Employee Offboarding with Open Source Tools"
date: 2026-11-22
author: "ARDOT Consulting"
tags: [offboarding, hr, automation, n8n, keycloak, security, open-source]
excerpt: "Employee offboarding is full of security risks and manual steps. Here's how to automate it end-to-end with open source tools like n8n, Keycloak, and Nextcloud."
---

Yesterday we covered automating customer onboarding. Today, let's talk about the other side of the employee lifecycle — offboarding. It's the process every business needs but nobody wants to think about. And it's where most security gaps live.

When an employee leaves, you need to revoke access to a dozen systems, recover company equipment, transfer their files, conduct an exit interview, and archive their accounts — all within a tight window. Miss a step, and you've got a former employee who can still read your Slack channels, download files from your project management tool, or worse.

The cost of getting offboarding wrong isn't just security. It's also time. IT managers spend an average of 3–5 hours per departing employee just on account provisioning and deprovisioning. For a company with 50 employees and 15% annual turnover, that's 30–50 hours a year spent on manual offboarding tasks.

Here's how to automate it with open source tools you can self-host.

## Why Offboarding Is Harder Than Onboarding

Onboarding has a natural momentum — everyone wants to help a new hire get set up. Offboarding is the opposite. The employee is already mentally gone. Managers are busy with their remaining team. And the task list is longer and more security-critical.

A complete offboarding checklist typically includes:

1. **Revoke system access** — email, chat, file sharing, CRM, project management, code repositories, cloud consoles
2. **Recover hardware** — laptops, phones, keys, badges
3. **Transfer data ownership** — reassign files, documents, project leads, recurring meetings
4. **Process final paperwork** — final paycheck, benefits termination, exit survey
5. **Archive accounts** — preserve emails and messages for compliance, then disable
6. **Update directories** — remove from company directory, Slack, Mattermost channels, mailing lists
7. **Notify stakeholders** — inform the team, clients, and external partners

Now multiply that by the number of systems you use. A typical small business might have 8–15 different tools. Each one needs a manual login, a search for the departing user, and a deactivation. It's tedious, error-prone, and easy to skip steps.

## The Open Source Offboarding Stack

The good news: if you're already self-hosting your business tools, you have everything you need to automate offboarding. Here's the stack we recommend:

| Tool | Role | Why It Matters |
|------|------|----------------|
| **Keycloak** | Identity provider | Central authentication — revoke once, disable everywhere |
| **n8n** | Workflow orchestration | Triggers the offboarding sequence and calls each system's API |
| **Nextcloud** | File management | Transfers file ownership and revokes share links |
| **Mattermost** | Team chat | Deactivates user, transfers channel admin rights |
| **BookStack** | Knowledge base | Removes edit access, preserves page history |
| **Odoo / ERPNext** | HR & payroll | Processes final paperwork, updates employee record |
| **Vaultwarden** | Password manager | Removes user from shared vaults |
| **Gitea** | Code hosting | Removes from organizations, revokes SSH keys and tokens |

The key insight is **Keycloak as your central identity provider**. If all your self-hosted tools authenticate through Keycloak using SSO (SAML or OpenID Connect), then disabling a user in Keycloak instantly revokes their access across every connected application. You don't need to log into each tool individually.

## Step 1: Centralize Authentication with Keycloak

If you haven't already, set up Keycloak as your identity provider. Most self-hosted tools support OpenID Connect or SAML out of the box:

- **Nextcloud**: OpenID Connect user backend app
- **Mattermost**: SAML 2.0 plugin (Enterprise edition) or OAuth proxy
- **BookStack**: SAML or OpenID Connect authentication
- **Gitea**: OAuth2 / OpenID Connect sign-in
- **Odoo**: Auth OAuth module
- **Vaultwarden**: SSO via reverse proxy auth

Here's a minimal Docker Compose snippet to get Keycloak running:

```yaml
version: "3.8"
services:
  keycloak:
    image: quay.io/keycloak/keycloak:26.0
    environment:
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
      KC_DB_USERNAME: keycloak
      KC_DB_PASSWORD: ${KC_DB_PASSWORD}
      KC_HOSTNAME: auth.yourcompany.com
      KC_PROXY_HEADERS: xforwarded
    command: start
    ports:
      - "8080:8080"
    depends_on:
      - postgres

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: keycloak
      POSTGRES_USER: keycloak
      POSTGRES_PASSWORD: ${KC_DB_PASSWORD}
    volumes:
      - keycloak_db:/var/lib/postgresql/data

volumes:
  keycloak_db:
```

Once Keycloak is your single source of truth for identities, disabling a user is one API call. Everything else flows from that.

## Step 2: Build the Offboarding Workflow in n8n

n8n is where the automation lives. The workflow is triggered when HR marks an employee as "departing" in Odoo (or ERPNext, or even a simple NocoDB form). From there, n8n orchestrates the entire sequence.

Here's what the workflow looks like:

```
[Trigger: Employee status → "Departing" in Odoo]
    │
    ├──→ [Keycloak: Disable user account]
    │
    ├──→ [Nextcloud: Transfer file ownership to manager]
    │
    ├──→ [Mattermost: Deactivate user, reassign channels]
    │
    ├──→ [Gitea: Remove from orgs, revoke SSH keys & tokens]
    │
    ├──→ [Vaultwarden: Remove from shared vaults]
    │
    ├──→ [BookStack: Remove edit permissions]
    │
    ├──→ [Email: Send exit checklist to manager]
    │
    ├──→ [Email: Send exit survey to departing employee]
    │
    └──→ [Slack/Mattermost: Notify team channel]
```

Each step is an HTTP Request node in n8n calling the relevant tool's API. Here's an example of the Keycloak deactivation step:

### Keycloak: Disable User

```json
{
  "method": "PUT",
  "url": "https://auth.yourcompany.com/admin/realms/yourcompany/users/{{$json.keycloak_user_id}}",
  "headers": {
    "Authorization": "Bearer {{$node[\"GetKeycloakToken\"].json[\"access_token\"]}}",
    "Content-Type": "application/json"
  },
  "body": {
    "enabled": false
  }
}
```

### Nextcloud: Transfer File Ownership

```json
{
  "method": "POST",
  "url": "https://files.yourcompany.com/ocs/v2.php/cloud/users/{{$json.username}}/transfer",
  "headers": {
    "OCS-APIRequest": "true",
    "Authorization": "Basic {{$node[\"NextcloudCreds\"].json[\"auth\"]}}"
  },
  "body": {
    "newuser": "{{$json.manager_username}}"
  }
}
```

### Gitea: Revoke Access

```json
{
  "method": "DELETE",
  "url": "https://git.yourcompany.com/api/v1/orgs/{{$json.org_name}}/members/{{$json.username}}",
  "headers": {
    "Authorization": "token {{$node[\"GiteaToken\"].json[\"token\"]}}"
  }
}
```

The beauty of n8n is that each step is independent. If one API call fails (maybe the user wasn't in that particular Gitea org), the workflow can continue with the others and log the exception for manual follow-up.

## Step 3: Handle the Human Parts

Not everything can be automated. Equipment return, exit interviews, and final paychecks need human involvement. But you can automate the *reminders and tracking*.

Add these nodes to your n8n workflow:

- **Create a task in your project management tool** (e.g., via the OpenProject or Vikunja API) for the manager to collect laptop, badge, and keys
- **Send a Cal.com scheduling link** to the departing employee for their exit interview
- **Generate a final paycheck record** in Odoo/ERPNext for payroll processing
- **Send a checklist email** to the manager with all pending items and their status

The workflow can also include a delay node — trigger access revocation immediately, but wait 7 days before archiving the email account (in case the team needs to search for old communications).

## Step 4: Audit and Compliance

For many businesses, especially in regulated industries, you need to prove that offboarding was completed correctly. Your n8n workflow can generate an audit trail automatically.

Add a final node that writes to a simple log — either a NocoDB table, a Directus collection, or even a BookStack page:

```json
{
  "method": "POST",
  "url": "https://db.yourcompany.com/api/v1/offboarding_logs",
  "headers": {
    "Authorization": "Bearer {{$node[\"NocoDBToken\"].json[\"token\"]}}"
  },
  "body": {
    "employee_name": "{{$json.employee_name}}",
    "departure_date": "{{$json.departure_date}}",
    "keycloak_disabled": "{{$json.keycloak_status}}",
    "nextcloud_transferred": "{{$json.nextcloud_status}}",
    "mattermost_deactivated": "{{$json.mattermost_status}}",
    "gitea_revoked": "{{$json.gitea_status}}",
    "vaultwarden_removed": "{{$json.vaultwarden_status}}",
    "manager_notified": "{{$json.email_status}}",
    "completed_at": "{{$now}}"
  }
}
```

Now you have a searchable record of every offboarding event, what was completed, and when. If a auditor asks "prove you revoked access for employee X on their departure date," you have the answer in seconds.

## What This Saves You

Let's quantify the impact for a 50-person company with 15% annual turnover (7–8 departures per year):

| Task | Manual Time | Automated Time |
|------|-------------|----------------|
| Disable accounts (8 systems) | 40 min/employee | 0 min (automated) |
| Transfer file ownership | 20 min/employee | 0 min (automated) |
| Generate audit record | 15 min/employee | 0 min (automated) |
| Send notifications | 10 min/employee | 0 min (automated) |
| **Total per departure** | **85 min** | **~5 min (review only)** |

At 8 departures per year, that's **~11 hours saved annually** — not enormous in absolute terms, but the real value is in risk reduction. The cost of a single security incident from a missed deactivation (a former employee accessing client data, exporting contacts, reading internal communications) can be thousands of dollars in legal fees, lost client trust, and remediation time.

The automated workflow also brings **consistency**. Every offboarding follows the same steps. Nothing gets forgotten because someone was busy or on vacation.

## Getting Started

You don't need to automate everything at once. Here's a practical phased approach:

**Phase 1 (Week 1):** Deploy Keycloak and connect your two most critical tools (email and file sharing). Even without automation, centralized SSO makes manual deactivation a single step.

**Phase 2 (Week 2–3):** Build the n8n workflow for the core steps — Keycloak deactivation, Nextcloud transfer, Mattermost deactivation, and manager notification. This covers 80% of the risk.

**Phase 3 (Week 4):** Add the long tail — Gitea, Vaultwarden, BookStack, audit logging, and equipment return reminders. These are lower-frequency but still important.

**Phase 4 (Ongoing):** Review the audit logs quarterly. Are there steps that frequently fail? Tools you've added that aren't in the workflow yet? Iterate.

## A Note on Data Sensitivity

Offboarding involves sensitive employee data — departure reasons, final compensation, exit interview feedback. When you self-host your HR tools and automation platform, this data never leaves your infrastructure. There's no third-party SaaS HR platform with your employees' departure records, no cloud automation service processing your personnel changes.

For businesses in regulated industries (healthcare, finance, legal), this data sovereignty isn't just a preference — it's often a compliance requirement. Self-hosted open source tools give you full control over where data lives, who can access it, and how long it's retained.

## Wrapping Up

Employee offboarding is one of those processes that's invisible when it works and catastrophic when it doesn't. By centralizing authentication with Keycloak and orchestrating the full sequence with n8n, you turn a scattered, error-prone manual process into a reliable, auditable workflow.

The tools are free. The setup takes a few weekends. The peace of mind — knowing that when someone leaves, access is revoked automatically and nothing falls through the cracks — is worth it.

---

*Want help setting up an automated offboarding workflow for your business? ARDOT Consulting specializes in open source automation for small and mid-size companies. [Get in touch](https://www.ardotconsulting.com/#contact) and we'll help you build a secure, self-hosted offboarding process tailored to your stack.*
