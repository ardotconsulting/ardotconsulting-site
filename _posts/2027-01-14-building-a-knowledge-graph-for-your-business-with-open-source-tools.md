---
layout: post
title: "Building a Knowledge Graph for Your Business with Open Source Tools"
date: 2027-01-14
author: "ARDOT Consulting"
tags: [knowledge-graph, neo4j, open-source, data-integration, ai, self-hosting, n8n]
excerpt: "Your business data lives in a dozen disconnected systems — CRM, inventory, accounting, support tickets, email. A knowledge graph connects them so you can ask real questions and get real answers. Here's a practical, no-hype guide to building one with open source tools."
---

# Building a Knowledge Graph for Your Business with Open Source Tools

Here's a familiar situation. A customer calls in with a problem. The support agent opens the help desk system and sees the ticket. But to understand the full picture, they also need to check the CRM for the customer's account history, the accounting system for their payment status, the inventory system for whether the product they bought is in stock, and the email archive for the last conversation. Five systems, five logins, five searches. By the time the agent pieces it together, the customer has been on hold for twelve minutes.

Every business accumulates data silos. You start with a CRM. You add an invoicing tool. You add a help desk. You add an inventory system. Each one stores a slice of the truth about your customers, products, and operations. Each one is good at its specific job. But none of them talk to each other in a way that lets you ask cross-system questions like "which customers who bought product X in the last six months have open support tickets about defects?"

A knowledge graph solves this. It's not a new database that replaces your existing ones. It's a layer that sits on top of them, connecting the dots between people, products, transactions, and events. And you can build one with open source tools, on your own infrastructure, without sending your data to anyone.

Let's walk through what a knowledge graph actually is, why it matters for your business, and how to build one practically.

## What Is a Knowledge Graph?

A knowledge graph is a way of storing information as **entities** and **relationships**. Entities are things — customers, products, invoices, support tickets, employees, suppliers. Relationships are the connections between them — a customer *purchased* a product, a product *is supplied by* a vendor, a support ticket *references* an invoice, an employee *handles* a ticket.

If you've ever drawn a diagram with boxes and arrows on a whiteboard to explain how your business works, you've already sketched a knowledge graph. The technology just makes that diagram queryable.

The key insight is that the **relationships are first-class data**. In a traditional database, you store a customer record and a product record, and the fact that the customer bought the product is buried in a line-item table that's hard to query across. In a graph, the connection between "Customer" and "Product" is an explicit, named, queryable thing. You can traverse it in any direction.

This sounds abstract, so let's make it concrete with an example.

### A Concrete Example

Imagine you run a business that sells industrial equipment parts. Your data lives in four systems:

- **CRM** (Odoo): customers, leads, sales opportunities
- **Accounting** (Invoice Ninja): invoices, payments, credit notes
- **Help Desk** (Chatwoot or osTicket): support tickets, conversations
- **Inventory** (NocoDB or Directus): products, stock levels, suppliers

In a knowledge graph, each of these becomes a set of connected nodes:

```
(Customer: Acme Manufacturing)
    |-- PURCHASED --> (Product: Hydraulic Pump HP-200)
    |-- RECEIVED_INVOICE --> (Invoice: INV-2026-1147)
    |-- OPENED_TICKET --> (Ticket: #4821 "Pump leaking after 3 weeks")
                          |-- REFERENCES --> (Product: Hydraulic Pump HP-200)
                          |-- HANDLED_BY --> (Employee: Sarah K.)
                          |-- RELATED_TO --> (Invoice: INV-2026-1147)

(Product: Hydraulic Pump HP-200)
    |-- SUPPLIED_BY --> (Supplier: PumpCorp)
    |-- IN_CATEGORY --> (Category: Hydraulic Systems)
    |-- STOCK_LEVEL --> 47 units
```

Now you can ask questions that span all four systems in a single query:

- "Show me all customers who bought the HP-200 pump and have open support tickets about it."
- "Which suppliers' products generate the most support tickets?"
- "What's the average time between purchase and first support ticket for products in the Hydraulic Systems category?"
- "Which customers have overdue invoices AND open support tickets?" (These are the ones at highest churn risk.)

Try writing that last query in SQL across four separate databases. It's possible, but it's painful, and it requires someone who understands all four schemas. In a graph database, it's a few lines of query language that any moderately technical person can read.

## The Tools: Open Source and Self-Hosted

