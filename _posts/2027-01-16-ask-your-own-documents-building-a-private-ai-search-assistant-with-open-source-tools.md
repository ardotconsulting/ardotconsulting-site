---
layout: post
title: "Ask Your Own Documents: Building a Private AI Search Assistant with Open Source Tools"
date: 2027-01-16
author: "ARDOT Consulting"
tags: [rag, ai-search, ollama, qdrant, anythingllm, open-source, self-hosting, document-search, privacy, automation]
excerpt: "Your business has thousands of documents — contracts, policies, invoices, manuals — scattered across folders and systems. Generic AI chatbots can't search them, and sending them to the cloud is a non-starter. Here's how to build a private AI assistant that answers questions from your own documents, running entirely on your own hardware."
---

# Ask Your Own Documents: Building a Private AI Search Assistant with Open Source Tools

You know the feeling. You need to find a specific clause in a vendor contract from two years ago. Or you need to know what your return policy says about partial shipments. Or you want to check whether a specific expense category is reimbursable under your employee handbook. So you start digging — through shared drives, email attachments, filing cabinets, maybe a document management system if you've gotten that far.

If you're lucky, you find the document in five minutes. If you're not, you spend twenty minutes opening PDFs, skimming, and searching for keywords that may or may not match what you're looking for. And once you find the right document, you still have to read it to find the specific answer.

Now imagine typing a question — "What's our policy on remote work equipment stipends?" — and getting an answer in ten seconds, with a citation pointing to the exact page of your employee handbook. That's what a document-aware AI assistant does. And you can build one with open source tools, running on hardware you control, without sending a single file to anyone else's server.

This guide walks through how it works, what you need, and how to set it up — written for business owners, not developers.

## What We're Building (and What We're Not)

The thing we're building has a technical name: **RAG**, which stands for Retrieval-Augmented Generation. It sounds complicated, but the concept is simple:

1. You put all your business documents into a system that can search them by meaning, not just by keyword.
2. When you ask a question, the system finds the most relevant passages from your documents.
3. It hands those passages to a language model, which writes a natural-language answer backed by those passages.

The key difference from a generic chatbot: **the AI can only answer based on your documents.** It's not making things up from the internet. It's reading your stuff and summarizing what it finds.

What this is **not**: It's not a replacement for your document management system. It's not a legal oracle. It's not something you plug in and forget. It's a search and summarization layer that sits on top of your existing documents and makes them dramatically more useful.

## Why Not Just Use a Cloud AI Service?

You could upload your documents to a cloud AI service and ask questions. Some businesses do. But there are three problems:

**Your data leaves your control.** Contracts, financial statements, employee records, customer data — these are the documents that would benefit most from AI search, and they're also the documents you least want sitting on someone else's servers. Once uploaded, you're trusting a third party with your most sensitive information, and you're subjecting it to their retention policies, their training data practices, and their breach risk.

**It gets expensive fast.** Cloud AI services charge per query, per document, per token. A team of twenty people asking fifty questions a day adds up to real money — often more than the cost of running your own infrastructure.

**You're dependent on their roadmap.** The service changes pricing, deprecates features, or goes down, and you have no recourse. Your AI search capability is only as stable as the company providing it.

