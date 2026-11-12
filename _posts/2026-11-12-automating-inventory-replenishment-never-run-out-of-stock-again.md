---
layout: post
title: "Automating Inventory Replenishment: Never Run Out of Stock Again"
date: 2026-11-14
author: "ARDOT Consulting"
tags: [inventory, replenishment, automation, open-source, odoo, n8n, nocodb, ollama, self-hosting]
excerpt: "Stockouts cost sales. Overstocking ties up cash. Here's how to automate inventory replenishment with open-source tools that monitor stock levels, trigger reorders, and keep your shelves full without a SaaS subscription."
---

# Automating Inventory Replenishment: Never Run Out of Stock Again

Every business that sells physical goods has the same problem on repeat: when do you reorder, and how much? Order too late and you stock out, losing sales and frustrating customers. Order too early and you tie up cash in inventory that sits on shelves.

Most small businesses handle this with a spreadsheet and a gut feeling. Someone walks the warehouse, eyeballs the shelves, and writes down what looks low. The reorder point for a fast-moving item might be "when the shelf looks half empty" — which is not a number you can automate or audit.

The result is predictable. A distributor we worked with was stock-out on their top 20 SKUs an average of 11 days per quarter. That's a month of lost sales every year on their best products. Meanwhile, they had $60,000 tied up in slow-moving inventory that nobody had flagged for review in eight months. Both problems share a root cause: no automated replenishment system.

The fix doesn't require a $2,000/month enterprise platform. Open-source and self-hostable tools can monitor stock levels, calculate reorder points, and trigger purchase orders automatically. Here's how to build that system.

## What Replenishment Automation Actually Does

Replenishment automation replaces the "walk and eyeball" method with rules-based logic:

1. **Monitors stock levels in real time.** Every sale, receipt, transfer, or adjustment updates a central database. No more end-of-week spreadsheet reconciliation.
2. **Triggers reorders at the right moment.** When stock drops below a predefined reorder point, the system flags it or creates a purchase order automatically.
3. **Calculates the right quantity.** Instead of ordering "a box," the system factors in lead time, demand velocity, and safety stock to order enough to cover the replenishment cycle.

The math isn't complicated. Reorder point = (average daily demand × lead time in days) + safety stock. What's hard isn't the formula — it's keeping the inputs current and acting on the output consistently. That's where automation comes in.

## The Tools: Three Approaches

There are three practical ways to automate replenishment with tools you can self-host. Each fits a different business size and complexity level.

### Approach 1: Odoo Community Edition (All-in-One)

