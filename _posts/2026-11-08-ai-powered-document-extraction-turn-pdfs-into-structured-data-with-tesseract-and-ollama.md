---
layout: post
title: "AI-Powered Document Extraction: Turn PDFs Into Structured Data with Tesseract and Ollama"
date: 2026-11-08
author: "ARDOT Consulting"
tags: [document-extraction, tesseract, ollama, ocr, automation, open-source]
excerpt: "Extract text from PDFs and scanned documents with Tesseract OCR, then turn it into clean structured data using a local LLM — all with open source tools running on your own hardware."
---

Every business has a document problem. Invoices arrive as PDFs. Contracts come in as scanned images. Receipts pile up in email attachments. Someone — usually you or an admin — manually types the key details into a spreadsheet, an accounting system, or a CRM. It's slow, error-prone, and frankly nobody enjoys doing it.

What if you could point a script at a folder of PDFs and have it spit out a clean spreadsheet with vendor names, invoice numbers, dates, and line items — automatically, and without sending a single document to a third-party API?

That's exactly what we'll build in this guide, using two open source tools: **Tesseract OCR** for extracting raw text from documents, and **Ollama** for turning that messy text into structured, usable data. Both run on your own hardware. No cloud APIs, no per-page pricing, no data leaving your network.

## Why Not Just Use a SaaS Document Processing Tool?

There are plenty of cloud-based document extraction services. They're convenient. They also cost anywhere from $0.05 to $0.50 per page, lock your data behind their infrastructure, and often require you to send sensitive financial or legal documents to a third party.

For a small business processing 500 invoices a month at $0.10/page, that's $50/month — $600/year — just for OCR. And you're trusting a vendor with every document you process.

The open source approach costs nothing per page after setup. Your data stays on your machine. You can customize the extraction logic for your specific document types. And because the tools are mature and well-maintained, you're not sacrificing much in accuracy.

## The Two-Stage Pipeline

Here's the architecture:

```
PDF/Scanned Image
       │
       ▼
  ┌─────────┐
  │ Tesseract │  ──► Raw text (messy, unstructured)
  │   OCR     │
  └─────────┘
       │
       ▼
  ┌─────────┐
  │  Ollama   │  ──► Structured JSON (clean, typed fields)
  │  (LLM)    │
  └─────────┘
       │
       ▼
  Spreadsheet / Database / API
```

**Stage 1: Tesseract** extracts raw text from the document. For digital PDFs, this is straightforward. For scanned images, Tesseract performs optical character recognition — identifying letters and numbers from pixel patterns.

**Stage 2: Ollama** takes that raw text (which is often messy — weird line breaks, missing spaces, garbled characters) and extracts the specific fields you care about, returning them as structured JSON that you can pipe into any system.

## Prerequisites

You'll need:

- A machine with Python 3.10+ (any Linux distro or macOS works)
- Docker (for running Tesseract and Ollama in containers, or install both natively)
- 8GB+ RAM (16GB recommended if you're running a local LLM)

## Step 1: Set Up Tesseract OCR

Tesseract is the most widely used open source OCR engine, originally developed at HP and now maintained by Google contributors. It supports 100+ languages and handles most printed documents well.

### Install Tesseract

On Ubuntu/Debian:

```bash
sudo apt install tesseract-ocr tesseract-ocr-eng
```

On macOS (via Homebrew):

```bash
brew install tesseract
```

Or use Docker (no system install needed):

```bash
docker pull tesseractshadow/re4tesseract:latest
```

### Test It

Grab any scanned document or image with text and run:

```bash
tesseract invoice_scan.png stdout
```

You should see the extracted text printed to your terminal. It won't be perfect — Tesseract struggles with low-quality scans, unusual fonts, and complex layouts — but for standard business documents (invoices, receipts, forms), it works reliably.

### Extract Text from PDFs

Tesseract works on images, not PDFs directly. For PDFs, you first need to convert pages to images. Here's a Python script that handles both cases:

```python
import subprocess
import tempfile
import os

def extract_text_from_document(file_path, lang='eng'):
    """
    Extract text from a PDF or image file using Tesseract OCR.
    Returns the raw extracted text as a string.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    if ext == '.pdf':
        # Convert PDF pages to images using pdftoppm (part of poppler-utils)
        with tempfile.TemporaryDirectory() as tmpdir:
            # Convert to 300 DPI PNG images
            subprocess.run([
                'pdftoppm', '-png', '-r', '300',
                file_path, os.path.join(tmpdir, 'page')
            ], check=True)
            
            # OCR each page
            all_text = []
            for img_file in sorted(os.listdir(tmpdir)):
                if img_file.endswith('.png'):
                    img_path = os.path.join(tmpdir, img_file)
                    result = subprocess.run(
                        ['tesseract', img_path, 'stdout', '-l', lang],
                        capture_output=True, text=True
                    )
                    all_text.append(result.stdout)
            
            return '\n---PAGE BREAK---\n'.join(all_text)
    
    elif ext in ('.png', '.jpg', '.jpeg', '.tiff', '.bmp'):
        result = subprocess.run(
            ['tesseract', file_path, 'stdout', '-l', lang],
            capture_output=True, text=True
        )
        return result.stdout
    
    else:
        raise ValueError(f"Unsupported file type: {ext}")
```

Install `poppler-utils` for the PDF conversion:

```bash
sudo apt install poppler-utils   # Ubuntu/Debian
brew install poppler             # macOS
```

## Step 2: Set Up Ollama

Ollama lets you run large language models locally — no API keys, no per-token charges, no data sent to external servers. It's the missing piece that turns raw OCR text into clean, structured data.

### Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Pull a Model

For structured data extraction, you want a model that's good at following instructions and producing JSON. **Llama 3.2** (3B parameter) is lightweight and fast — great for this task:

```bash
ollama pull llama3.2
```

If you have more RAM and want better accuracy, try Qwen 2.5 (7B):

```bash
ollama pull qwen2.5
```

Verify it's working:

```bash
ollama run llama3.2 "Say hello in JSON format: {\"message\": \"...\"}"
```

## Step 3: Turn Raw Text Into Structured Data

Now for the magic. We'll send Tesseract's raw output to Ollama with a prompt that asks for specific fields in JSON format.

### The Extraction Prompt

The key is a well-structured prompt that tells the LLM exactly what to extract and how to format it:

```python
import json
import requests

def extract_structured_data(raw_text, document_type='invoice'):
    """
    Send raw OCR text to Ollama and get structured JSON back.
    """
    prompts = {
        'invoice': """You are a document extraction assistant. Extract the following fields 
from this invoice text and return them as a JSON object. If a field is not present, 
use null.

Fields to extract:
- vendor_name: The company issuing the invoice
- invoice_number: The invoice/reference number
- invoice_date: The date of the invoice (YYYY-MM-DD format)
- due_date: The payment due date (YYYY-MM-DD format, null if not specified)
- total_amount: The total amount due (number only, no currency symbol)
- currency: The currency code (USD, EUR, GBP, etc.)
- line_items: Array of objects, each with description, quantity, and unit_price
- payment_terms: Payment terms if specified (e.g., "Net 30")

Return ONLY the JSON object, no other text.

Invoice text:
""",
        'receipt': """You are a document extraction assistant. Extract the following fields 
from this receipt text and return them as a JSON object. If a field is not present, 
use null.

Fields to extract:
- merchant_name: The store or merchant name
- receipt_date: The date (YYYY-MM-DD format)
- total_amount: The total amount (number only)
- currency: The currency code
- items: Array of objects with name and price
- payment_method: How payment was made (cash, card, etc.)

Return ONLY the JSON object, no other text.

Receipt text:
""",
        'contract': """You are a document extraction assistant. Extract the following fields 
from this contract text and return them as a JSON object. If a field is not present, 
use null.

Fields to extract:
- parties: Array of party names
- contract_date: The effective date (YYYY-MM-DD format)
- contract_value: The total contract value (number only)
- currency: The currency code
- term_months: The contract duration in months (number)
- key_obligations: Array of strings describing main obligations

Return ONLY the JSON object, no other text.

Contract text:
"""
    }
    
    prompt = prompts.get(document_type, prompts['invoice'])
    full_prompt = prompt + raw_text
    
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'llama3.2',
            'prompt': full_prompt,
            'stream': False,
            'format': 'json',  # Force JSON output
            'options': {
                'temperature': 0.1,  # Low temperature for consistent extraction
                'num_predict': 2000,
            }
        }
    )
    
    result = response.json()
    
    try:
        return json.loads(result['response'])
    except json.JSONDecodeError:
        # Sometimes the model wraps JSON in markdown code blocks
        text = result['response']
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        return json.loads(text.strip())
```

The `format: 'json'` parameter in the Ollama API forces the model to produce valid JSON. The `temperature: 0.1` setting keeps output consistent — you don't want creative variation when extracting invoice numbers.

## Step 4: Put It All Together

Here's the complete pipeline that processes a folder of documents:

```python
#!/usr/bin/env python3
"""
Document Extraction Pipeline
Processes all PDFs and images in a folder, extracts structured data,
and saves results to a CSV file.
"""

import os
import csv
import json
from datetime import datetime

# Import the functions from Steps 1 and 3
# (extract_text_from_document and extract_structured_data)

def process_folder(input_dir, output_csv, document_type='invoice'):
    """Process all documents in a folder and write results to CSV."""
    
    supported_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    results = []
    
    files = [f for f in os.listdir(input_dir) 
             if os.path.splitext(f)[1].lower() in supported_extensions]
    
    print(f"Found {len(files)} documents to process")
    
    for i, filename in enumerate(files, 1):
        file_path = os.path.join(input_dir, filename)
        print(f"  [{i}/{len(files)}] Processing {filename}...")
        
        try:
            # Stage 1: OCR
            raw_text = extract_text_from_document(file_path)
            
            if not raw_text.strip():
                print(f"    ⚠ No text extracted, skipping")
                continue
            
            # Stage 2: LLM extraction
            structured = extract_structured_data(raw_text, document_type)
            
            # Add metadata
            structured['source_file'] = filename
            structured['processed_at'] = datetime.now().isoformat()
            structured['extraction_status'] = 'success'
            
            results.append(structured)
            print(f"    ✓ Extracted: {structured.get('vendor_name', 'N/A')} — {structured.get('invoice_number', 'N/A')}")
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            results.append({
                'source_file': filename,
                'processed_at': datetime.now().isoformat(),
                'extraction_status': f'error: {str(e)}'
            })
    
    # Write to CSV
    if results:
        # Collect all unique field names across results
        fieldnames = set()
        for r in results:
            fieldnames.update(r.keys())
        
        # Order: standard fields first, then alphabetical
        priority_fields = ['source_file', 'vendor_name', 'invoice_number', 
                          'invoice_date', 'total_amount', 'currency', 
                          'extraction_status', 'processed_at']
        ordered_fields = [f for f in priority_fields if f in fieldnames]
        ordered_fields += sorted(fieldnames - set(priority_fields))
        
        with open(output_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=ordered_fields, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\n✓ Processed {len(results)} documents → {output_csv}")
        print(f"  Successful: {sum(1 for r in results if r.get('extraction_status') == 'success')}")
        print(f"  Failed: {sum(1 for r in results if r.get('extraction_status') != 'success')}")

if __name__ == '__main__':
    process_folder(
        input_dir='./invoices',
        output_csv='./extracted_invoices.csv',
        document_type='invoice'
    )
```

### Run It

```bash
mkdir -p invoices
# Drop some PDF invoices or scanned images into the invoices/ folder
python3 extract_pipeline.py
```

Output:

```
Found 3 documents to process
  [1/3] Processing invoice_001.pdf...
    ✓ Extracted: Acme Supply Co — INV-2027-0042
  [2/3] Processing invoice_002.png...
    ✓ Extracted: Brightpath LLC — BP-1187
  [3/3] Processing receipt_jan15.jpg...
    ✓ Extracted: Office Depot — null

✓ Processed 3 documents → extracted_invoices.csv
  Successful: 3
  Failed: 0
```

The resulting `extracted_invoices.csv` opens directly in LibreOffice Calc, Excel, or any spreadsheet tool — ready for review, import, or further processing.

## Tesseract OCR: What Affects Accuracy

Tesseract is powerful, but its accuracy depends heavily on input quality. Here's what matters:

| Factor | Good | Bad |
|--------|------|-----|
| Resolution | 300 DPI or higher | Under 150 DPI |
| Image quality | Sharp, high contrast | Blurry, faded |
| Background | White, clean | Colored, textured |
| Font | Standard, printed | Handwritten, decorative |
| Layout | Simple, single-column | Multi-column, rotated |
| Skew | Straight (0°) | Rotated 5°+ |

### Pre-processing for Better Results

If your scans are rough, a little pre-processing goes a long way. Here's a function that cleans up images before OCR:

```python
from PIL import Image, ImageFilter, ImageOps

def preprocess_image(image_path, output_path):
    """Apply basic pre-processing to improve OCR accuracy."""
    img = Image.open(image_path)
    
    # Convert to grayscale
    img = img.convert('L')
    
    # Increase contrast
    img = ImageOps.autocontrast(img, cutoff=5)
    
    # Slight sharpening
    img = img.filter(ImageFilter.SHARPEN)
    
    # Scale up if small (Tesseract prefers at least 300 DPI)
    width, height = img.size
    if width < 2000:
        scale = 2000 / width
        img = img.resize((int(width * scale), int(height * scale)), Image.LANCZOS)
    
    img.save(output_path)
    return output_path
```

Install Pillow: `pip install Pillow`

## Tesseract vs Other OCR Engines

Tesseract isn't the only option. Here's how it compares to alternatives:

| Tool | Type | Accuracy | Languages | Cost | Best For |
|------|------|----------|-----------|------|----------|
| Tesseract | Open source (local) | Good | 100+ | Free | Standard printed documents |
| PaddleOCR | Open source (local) | Very good | 90+ | Free | Complex layouts, multi-language |
| OCRmyPDF | Open source (wraps Tesseract) | Good | 100+ | Free | Adding OCR layer to PDFs |
| EasyOCR | Open source (local) | Very good | 80+ | Free | Mixed-quality scans |
| Cloud OCR services | SaaS | Excellent | Varies | $0.05-0.50/page | High-volume, complex docs |

For most small businesses, Tesseract handles 90%+ of documents correctly. If you're dealing with poor-quality scans or complex multi-column layouts, try PaddleOCR as a drop-in replacement.

**OCRmyPDF** is worth mentioning separately — it takes a PDF, adds an invisible OCR text layer, and saves it back as a searchable PDF. Perfect for archiving:

```bash
ocrmypdf --skip-text input.pdf output.pdf
```

The `--skip-text` flag tells it to only OCR pages that don't already have a text layer (useful for PDFs that are partially digital, partially scanned).

## Common Use Cases

This pipeline works for more than just invoices:

### Receipt Processing for Expense Reports

Change the `document_type` to `'receipt'` and you get merchant names, dates, totals, and item lists — ready to import into your expense tracking system.

### Contract Analysis

Set `document_type` to `'contract'` to extract parties, dates, values, and key obligations. Useful for legal teams managing a large volume of agreements.

### Form Data Entry

Customize the prompt to extract specific fields from any standardized form — job applications, intake forms, insurance claims. The LLM adapts to whatever structure you define.

### Email Attachment Processing

Pair this with n8n to automatically process email attachments:

```
Email arrives with PDF attachment
    → n8n saves attachment to watched folder
    → This pipeline runs automatically
    → Results pushed to Odoo / spreadsheet / database
```

## Performance and Scaling

On a modest machine (4-core CPU, 16GB RAM), here's what to expect:

| Document Type | Pages | Tesseract Time | Ollama Time | Total |
|---------------|-------|----------------|-------------|-------|
| Single-page invoice (image) | 1 | ~2s | ~3s | ~5s |
| 5-page PDF contract | 5 | ~15s | ~8s | ~23s |
| Single-page receipt (photo) | 1 | ~3s | ~4s | ~7s |

A folder of 100 single-page invoices processes in about 8-10 minutes. Not lightning fast, but compare that to manually typing 100 invoices — which would take a human 3-4 hours — and the value is clear.

### Speeding Things Up

- **Use a smaller model**: Llama 3.2 (3B) is 3-4x faster than Qwen 2.5 (7B) with only slightly lower extraction accuracy
- **Batch processing**: Process documents overnight with a cron job
- **GPU acceleration**: If you have a GPU, Ollama uses it automatically — extraction times drop to under 1 second per page
- **Parallel processing**: Run multiple Tesseract instances on different CPU cores

## When to Use This vs. a Managed Service

| Choose This Pipeline If... | Choose a SaaS OCR If... |
|---|---|
| You process <1,000 documents/month | You process 10,000+ documents/month |
| Documents contain sensitive data | Documents are non-sensitive |
| You want zero per-page costs | You need maximum accuracy on poor scans |
| You're comfortable with Python | You need a no-code solution |
| You want full control over data | You need rapid deployment with no setup |

There's no wrong answer. Some businesses use this pipeline for internal documents and a SaaS for customer-facing forms. The tools can coexist.

## A Note on Privacy

This is the part that matters most for many businesses. When you use a cloud OCR service, you're uploading every document to someone else's server. For invoices with vendor pricing, contracts with confidential terms, or patient records with health information, that's a real risk.

Tesseract and Ollama run entirely on your machine. No document ever leaves your network. There are no API logs on a third-party server. No risk of a vendor breach exposing your files. For businesses in regulated industries (healthcare, legal, finance), this isn't just a preference — it's often a compliance requirement.

## Getting Started Checklist

1. ☐ Install Tesseract: `sudo apt install tesseract-ocr`
2. ☐ Install poppler-utils: `sudo apt install poppler-utils`
3. ☐ Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
4. ☐ Pull a model: `ollama pull llama3.2`
5. ☐ Install Python dependencies: `pip install requests Pillow`
6. ☐ Create a folder of test documents
7. ☐ Run the pipeline script
8. ☐ Review the CSV output and adjust prompts as needed

## Wrapping Up

Document extraction doesn't have to mean manual data entry or expensive per-page APIs. With Tesseract for OCR and Ollama for structured extraction, you can build a pipeline that handles invoices, receipts, contracts, and forms — all on your own hardware, with zero per-page costs, and with complete data privacy.

The pipeline we built here processes a folder of documents and outputs a clean CSV. From there, you can import into Odoo for accounting, push to NocoDB for a searchable database, or trigger downstream workflows in n8n. The structured data becomes the input for everything else.

Start with a small batch — ten invoices, say — and see how the extraction quality looks. Tweak the prompt fields to match your specific document format. Within an afternoon, you'll have a working pipeline that saves hours of manual work every week.

**Need help setting this up for your business?** [Contact ARDOT Consulting](/) — we specialize in building document automation pipelines with open source tools that keep your data on your own infrastructure.