You don't need a commercial graph database that costs $50,000 per year. The open source ecosystem for knowledge graphs has matured significantly. Here's the stack I recommend for a small or mid-size business:

### Graph Database: Neo4j Community Edition

**Neo4j** is the most widely used graph database in the world. The Community Edition is fully open source (GPLv3), self-hostable, and has no artificial limits on data size. It uses a query language called **Cypher** that's designed to be readable — it literally uses ASCII-art-style arrows to represent relationships.

A query that finds customers with open tickets referencing products they purchased looks like this:

```cypher
MATCH (c:Customer)-[:PURCHASED]->(p:Product)
MATCH (c)-[:OPENED_TICKET]->(t:Ticket)-[:REFERENCES]->(p)
WHERE t.status = 'open'
RETURN c.name, p.name, t.id, t.subject
```

If you can read the MATCH pattern visually — customer purchased product, customer opened ticket, ticket references product — you can write Cypher. It's that approachable.

Neo4j Community Edition runs in Docker, needs modest hardware (2GB RAM minimum, 4GB recommended for small datasets), and has a built-in browser interface for exploring your graph visually.

**Alternative:** If you want a pure open source option with no commercial licensing concerns at all, **Apache Jena** (with its TDB2 store and SPARQL query language) is a solid choice. It's part of the Apache Foundation and is used by major enterprises. The trade-off is that SPARQL is more complex than Cypher, and the tooling is less polished. For most businesses, Neo4j Community Edition is the better starting point.

### Data Integration: n8n

You already have data in your CRM, accounting system, help desk, and inventory. The knowledge graph starts empty. You need to populate it.

**n8n** is the open source workflow automation tool we've recommended throughout this blog. It's perfect for this job because it has built-in connectors for most business tools (or can call their REST APIs), and it can write to Neo4j via its HTTP Request node or the Neo4j node.

The pattern is straightforward:

1. **n8n** polls your CRM for new or updated customers every 15 minutes
2. For each new customer, n8n creates a `Customer` node in Neo4j
3. When an invoice is created in your accounting system, n8n creates an `Invoice` node and a `RECEIVED_INVOICE` relationship connecting it to the customer
4. When a support ticket is opened, n8n creates a `Ticket` node and connects it to both the customer and the referenced product

This is incremental. You don't need to migrate all your historical data at once. Start with one system — say, your CRM — and get customer nodes flowing into the graph. Then add invoices. Then add tickets. Each addition makes the graph more useful.

### Enrichment: Ollama (Local LLM)

This is where it gets interesting. Once your graph has data, you can use a local language model running through **Ollama** to enrich it.

For example, when a support ticket comes in, you can send the ticket text to Ollama and ask it to:

- **Classify the issue** — is this a defect, a shipping problem, a billing question, a user error?
- **Extract referenced products** — "the HP-200 pump" becomes a link to the Product node
- **Assess urgency** — based on language and customer tier
- **Identify sentiment** — is the customer frustrated, neutral, or happy?

Ollama runs on your own hardware. Your support ticket text never leaves your network. That matters for customer data, and it matters even more if you're in a regulated industry like healthcare, legal, or finance.

The enriched data gets written back to the graph as new properties on the Ticket node or as new relationships. Now you can query "show me all defect-classified tickets for products from Supplier X" — a question that would be impossible without the classification step.

### Visualization: Neo4j Bloom (Community) or Linkurious

Once you have a graph with real data, you'll want to explore it visually. **Neo4j Bloom** (included with Neo4j Community Edition in a limited form) lets you click around your graph, expand nodes, and see relationships rendered as an interactive network diagram. For business owners who aren't going to write Cypher queries, this is how they'll interact with the graph — by clicking and exploring.

For more advanced visualization, **Linkurious** has an open source edition (Linkurious Enterprise has a commercial version, but the core visualization library is open source). If you're comfortable with a bit more setup, it provides a polished exploration interface.

## A Practical Build Plan

Let's get concrete. Here's how to build a knowledge graph for a 20-person business over a few weekends, without disrupting any existing systems.

### Phase 1: Set Up Neo4j (Weekend 1, Day 1)

Deploy Neo4j Community Edition using Docker Compose:

```yaml
version: '3.8'
services:
  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"   # Browser UI
      - "7687:7687"   # Bolt protocol
    environment:
      - NEO4J_AUTH=neo4j/your-strong-password
      - NEO4J_PLUGINS=["apoc"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    restart: unless-stopped

volumes:
  neo4j_data:
  neo4j_logs:
```

