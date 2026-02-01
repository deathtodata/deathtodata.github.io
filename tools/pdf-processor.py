#!/usr/bin/env python3
"""
PDF Processing Pipeline
=======================

Handles complex PDFs like ARK Big Ideas (120+ pages, images, charts, tables)

Requirements:
    brew install poppler    # for pdftotext, pdfimages, pdfinfo
    pip install PyMuPDF     # for better text extraction
    pip install Pillow      # for image handling
    
Usage:
    python3 pdf-processor.py ~/Downloads/ark-big-ideas-2026.pdf
    
Output:
    ark-big-ideas-2026/
    ├── metadata.json       # PDF info
    ├── full-text.txt       # All text
    ├── sections.json       # Chunked sections
    ├── images/             # Extracted images
    ├── analysis.json       # Ollama analysis per section
    └── summary.json        # Final structured output
"""

import subprocess
import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path

# =============================================================================
# CONFIG
# =============================================================================

CHUNK_SIZE = 3000  # Characters per chunk for Ollama
OLLAMA_MODEL = "llama2"  # Change to mistral, llama3, etc.
MAX_CHUNKS_TO_PROCESS = 50  # Limit for testing (set to None for all)

# =============================================================================
# HELPERS
# =============================================================================

def run(cmd, capture=True):
    """Run shell command"""
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    return result.stdout.strip() if capture else result.returncode

def ensure_dir(path):
    """Create directory if needed"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

# =============================================================================
# EXTRACTION
# =============================================================================

def get_pdf_info(pdf_path):
    """Get PDF metadata"""
    info = {}
    
    # Basic info from pdfinfo
    output = run(f'pdfinfo "{pdf_path}"')
    for line in output.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            info[key.strip().lower().replace(' ', '_')] = val.strip()
    
    return info

def extract_text(pdf_path, output_dir):
    """Extract all text from PDF"""
    txt_path = f"{output_dir}/full-text.txt"
    run(f'pdftotext -layout "{pdf_path}" "{txt_path}"')
    
    with open(txt_path, 'r', errors='ignore') as f:
        text = f.read()
    
    return text

def extract_images(pdf_path, output_dir):
    """Extract all images from PDF"""
    img_dir = ensure_dir(f"{output_dir}/images")
    run(f'pdfimages -png "{pdf_path}" "{img_dir}/img"')
    
    # List extracted images
    images = []
    for f in os.listdir(img_dir):
        if f.endswith('.png'):
            img_path = f"{img_dir}/{f}"
            size = os.path.getsize(img_path)
            # Skip tiny images (likely icons/bullets)
            if size > 5000:  # 5KB minimum
                images.append({
                    "file": f,
                    "path": img_path,
                    "size_bytes": size
                })
    
    return images

# =============================================================================
# CHUNKING
# =============================================================================

def chunk_by_pages(text):
    """Split text by page breaks"""
    pages = text.split('\f')
    return [p.strip() for p in pages if p.strip()]

def chunk_by_headers(text):
    """Try to split by section headers (ALL CAPS lines)"""
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_header = "Introduction"
    
    for line in lines:
        # Detect headers (lines that are mostly uppercase, 3+ words)
        stripped = line.strip()
        if (stripped.isupper() and 
            len(stripped) > 10 and 
            len(stripped.split()) >= 2 and
            not stripped.startswith('©')):
            # Save previous chunk
            if current_chunk:
                chunks.append({
                    "header": current_header,
                    "content": '\n'.join(current_chunk)
                })
            current_header = stripped
            current_chunk = []
        else:
            current_chunk.append(line)
    
    # Don't forget last chunk
    if current_chunk:
        chunks.append({
            "header": current_header,
            "content": '\n'.join(current_chunk)
        })
    
    return chunks

def chunk_by_size(text, size=CHUNK_SIZE):
    """Split into fixed-size chunks"""
    chunks = []
    
    # Try to break at paragraph boundaries
    paragraphs = text.split('\n\n')
    current = ""
    
    for para in paragraphs:
        if len(current) + len(para) > size:
            if current:
                chunks.append(current.strip())
            current = para
        else:
            current += "\n\n" + para
    
    if current.strip():
        chunks.append(current.strip())
    
    return chunks

# =============================================================================
# OLLAMA INTEGRATION
# =============================================================================

def ask_ollama(prompt, model=OLLAMA_MODEL):
    """Send prompt to Ollama"""
    # Escape for shell
    escaped = prompt.replace("'", "'\\''")
    result = run(f"ollama run {model} '{escaped}'")
    return result

def analyze_section(section_text, section_num, total_sections):
    """Analyze a single section with Ollama"""
    print(f"  Analyzing section {section_num}/{total_sections}...")
    
    prompt = f"""Analyze this section from an investment research report. Extract:

1. TOPIC: Main subject (1 line)
2. KEY_POINTS: Important insights (3-5 bullets)
3. NUMBERS: Any statistics, percentages, dollar amounts, growth rates
4. COMPANIES: Companies mentioned
5. TECHNOLOGIES: Technologies or trends discussed
6. PREDICTIONS: Any forecasts or predictions made

Be concise. Return structured text, not JSON.