Self-hosting solves all three problems. Your data stays on your hardware. Your costs are fixed (the server you're already running). And the open source tools don't change their terms of service on a whim.

## The Open Source Stack

Here's what you need. All of these are free, open source, and run via Docker — the same deployment method we've used throughout this blog series.

| Component | Tool | What It Does |
|-----------|------|--------------|
| Language model | **Ollama** | Runs the AI model locally — the "brain" that reads passages and writes answers |
| Document ingestion | **AnythingLLM** (or Dify) | A web interface where you upload documents, ask questions, and manage your knowledge base |
| Vector database | **Qdrant** (or Chroma) | Stores your documents in a searchable format — the "index" that finds relevant passages |
| Workflow automation | **n8n** (optional) | Connects the system to your other tools — auto-ingesting new documents, routing answers to Slack/Matrix, etc. |

If that sounds like a lot, don't worry. AnythingLLM bundles most of this into a single Docker container and handles the connections for you. You can start simple and add components as you grow.

### A Note on Hardware

The language model is the one component that benefits from real hardware. You can run a smaller model (like Llama 3.2 3B or Qwen 2.5 7B) on a machine with 16GB of RAM and no GPU — it'll be slow (5-10 seconds per answer) but functional. For a production setup serving a team, you'll want either:

- A machine with 32GB+ RAM and a recent CPU (answers in 3-5 seconds with a 7B model)
- A machine with a used GPU like an RTX 3060 or A4000 (answers in 1-2 seconds with a larger model)

If you're already running a self-hosted stack (Nextcloud, Odoo, n8n, etc.), you can often add this to the same server if it has the RAM. The vector database and AnythingLLM itself are lightweight — it's the language model that needs resources.

## Setting It Up: A Practical Walkthrough

### Step 1: Install Ollama

Ollama runs language models on your server. Install it with a single command on Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Then pull a model. For document Q&A, a model that's good at reading comprehension and following instructions is what you want. Start with Qwen 2.5 7B — it's small, fast, and handles question-answering well:

```bash
ollama pull qwen2.5:7b
```

This downloads about 4.7GB. Once it's done, Ollama is running in the background, ready to answer queries.

### Step 2: Run AnythingLLM

AnythingLLM is the interface your team will actually use. It handles document upload, chunking (splitting documents into searchable pieces), vector storage, and the chat interface — all in one package.

Create a `docker-compose.yml` file:

```yaml
version: "3.8"
services:
  anythingllm:
    image: mintplexlabs/anythingllm:latest
    container_name: anythingllm
    ports:
      - "3001:3001"
    volumes:
      - anythingllm_storage:/app/server/storage
    environment:
      - STORAGE_DIR=/app/server/storage
    restart: unless-stopped

volumes:
  anythingllm_storage:
```

Run it:

```bash
docker compose up -d
```

Open `http://your-server-ip:3001` in a browser. You'll see a setup wizard. Here's what to configure:

1. **LLM Provider**: Select "Ollama" and enter `http://host.docker.internal:11434` as the URL. Select the `qwen2.5:7b` model you pulled.
2. **Vector Database**: AnythingLLM has a built-in vector store (LanceDB) that works fine for getting started. If you outgrow it, you can switch to Qdrant later.
3. **Embedding model**: Use the built-in `all-MiniLM-L6-v2` — it's small, fast, and good enough for most business document collections.

That's it. The system is running.

### Step 3: Create a Workspace and Upload Documents

AnythingLLM organizes documents into "workspaces." Think of a workspace as a folder of related documents that the AI can search within. You might create workspaces like:

- **Company Policies** — employee handbook, PTO policy, expense guidelines, remote work policy
- **Client Contracts** — all your client agreements and statements of work
- **Product Documentation** — user manuals, spec sheets, warranty terms
- **HR** — job descriptions, onboarding checklists, benefits summaries

To populate a workspace, you upload documents (PDF, Word, TXT, Markdown, HTML — most formats work). AnythingLLM processes them automatically: extracting text, splitting into chunks, and creating the searchable index.

A workspace with 200 documents takes about 10-15 minutes to fully index. You'll see a progress indicator. Once it's done, you can start asking questions.

### Step 4: Ask Questions

Open your workspace and type a question in the chat box. For example, in a "Company Policies" workspace:

> "How many vacation days does an employee with 3 years of tenure get?"

The system will:
1. Search the indexed documents for passages about vacation, tenure, and leave
2. Send the most relevant passages to the language model
3. Return an answer like: *"According to the Employee Handbook (page 12), employees with 3+ years of tenure receive 18 vacation days per year, plus 2 floating personal days."*

It also shows you which documents and passages it used to generate the answer, so you can verify it. This citation feature is critical — it means you can trust but verify, rather than blindly accepting AI output.

## Making It Useful: Practical Patterns

### Auto-Ingest New Documents

The biggest maintenance challenge is keeping your knowledge base current. If you upload 200 documents today but never add new ones, the system becomes stale. Use n8n to automate ingestion:

- **When a new contract is signed in Documenso** → automatically upload the final PDF to your "Client Contracts" workspace
- **When a new policy is added to BookStack** → sync it to your "Company Policies" workspace
- **When invoices are processed in Paperless-ngx** → index them in a "Finance" workspace

An n8n workflow for this is straightforward: a webhook trigger from your document system → an HTTP request to AnythingLLM's API to upload the file → a notification to your team chat that new content is available.

### Limit the Scope Per Question

One of the most useful features is workspace separation. If someone asks about vacation policy, the system only searches the Company Policies workspace — it doesn't pull in irrelevant results from client contracts or product manuals. This improves answer quality dramatically compared to dumping everything into one giant knowledge base.

If you do need cross-workspace search (e.g., "show me all documents related to client Acme Corp"), AnythingLLM supports "agent" mode that can search across multiple workspaces — but for day-to-day questions, scoped workspaces give better answers.

### Set Expectations With Your Team

This is a search and summarization tool, not an oracle. Tell your team:

- **Always check the citation.** If the answer cites the handbook, open the handbook and confirm. The AI is usually right, but it can misread context.
- **It's better at specific questions than broad ones.** "What's the deductible on our Bronze health plan?" works great. "Tell me about our benefits" produces a vague summary.
- **If a document isn't in the system, the AI can't answer.** Garbage in, garbage out. The most common failure is someone asking about a document that was never uploaded.

## What It Costs

Let's be concrete. Here's a realistic cost breakdown for a small business running this stack:

| Item | One-Time | Monthly |
|------|----------|---------|
| Server (used workstation, 32GB RAM, no GPU) | $400-600 | — |
| Server (with used RTX 3060 GPU) | $700-900 | — |
| Cloud VPS alternative (32GB RAM) | — | $80-120 |
| Electricity (on-premise server) | — | $15-25 |
| Ollama, AnythingLLM, Qdrant | $0 | $0 |
| **Total (on-premise, year 1)** | **$400-900** | **$15-25** |
| **Total (cloud VPS, year 1)** | **$0** | **$80-120** |

Compare that to a cloud AI document service at $20/user/month for a 15-person team — that's $300/month, or $3,600/year. The self-hosted stack pays for itself in 2-4 months, and your data never leaves your building.

## When This Makes Sense (and When It Doesn't)

**It makes sense if:**
- You have a large volume of text-based documents (contracts, policies, manuals, reports) that people search frequently
- Your team wastes significant time hunting for information in documents
- Your documents contain sensitive information you don't want on third-party servers
- You're already self-hosting other tools and have a server with spare capacity

**It doesn't make sense if:**
- You have fewer than ~50 documents — folder organization and full-text search (which Nextcloud and Paperless-ngx already provide) is sufficient
- Your documents are mostly spreadsheets or databases — RAG works on text, not tabular data. For structured data, use a proper reporting tool like Metabase.
- You don't have anyone who can spend a few hours on initial setup and ongoing maintenance

## A Realistic Timeline

- **Day 1**: Install Ollama and AnythingLLM. Upload a test workspace with 20-30 documents. Get familiar with asking questions and checking citations.
- **Week 1**: Create your production workspaces. Upload all relevant documents. Set up n8n auto-ingest for at least one document source.
- **Week 2**: Roll out to your team. Do a 30-minute demo. Collect feedback on what questions work well and what doesn't.
- **Month 1**: Tune workspace boundaries, add missing documents, adjust the model if needed (try a larger model like Qwen 2.5 14B if answer quality is poor).

This isn't a weekend project, but it's not a months-long initiative either. A motivated business owner or IT-literate team member can have a working system in a week and a polished one in a month.

## Keeping It Honest

A few things to be upfront about:

**Answer quality depends on model size.** A 7B model running on CPU will give you good-but-not-great answers. It might miss nuance in a complex contract clause. For high-stakes use (legal review, compliance questions), invest in a larger model and a GPU — or treat the AI's output as a first pass that a human verifies.

**Maintenance is real.** Documents need to be added when created and removed when obsolete. The system doesn't magically know when a policy has been superseded. Budget 30 minutes a week for housekeeping.

**It's not a replacement for proper document management.** You still need organized storage, version control, and access permissions (which Paperless-ngx, Nextcloud, or BookStack handle well). The AI search layer makes those documents more useful — it doesn't replace the need for them.

## Next Steps

If you've been building out a self-hosted stack — Paperless-ngx for documents, Nextcloud for files, BookStack for knowledge — adding an AI search layer is one of the highest-impact things you can do. It turns a static archive into an interactive resource. The setup is modest, the tools are mature, and the payoff is immediate: your team stops digging and starts asking.

Start small. One workspace, one model, twenty documents. See how it feels. Then expand.

If you want help designing a document AI setup tailored to your business — which model to run, how to organize workspaces, how to automate ingestion from your existing systems — [get in touch](/#contact). We specialize in practical, self-hosted automation for small businesses, and we'd be happy to help you get this running.