The APOC plugin is important — it provides utility functions for working with data that you'll need during the loading phase. Once the container is up, open `http://your-server:7474` in a browser, log in with your password, and you'll see the Neo4j Browser. You're ready to create nodes.

### Phase 2: Connect Your CRM (Weekend 1, Day 2)

In n8n, create a workflow that:

1. Triggers on a schedule (every 15 minutes)
2. Calls your CRM's API (Odoo, SuiteCRM, or whatever you use) to fetch customers created or updated since the last run
3. For each customer, runs a Cypher `MERGE` statement via the Neo4j node:

```cypher
MERGE (c:Customer {crm_id: $customer_id})
SET c.name = $name,
    c.email = $email,
    c.tier = $tier,
    c.last_updated = $timestamp
```

`MERGE` is important here — it creates the node if it doesn't exist and updates it if it does. This makes your sync idempotent. If n8n re-runs the same batch, nothing breaks.

Run it once to backfill existing customers, then let the scheduled workflow keep it in sync going forward.

### Phase 3: Add Invoices and Products (Weekend 2)

Repeat the pattern for your accounting system and inventory system:

- When an invoice is created → create `Invoice` node, `RECEIVED_INVOICE` relationship from Customer, `LINE_ITEM` relationships to Product nodes
- When a product is created or updated → create or update `Product` node, `SUPPLIED_BY` relationship to Supplier node
- When a payment is recorded → create `Payment` node, `PAYED` relationship from Customer to Invoice

Each integration is a separate n8n workflow. This keeps things modular — if one system changes its API, you fix one workflow, not a monolithic pipeline.

### Phase 4: Add Support Tickets with AI Enrichment (Weekend 3)

This is where Ollama comes in. Create an n8n workflow that triggers when a new support ticket is created:

1. Fetch the ticket details from your help desk
2. Send the ticket subject and body to Ollama (running locally) with a prompt like:

```
You are a support ticket classifier. Analyze this support ticket and return JSON with:
- category: one of [defect, shipping, billing, user-error, question, other]
- product_references: list of product names or SKUs mentioned
- urgency: one of [low, medium, high, critical]
- sentiment: one of [positive, neutral, negative, frustrated]

Ticket subject: {{ $json.subject }}
Ticket body: {{ $json.body }}
```

3. Parse the JSON response from Ollama
4. Create the `Ticket` node in Neo4j with the enriched properties
5. Create `REFERENCES` relationships to any Product nodes matching the extracted product references
6. Create `OPENED_TICKET` relationship from the Customer node

Now your graph isn't just a mirror of your existing data — it's enriched with AI-generated classifications that make cross-system analysis possible.

### Phase 5: Start Asking Questions (Weekend 3, afternoon)

Once you have customers, products, invoices, and enriched tickets flowing into the graph, you can start asking real business questions. Here are five queries that demonstrate the value:

**1. Churn risk identification:**
```cypher
MATCH (c:Customer)-[:RECEIVED_INVOICE]->(i:Invoice)
WHERE i.status = 'overdue'
MATCH (c)-[:OPENED_TICKET]->(t:Ticket)
WHERE t.sentiment = 'frustrated' OR t.urgency = 'high'
RETURN c.name, count(t) as frustrated_tickets, sum(i.amount) as overdue_amount
ORDER BY overdue_amount DESC
```

**2. Product quality red flags:**
```cypher
MATCH (p:Product)<-[:REFERENCES]-(t:Ticket {category: 'defect'})
WITH p, count(t) as defect_count
MATCH (p)<-[:PURCHASED]-(c:Customer)
RETURN p.name, defect_count, count(DISTINCT c) as customers_affected
ORDER BY defect_count DESC
```

**3. Supplier risk assessment:**
```cypher
MATCH (s:Supplier)<-[:SUPPLIED_BY]-(p:Product)<-[:REFERENCES]-(t:Ticket {category: 'defect'})
RETURN s.name, count(t) as defect_tickets, count(DISTINCT p) as products_with_issues
ORDER BY defect_tickets DESC
```

**4. Upsell opportunities:**
```cypher
MATCH (c:Customer)-[:PURCHASED]->(p1:Product)-[:IN_CATEGORY]->(cat:Category)
MATCH (p2:Product)-[:IN_CATEGORY]->(cat)
WHERE NOT (c)-[:PURCHASED]->(p2)
AND p1 <> p2
RETURN c.name, cat.name, collect(p2.name) as cross_sell_candidates
```