SECTION TEXT:
{section_text[:2500]}
"""
    
    response = ask_ollama(prompt)
    return response

def generate_summary(all_analyses, pdf_name):
    """Generate overall summary from all section analyses"""
    print("Generating overall summary...")
    
    # Combine key points from all sections
    combined = "\n\n---\n\n".join([
        f"Section {i+1}:\n{a}" 
        for i, a in enumerate(all_analyses[:20])  # Limit context
    ])
    
    prompt = f"""Based on these section analyses from the {pdf_name} research report, create:

1. EXECUTIVE_SUMMARY: 3-4 sentence overview
2. TOP_THEMES: The 5 most important themes/trends
3. KEY_PREDICTIONS: The 5 most significant predictions with numbers
4. COMPANIES_TO_WATCH: Top 10 companies mentioned most positively
5. INVESTMENT_IMPLICATIONS: 3-5 actionable insights

SECTION ANALYSES:
{combined[:6000]}
"""
    
    response = ask_ollama(prompt)
    return response

# =============================================================================
# MAIN PIPELINE
# =============================================================================

def process_pdf(pdf_path):
    """Full processing pipeline"""
    pdf_path = os.path.expanduser(pdf_path)
    
    if not os.path.exists(pdf_path):
        print(f"ERROR: File not found: {pdf_path}")
        sys.exit(1)
    
    pdf_name = os.path.basename(pdf_path).replace('.pdf', '')
    output_dir = os.path.dirname(pdf_path) + '/' + pdf_name
    ensure_dir(output_dir)
    
    print(f"\n{'='*60}")
    print(f"PDF PROCESSOR")
    print(f"{'='*60}")
    print(f"Input:  {pdf_path}")
    print(f"Output: {output_dir}")
    print(f"{'='*60}\n")
    
    # Step 1: Metadata
    print("[1/6] Extracting metadata...")
    metadata = get_pdf_info(pdf_path)
    metadata['processed_at'] = datetime.now().isoformat()
    metadata['source_file'] = pdf_path
    
    with open(f"{output_dir}/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  Pages: {metadata.get('pages', 'unknown')}")
    
    # Step 2: Text extraction
    print("[2/6] Extracting text...")
    full_text = extract_text(pdf_path, output_dir)
    print(f"  Extracted {len(full_text):,} characters")
    
    # Step 3: Image extraction
    print("[3/6] Extracting images...")
    images = extract_images(pdf_path, output_dir)
    print(f"  Extracted {len(images)} images (>5KB)")
    
    with open(f"{output_dir}/images.json", 'w') as f:
        json.dump(images, f, indent=2)
    
    # Step 4: Chunking
    print("[4/6] Chunking content...")
    
    # Try header-based first
    header_chunks = chunk_by_headers(full_text)
    
    # If that didn't work well, fall back to size-based
    if len(header_chunks) < 5:
        print("  Using size-based chunking...")
        chunks = [{"header": f"Section {i+1}", "content": c} 
                  for i, c in enumerate(chunk_by_size(full_text))]
    else:
        print("  Using header-based chunking...")
        chunks = header_chunks
    
    print(f"  Created {len(chunks)} sections")
    
    with open(f"{output_dir}/sections.json", 'w') as f:
        json.dump(chunks, f, indent=2)
    
    # Step 5: Ollama analysis
    print("[5/6] Analyzing with Ollama...")
    
    analyses = []
    chunks_to_process = chunks[:MAX_CHUNKS_TO_PROCESS] if MAX_CHUNKS_TO_PROCESS else chunks
    
    for i, chunk in enumerate(chunks_to_process):
        content = chunk.get('content', chunk) if isinstance(chunk, dict) else chunk
        if len(content) < 100:  # Skip tiny chunks
            continue
        
        analysis = analyze_section(content, i+1, len(chunks_to_process))
        analyses.append({
            "section": i+1,
            "header": chunk.get('header', f'Section {i+1}'),
            "analysis": analysis
        })
    
    with open(f"{output_dir}/analysis.json", 'w') as f:
        json.dump(analyses, f, indent=2)
    
    # Step 6: Summary
    print("[6/6] Generating summary...")
    summary_text = generate_summary(
        [a['analysis'] for a in analyses],
        pdf_name
    )
    
    summary = {
        "pdf_name": pdf_name,
        "pages": metadata.get('pages'),
        "sections_analyzed": len(analyses),
        "images_extracted": len(images),
        "summary": summary_text,
        "processed_at": datetime.now().isoformat()
    }
    
    with open(f"{output_dir}/summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Done
    print(f"\n{'='*60}")
    print("COMPLETE")
    print(f"{'='*60}")
    print(f"\nOutput files in: {output_dir}/")
    print(f"  - metadata.json    (PDF info)")
    print(f"  - full-text.txt    (All text)")
    print(f"  - sections.json    ({len(chunks)} sections)")
    print(f"  - images/          ({len(images)} images)")
    print(f"  - analysis.json    (Ollama analysis)")
    print(f"  - summary.json     (Executive summary)")
    
    print(f"\n📊 Quick summary preview:")
    print("-" * 40)
    print(summary_text[:1000])
    print("-" * 40)
    
    return output_dir

# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 pdf-processor.py <pdf_file>")
        print("")
        print("Example:")
        print("  python3 pdf-processor.py ~/Downloads/ark-big-ideas-2026.pdf")
        print("")
        print("Requirements:")
        print("  brew install poppler")
        print("  ollama pull llama2")
        sys.exit(1)
    
    process_pdf(sys.argv[1])
