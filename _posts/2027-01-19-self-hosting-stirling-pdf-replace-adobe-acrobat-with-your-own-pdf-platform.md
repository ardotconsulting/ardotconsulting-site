---
layout: post
title: "Self-Hosting Stirling-PDF: Replace Adobe Acrobat With Your Own PDF Platform"
date: 2027-01-19
author: "ARDOT Consulting"
tags: [stirling-pdf, pdf, self-hosting, open-source, docker, document-management, adobe-alternative]
excerpt: "Adobe Acrobat Pro costs $240 per user per year. Stirling-PDF is a 97,000-star open source PDF platform you can self-host — merge, split, convert, sign, redact, and automate PDFs without sending documents to the cloud."
---

# Self-Hosting Stirling-PDF: Replace Adobe Acrobat With Your Own PDF Platform

Every business deals with PDFs. Contracts, invoices, proposals, reports, forms — they all arrive as PDFs, and they all need something done to them. Merge two files. Split a 200-page document. Add a signature. Redact sensitive information. Convert to Word for editing. Compress a file that's too big to email.

The default answer for most businesses is Adobe Acrobat Pro. At $20–25 per user per month, it adds up fast — a 10-person team pays $2,400–3,000 per year just to edit PDFs. And every document you touch passes through Adobe's cloud services, whether you want it to or not.

There's a better way. [Stirling-PDF](https://github.com/Stirling-Tools/Stirling-PDF) is an open source PDF platform with over 97,000 GitHub stars that does almost everything Acrobat does — merge, split, convert, sign, redact, compress, watermark, OCR — and you can run it on your own server. No per-user licensing. No documents leaving your network. No subscription that increases every year.

Here's what it does, how to deploy it, and when it makes sense for your business.

## What Stirling-PDF Actually Does

Stirling-PDF is a web-based PDF toolkit. You open it in a browser, upload a file (or files), pick an operation, and download the result. The processing happens entirely on your server — nothing is sent to a third-party API.

The feature list is extensive. Here are the operations most businesses actually use:

**Merging and splitting.** Combine multiple PDFs into one. Split a large PDF into individual pages or page ranges. Extract specific pages. Reorder pages within a document. If you've ever manually assembled a 50-page proposal from individual section PDFs, this alone pays for the setup time.

**Conversion.** Convert PDF to Word, Excel, HTML, PNG, JPEG, or plain text. Convert the other direction too — Word, Excel, images, HTML, and Markdown to PDF. This covers 90% of the "I need to edit this PDF" problem: convert to Word, make your changes, convert back.

**Signing and forms.** Add signature images to documents. Fill form fields. Create new form fields in existing PDFs. For businesses that need basic e-signing without a full platform like Documenso, this handles the common cases.

**Security.** Add password protection. Set permissions (prevent copying, printing, editing). Remove passwords from documents you own. Redact content by drawing boxes over sensitive text — the redacted area is actually removed from the document, not just covered with a black rectangle.

**Page manipulation.** Rotate pages. Crop pages. Add page numbers. Add headers and footers. Add watermarks. Scale or resize pages to different paper sizes.

**OCR (optical character recognition).** Turn scanned documents into searchable, selectable text. If you receive scanned invoices or contracts as image-only PDFs, OCR makes them indexable and copy-pasteable.

**Compression.** Reduce file size without visible quality loss. Useful when a PDF is too large to email — many email systems cap attachments at 10 or 25 MB.

That's not the complete list. Stirling-PDF includes over 50 operations. The full catalog is in their [documentation](https://docs.stirlingpdf.com).

## Why This Matters for Small Businesses

Three reasons.

**Cost.** Adobe Acrobat Pro is $20–25 per user per month. For a team of 10, that's $2,400–3,000 annually. Stirling-PDF runs on a server you already have (or a $5/month VPS) with no per-user fees. Everyone in your company uses it through a browser.

**Privacy.** When you edit a PDF in Acrobat's online services, that document is uploaded to Adobe's servers. Contracts, financial statements, client information — all processed on someone else's infrastructure. Stirling-PDF processes everything locally. Your documents never leave your network. For law firms, healthcare providers, financial services, and any business handling confidential client data, this is the difference between "probably fine" and "definitely compliant."