**5. Support burden by customer tier:**
```cypher
MATCH (c:Customer)-[:OPENED_TICKET]->(t:Ticket)
RETURN c.tier, count(t) as total_tickets,
       avg(CASE WHEN t.category = 'user-error' THEN 1 ELSE 0 END) as user_error_rate
ORDER BY total_tickets DESC
```

Each of these queries would require joining data across four systems if you were working with them separately. In the graph, they're straightforward traversals. That's the core value proposition.

## What This Is Not

Let me be clear about what a knowledge graph won't do for you, because the hype around "AI knowledge graphs" has gotten out of hand.

**It's not a replacement for your existing systems.** Your CRM still manages your sales pipeline. Your accounting system still handles your books. The knowledge graph is a read-oriented analytical layer that connects them. It's not where you enter data — it's where you analyze it.

**It's not a magic AI that answers any question.** The graph is only as good as the data you feed it and the relationships you define. If you don't connect support tickets to products, you can't query that relationship. Building the graph requires thought about what connections matter to your business.

**It's not a weekend project for a 5-person team with no technical capacity.** Setting up Neo4j and building n8n integrations requires someone who's comfortable with Docker, APIs, and basic query languages. If that's not you, that's exactly what we're here for — but I want to be honest about the effort involved.

**It doesn't require a huge server.** A knowledge graph for a business with 10,000 customers, 5,000 products, and 50,000 transactions will run comfortably on a $20/month VPS with 4GB of RAM. Graph databases are efficient for this kind of connected data. You're not building Google's Knowledge Graph — you're building a practical tool for a 20-person company.

## Maintenance and Realistic Expectations

Once your graph is running, maintenance is modest. The n8n workflows keep it updated automatically. You'll occasionally need to:

- **Add a new entity type** when you connect a new system (e.g., adding "Employee" nodes when you integrate your HR system)
- **Adjust enrichment prompts** in Ollama if the ticket classification quality isn't meeting your needs
- **Clean up duplicate nodes** if your deduplication logic in n8n isn't perfect (this is where the APOC plugin helps — it has procedures for merging duplicate nodes)
- **Monitor disk usage** — graphs grow, but not explosively. A year of data for a 20-person business will be well under 1GB.

The biggest ongoing investment is **thinking about what relationships matter**. When you first build the graph, you'll connect the obvious things (customer → invoice → product). Over time, you'll discover that connecting less obvious things — like linking support tickets to the specific employee who handled them, or linking products to the marketing campaign that drove their purchase — unlocks insights you didn't expect.

## When Does This Make Sense?

A knowledge graph is worth building when you have **three or more business systems that don't share data well**, and you find yourself regularly doing manual cross-referencing to answer business questions.

If you're a 3-person team using one CRM and nothing else, you don't need this. If you're a 50-person company with a CRM, accounting system, help desk, inventory manager, project management tool, and marketing automation platform — and your operations manager spends half their day pulling data from all of them into spreadsheets — a knowledge graph will save you significant time and reveal patterns you're currently missing.

The sweet spot is businesses with 15–200 employees and 3+ disconnected data systems. That's where the manual cross-referencing cost is high enough to justify the build, and the data volume is large enough that patterns are genuinely hidden without a graph.

## Wrapping Up

A knowledge graph is one of those tools that sounds more complex than it is. The concept is simple: connect your data so you can ask questions across it. The implementation is approachable: Neo4j Community Edition for storage, n8n for data integration, Ollama for AI enrichment, all open source and self-hosted.

The payoff is real. Instead of five logins and a spreadsheet to answer "which customers are at churn risk," you run one query. Instead of guessing which products have quality issues, you let the graph show you the defect-ticket clusters by supplier. Instead of cross-referencing invoices and support tickets manually, you let the relationships do the work.

Start small. Connect your CRM. Get customer nodes flowing. Then add one more system at a time. Within a month, you'll have a graph that answers questions you currently can't ask — and that's when the tool starts paying for itself.

---

*Want help building a knowledge graph for your business? [Contact ARDOT Consulting](/#contact) — we specialize in open source automation and data integration for small and mid-size businesses. We'll help you connect your systems, set up the workflows, and start getting answers from your data. No hype, no vendor lock-in, just practical solutions.*