[Odoo](https://www.odoo.com/app/inventory) is a full business suite licensed under the LGPL v3, making the Community Edition genuinely open source. Its Inventory module includes built-in replenishment rules: min-max rules, Make-to-Order (MTO) routes, and the master production schedule. When stock drops below a minimum, Odoo can automatically generate a purchase order or manufacturing order.

Odoo is the right choice if you want replenishment tied directly to purchasing, sales, and accounting in one system. A sale creates a delivery order, the delivery reduces stock, the stock drop triggers a reorder rule, the reorder creates a draft purchase order, and the PO flows into vendor management. No external integrations needed.

We covered setting up Odoo Community Edition with Docker in a [previous guide on CRM automation](/blog/2026/09/09/setting-up-odoo-community-edition-crm-automation-for-small-business/). The Inventory module installs the same way — add it from the Apps menu after your Docker instance is running.

### Approach 2: NocoDB + n8n (Modular)

If you already track inventory in a spreadsheet or database and don't want to migrate to a full ERP, [NocoDB](https://github.com/nocodb/nocodb) plus [n8n](https://github.com/n8n-io/n8n) gives you replenishment automation without changing how you store data.

NocoDB turns any PostgreSQL or MySQL database into a spreadsheet-like interface with API access. You keep your existing inventory table — SKU, description, quantity on hand, reorder point, lead time — and NocoDB makes it editable through a web UI and queryable through a REST API.

n8n monitors that table on a schedule, checks which items have fallen below their reorder points, and triggers actions: create a purchase order record, send a Mattermost notification, or email a supplier directly.

**A note on licenses:** NocoDB and n8n are both distributed under the Sustainable Use License, which is a source-available license — not OSI-approved open source. You can self-host them freely for internal business use, but the license restricts reselling them as a hosted service. For most small businesses running these tools internally, this distinction doesn't matter in practice. But if you're in a regulated industry with strict open-source procurement requirements, Odoo Community (LGPL v3) is the safer choice.

### Approach 3: InvenTree (Purpose-Built)

[InvenTree](https://github.com/inventree/InvenTree) is an open-source inventory management system (MIT-licensed) specifically designed for parts and component tracking. If your business deals with parts, assemblies, or BOMs — think electronics manufacturers, repair shops, or makers — InvenTree is purpose-built for this use case.

When a part's stock drops below its minimum, InvenTree generates an alert visible in the dashboard or sent via webhook. Connect that webhook to n8n, and you've got automated PO creation without touching Odoo.

## Setting Up Reorder Rules in Odoo Community

Let's walk through the most common setup: configuring automated replenishment in Odoo Community Edition.

### Step 1: Install the Inventory Module

From your Odoo instance (running via Docker as described in our [setup guide](/blog/2026/09/09/setting-up-odoo-community-edition-crm-automation-for-small-business/)), go to the Apps menu and install "Inventory." This gives you warehouse management, stock moves, and the replenishment rules engine.

### Step 2: Configure Your Products

For each product you want to automate, open the product form and set these fields:

- **Reordering Rule** — enable this on the Inventory tab
- **Min Quantity** — the stock level that triggers a reorder
- **Max Quantity** — the stock level to order up to
- **Lead Time** — how many days between placing the PO and receiving the stock

Set the min quantity based on your lead time and average daily sales. If you sell 10 units per day and your supplier takes 7 days to deliver, your min quantity should be at least 70 units (plus a safety buffer). The max quantity is typically min + your normal order size.

### Step 3: Enable Automated Reordering

Once reorder rules are in place, Odoo's scheduler checks stock levels daily. When a product drops below its minimum, Odoo creates a draft purchase order for the quantity needed to reach the max. Configure this to either:

- **Manual confirmation** — draft POs sit in the purchasing queue for review
- **Automatic confirmation** — POs are confirmed and sent to the vendor without human intervention

Most businesses start with manual confirmation, then switch to automatic for trusted, high-frequency suppliers once the reorder quantities are tuned.

### Step 4: Tune the Reorder Points

The first month is about calibration. Watch which items stock out (raise the min) and which sit above the max (lower the max). After 60–90 days, your reorder points should stabilize and require minimal adjustment.

## Building a Replenishment Workflow with n8n + NocoDB

If you're taking the modular approach, here's a practical n8n workflow that checks stock levels and triggers reorders.

### The Inventory Table in NocoDB

Create a table called `inventory` with these columns:

| Column | Type | Example |
|--------|------|---------|
| sku | string | WIDGET-001 |
| name | string | Blue Widget |
| qty_on_hand | integer | 45 |
| reorder_point | integer | 50 |
| reorder_qty | integer | 200 |
| lead_time_days | integer | 7 |
| supplier_email | string | orders@supplier.com |
| last_reorder_date | date | 2026-11-01 |

NocoDB exposes this table through a REST API at `https://your-nocodb-instance/api/v2/tables/{tableId}/records`.

### The n8n Workflow

Build a workflow with these nodes:

**Node 1: Schedule Trigger.** Run daily at 8:00 AM. This replaces the Friday warehouse walk.

**Node 2: HTTP Request.** Query the NocoDB API for all inventory records where `qty_on_hand <= reorder_point`. The filter URL looks like:

```
https://your-nocodb-instance/api/v2/tables/{tableId}/records?where=(qty_on_hand,le,reorder_point)
```

Include your NocoDB API token in the `xc-token` header.

**Node 3: Split In Batches.** If multiple items need reordering, process each one individually.

**Node 4: HTTP Request (create PO).** POST to a `purchase_orders` table in NocoDB to log the order:

{% raw %}
```json
{
  "sku": "={{ $json.sku }}",
  "quantity": "={{ $json.reorder_qty }}",
  "supplier": "={{ $json.supplier_email }}",
  "status": "draft",
  "created_date": "={{ $now.toISO() }}"
}
```
{% endraw %}

**Node 5: Send Email.** Email the supplier with the order details. Use n8n's built-in SMTP node or connect to a self-hosted mail server.

**Node 6: Mattermost Notification.** Post a message to your purchasing channel so the team knows a reorder was triggered:

{% raw %}
```
📦 Auto-reorder triggered: {{ $json.name }} ({{ $json.sku }})
   Quantity: {{ $json.reorder_qty }}
   Supplier: {{ $json.supplier_email }}
   Current stock: {{ $json.qty_on_hand }} (reorder point: {{ $json.reorder_point }})
```
{% endraw %}

This workflow runs unattended, checks every SKU every morning, and handles the reorder without anyone walking the warehouse. If you're new to n8n, our [beginner's guide to n8n workflows](/blog/2026/08/17/how-to-build-your-first-ai-automation-workflow-with-n8n/) walks through the basics.

## Adding Demand Forecasting with Ollama

Reorder points based on average daily demand work well for stable products. But what about seasonal items, new products, or products with growing demand? A static reorder point can't adapt to changing patterns. This is where a local LLM adds value.

[Ollama](https://ollama.com) lets you run language models on your own hardware. Connect it to your n8n workflow to analyze sales trends and suggest reorder point adjustments.

Here's the pattern:

1. **Monthly review node.** Once a month, n8n pulls the last 90 days of sales data per SKU from NocoDB.
2. **Ollama API call.** Send the data to a local Ollama instance with a prompt:

{% raw %}
```
Analyze this 90-day sales history for SKU {{ sku }}:
{{ sales_data }}

1. Is demand trending up, down, or stable?
2. Is there weekly or monthly seasonality?
3. What should the reorder point be for the next 30 days (lead time: {{ lead_time }} days)?
4. Is the current reorder quantity appropriate?

Current reorder point: {{ current_reorder_point }}
Current reorder qty: {{ current_reorder_qty }}
```
{% endraw %}

3. **Review suggestions.** The LLM's output goes to a Mattermost channel for human review. A purchasing manager approves or adjusts the recommended reorder points.

This is AI-assisted review, not fully automated forecasting. The LLM spots patterns a human might miss, but a person makes the final call. For a small business with 200–500 SKUs, this monthly review takes about an hour and catches drift before it causes stockouts.

We covered setting up Ollama in our [practical guide for businesses](/blog/2026/08/20/running-local-llms-with-ollama-a-practical-guide-for-businesses/). The n8n integration uses an HTTP Request node pointed at `http://localhost:11434/api/generate`. No external API calls, no per-token costs, no sales data leaving your server.

## Comparison: Which Approach Fits You?

| Feature | Odoo Community | NocoDB + n8n | InvenTree |
|---------|---------------|-------------|-----------|
| License | LGPL v3 (open source) | Sustainable Use (source-available) | MIT (open source) |
| Setup complexity | Medium | Medium | Low-Medium |
| Built-in reorder rules | Yes | No (build in n8n) | Yes (alerts) |
| Auto PO generation | Yes | Via n8n workflow | Via webhook + n8n |
| Full ERP integration | Yes (purchasing, sales, accounting) | No | No |
| API access | Yes (XML-RPC, REST) | Yes (REST) | Yes (REST, Python) |
| BOM / assembly support | Yes (Manufacturing module) | Manual | Yes (core feature) |
| Best for | Businesses wanting one system | Businesses with existing data | Parts/component businesses |
| GitHub stars | 40k+ | 65k+ | 4k+ |

## Cost Comparison

The argument for self-hosting is straightforward. Here's what a 50-SKU business with 3 users would pay:

| Solution | Monthly Cost | Annual Cost |
|----------|-------------|-------------|
| TradeGecko / QuickBooks Commerce | $199–$399 | $2,388–$4,788 |
| Cin7 | $299–$599 | $3,588–$7,188 |
| Odoo Enterprise (Inventory) | ~$24/user + $724/app | ~$1,700+ |
| Odoo Community (self-hosted) | $20 (server) | $240 |
| NocoDB + n8n (self-hosted) | $20 (server) | $240 |
| InvenTree (self-hosted) | $10–$20 (server) | $120–$240 |

The self-hosted options share a server you're likely already running for other tools. If you've followed our [self-hosting series](/blog/2026/11/10/self-hosting-caddy-the-reverse-proxy-that-makes-https-effortless/), adding an inventory tool is one more `docker-compose` file.

The trade-off is your time: 4–8 hours on setup, 1–2 hours per month on maintenance. Even at $75/hour, you're saving $2,000–$6,000 per year compared to SaaS inventory tools.

## When Automated Replenishment Might Not Be Right

Not every business should automate replenishment day one:

- **Very low SKU count (under 20).** If you can eyeball your inventory in 10 minutes, setup time exceeds the time saved. A spreadsheet with conditional formatting is sufficient.
- **Highly irregular demand.** If your products are one-off or custom (made-to-order), reorder points don't apply. You're ordering per project, not replenishing stock.
- **Supplier reliability issues.** If lead times vary wildly (7 days one order, 30 days the next), reorder point calculations break down. Fix the supplier relationship first.
- **No one to maintain the system.** If nobody can update Docker containers, check logs, and tune reorder points, a managed SaaS is the better choice. Self-hosting requires someone willing to own it.

For businesses with 50+ SKUs, consistent suppliers, and someone who can manage a server, automated replenishment pays for itself within the first quarter.

## Getting Started: A 30-Day Plan

If you want to move from spreadsheet-based inventory to automated replenishment, here's a realistic timeline:

**Week 1: Choose your tool and get it running.** Pick Odoo Community if you want the full suite, NocoDB + n8n if you want modular, or InvenTree if you're in parts. Deploy via Docker.

**Week 2: Import your inventory data.** Get every SKU into the system with accurate quantities on hand. Barcode scanning, physical counts, data entry. Garbage in, garbage out.

**Week 3: Set reorder points.** For each SKU, calculate (average daily demand × lead time) + safety stock. Start conservative.

**Week 4: Enable automated reordering.** Start with manual PO confirmation. Every time a reorder triggers, verify it was the right call. Adjust min/max quantities.

After 30 days, you'll have a system that catches stockouts before they happen and frees up the person who used to walk the warehouse every Friday.

Inventory replenishment is one of the highest-ROI automation targets for any business that sells physical goods. The cost of stockouts and overstocking compounds every month you operate without a proper system.

The tools to fix this are self-hostable and well within reach for a small business with a $20/month server and someone willing to spend a weekend setting it up. Whether you choose Odoo Community for the integrated approach, NocoDB + n8n for modularity, or InvenTree for parts-specific needs, the pattern is the same: centralize your inventory data, set reorder rules, and let the system watch the shelves so you don't have to.

If you want help choosing the right inventory automation approach for your business, [reach out through our contact form](/). We'll help you map your current process, pick the right tools, and build a replenishment workflow that fits how you actually operate.