**Automation.** Stirling-PDF has a full REST API. You can integrate it into automated workflows — n8n pipelines that merge incoming PDFs, scripts that convert and file documents automatically, scheduled jobs that compress and archive reports. Adobe's API requires enterprise licensing and rate-limited cloud calls. Stirling-PDF's API is yours, unlimited, on your hardware.

## Deploying Stirling-PDF with Docker

Stirling-PDF runs as a Docker container. If you already have Docker installed (and if you've been following this blog, you probably do), deployment takes about two minutes.

### The Quick Start

Create a directory for Stirling-PDF and a `docker-compose.yml` file:

```yaml
version: "3.8"
services:
  stirling-pdf:
    image: docker.stirlingpdf.com/stirlingtools/stirling-pdf:latest
    container_name: stirling-pdf
    ports:
      - "8080:8080"
    volumes:
      - ./trainingData:/usr/share/tessdata        # OCR training data
      - ./extraConfigs:/configs                   # custom config files
      - ./logs:/logs
    environment:
      - DOCKER_ENABLE_SECURITY=false
      - LANGS=en_US
    restart: unless-stopped
```

Then start it:

```bash
docker compose up -d
```

Open `http://localhost:8080` in your browser. That's it — you have a fully functional PDF platform.

### Production Setup with HTTPS

For a server accessible to your team, you'll want HTTPS. The simplest approach is to put Stirling-PDF behind [Caddy](https://caddyserver.com), which handles TLS certificates automatically:

```yaml
version: "3.8"
services:
  stirling-pdf:
    image: docker.stirlingpdf.com/stirlingtools/stirling-pdf:latest
    container_name: stirling-pdf
    volumes:
      - ./trainingData:/usr/share/tessdata
      - ./extraConfigs:/configs
      - ./logs:/logs
    environment:
      - DOCKER_ENABLE_SECURITY=false
      - LANGS=en_US
    restart: unless-stopped
    networks:
      - pdf-net

  caddy:
    image: caddy:2
    container_name: caddy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    restart: unless-stopped
    networks:
      - pdf-net

volumes:
  caddy_data:
  caddy_config:

networks:
  pdf-net:
```

And a minimal `Caddyfile`:

```
pdf.yourcompany.com {
    reverse_proxy stirling-pdf:8080
}
```

Point your DNS to the server, run `docker compose up -d`, and Caddy handles the TLS certificate automatically. Your team accesses Stirling-PDF at `https://pdf.yourcompany.com`.

### Enabling OCR

OCR requires Tesseract language data. The container includes English by default. To add more languages, set the `LANGS` environment variable:

```yaml
environment:
  - LANGS=en_US,es_ES,fr_FR,de_DE
```

The first time the container starts with new languages, it downloads the Tesseract training data. Subsequent restarts use the cached data in the `trainingData` volume.

## Automating PDF Workflows with the API

The real power of Stirling-PDF for small businesses isn't the web interface — it's the API. Every operation available in the UI is available as a REST endpoint. This means you can build automated PDF workflows without any human interaction.

Here's a practical example. Say your sales team sends proposals as individual section PDFs that need to be merged, a cover page added, and the result compressed before emailing to the client. With n8n and Stirling-PDF, this becomes a workflow:

1. **Trigger.** An n8n webhook receives the section PDFs (uploaded by the sales rep through a simple form).
2. **Merge.** n8n calls Stirling-PDF's merge endpoint (`POST /api/v1/general/merge-pdfs`) with the uploaded files.
3. **Add cover page.** n8n calls the merge endpoint again, prepending a template cover page stored on the server.
4. **Compress.** n8n calls the compression endpoint (`POST /api/v1/general/compress-pdf`) to reduce the file size for email.
5. **Deliver.** n8n sends the final PDF via email or uploads it to Nextcloud, and posts a notification in Mattermost.

No one manually opens Acrobat. No one drags files around. The entire process takes seconds and runs on your infrastructure.

Other automation use cases:

- **Invoice processing.** A watched email inbox receives invoice PDFs. n8n extracts text using Stirling-PDF's PDF-to-text endpoint, passes it to Ollama for structured data extraction, and files the result in Odoo or ERPNext.
- **Report assembly.** A scheduled job pulls weekly metrics from Metabase as PDFs, merges them into a single report with a generated cover page, and emails it to stakeholders.
- **Document redaction.** Incoming legal documents are automatically redacted — removing personally identifiable information — before being filed in Paperless-ngx.

The API documentation is available within the application at `/api-docs` (Swagger UI), so you can explore endpoints interactively.

## Stirling-PDF vs Adobe Acrobat: An Honest Comparison

| Feature | Adobe Acrobat Pro | Stirling-PDF |
|---------|------------------|-------------|
| Price | $20–25/user/month | Free (self-hosted) |
| Document privacy | Cloud processing | Local processing |
| Merge/split | Yes | Yes |
| Convert to Office formats | Yes | Yes |
| OCR | Yes | Yes (via Tesseract) |
| E-signatures | Yes (via Adobe Sign) | Basic (image signatures, form fields) |
| Redaction | Yes | Yes |
| Compression | Yes | Yes |
| API access | Enterprise plan only | Included, unlimited |
| User limit | Per-seat licensing | Unlimited users |
| Desktop app | Yes | Yes (desktop builds available) |
| Browser-based | Yes (cloud) | Yes (self-hosted) |
| Setup required | None | Docker deployment |

Stirling-PDF wins on cost, privacy, API access, and user limits. Acrobat wins on setup simplicity (no deployment needed) and has more polished e-signature workflows. For most small businesses that need PDF manipulation — not a full e-signature platform — Stirling-PDF covers everything you need.

If you need formal e-signatures with audit trails and legal compliance, pair Stirling-PDF with [Documenso](https://documenso.com) (open source, AGPL-3.0) for signing workflows. Stirling-PDF handles the manipulation; Documenso handles the signing. Both self-hosted, both free.

## Licensing

Stirling-PDF is primarily MIT licensed. The core application — all the PDF operations, the web interface, the API — is open source under the MIT License, one of the most permissive licenses available. Some specific subdirectories (proprietary features, SaaS components, the desktop editor) have separate licenses, but the self-hosted community edition you'd deploy with Docker is MIT.

This means you can use it commercially, modify it, and distribute it without licensing concerns. Always verify the current license at the [repository](https://github.com/Stirling-Tools/Stirling-PDF/blob/main/LICENSE) before making business decisions.

## Hardware Requirements

Stirling-PDF is lightweight compared to most business software. For a small team (up to 20 concurrent users):

- **CPU:** 2 cores minimum, 4 cores recommended (OCR and conversion are CPU-intensive)
- **RAM:** 2 GB minimum, 4 GB recommended
- **Disk:** 1 GB for the application, plus temporary working space for file processing
- **Network:** Minimal — files are uploaded, processed, and downloaded

If you're already running Docker services like n8n, Nextcloud, or Plausible, Stirling-PDF can share the same server. It doesn't need a dedicated machine.

For OCR-heavy workloads (processing hundreds of scanned pages), add more CPU and RAM. Tesseract OCR is the bottleneck — it's single-threaded per document, so more cores let you process multiple documents in parallel.

## When It Makes Sense

**Self-host Stirling-PDF if:**

- You have 5+ people who regularly edit or manipulate PDFs
- You handle confidential documents (legal, financial, healthcare) and can't use cloud PDF services
- You want to automate PDF workflows through n8n or scripts
- You're already self-hosting other tools and have Docker running

**Skip it (for now) if:**

- Only one or two people occasionally edit PDFs — a one-time Acrobat license may be simpler
- You need advanced e-signature workflows with legal audit trails — use Documenso instead
- You don't have a server or aren't comfortable with Docker — though the setup is genuinely simple

## Getting Started

The fastest way to try Stirling-PDF is the one-line Docker command:

```bash
docker run -p 8080:8080 docker.stirlingpdf.com/stirlingtools/stirling-pdf
```

Open `http://localhost:8080`, upload a PDF, and try a few operations. If it does what you need — and for most businesses, it will — move to the Docker Compose setup above for a permanent deployment.

The [official documentation](https://docs.stirlingpdf.com) covers advanced configuration, security settings, multi-language support, and the full API reference.

---

PDF manipulation shouldn't cost thousands of dollars per year or require sending your documents to a third-party cloud. Stirling-PDF gives you a complete, open source PDF platform that runs on your own server, integrates with your automation workflows, and scales to your entire team without per-seat fees.

If you want help setting up Stirling-PDF or building automated PDF workflows for your business, [get in touch](/#contact) — we'll help you deploy it, connect it to your existing tools, and start saving those subscription fees.