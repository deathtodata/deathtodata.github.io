#!/usr/bin/env python3
"""
Patch story.html to render educational card types.
Run from INSIDE the deathtodata.github.io folder:
  cd ~/wherever/deathtodata.github.io
  python3 patch_story_html.py
"""
import os, sys

# Find story.html in current directory
story_html = os.path.join(os.getcwd(), "story.html")
if not os.path.exists(story_html):
    print(f"✗ story.html not found in {os.getcwd()}")
    print("  Run this from inside your deathtodata.github.io folder")
    sys.exit(1)

with open(story_html, "r") as f:
    html = f.read()

# Check if already patched
if "card.type === 'what_to_know'" in html:
    print("✓ Already patched!")
    sys.exit(0)

OLD_IMAGE_BLOCK = """    } else if (card.type === 'image') {
      result.push({
        type: 'image',
        html: `<div class="card-inner card-image">
          <img src="${esc(card.src)}" alt="${esc(card.alt)}" loading="lazy" onerror="this.closest('.story-card').style.display='none'">
          ${card.alt ? `<div class="img-caption">${esc(truncate(card.alt, 120))}</div>` : ''}
        </div>`
      });
    }"""

NEW_WITH_EDUCATIONAL = """    } else if (card.type === 'what_to_know') {
      result.push({
        type: 'what_to_know',
        html: `<div class="card-inner" style="display:flex;flex-direction:column;justify-content:center;gap:20px;max-width:520px;margin:0 auto;">
          <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--green);">What You Should Know</div>
          <div style="font-size:16px;line-height:1.8;color:var(--gray);">${esc(card.text)}</div>
          <div style="font-size:11px;color:var(--muted);border-top:1px solid var(--border);padding-top:12px;">D2D Privacy Education</div>
        </div>`
      });
    } else if (card.type === 'alternatives') {
      result.push({
        type: 'alternatives',
        html: `<div class="card-inner" style="display:flex;flex-direction:column;justify-content:center;gap:20px;max-width:520px;margin:0 auto;">
          <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);">Privacy-Friendly Alternatives</div>
          <div style="font-size:15px;line-height:1.8;color:var(--gray);">${esc(card.text)}</div>
        </div>`
      });
    } else if (card.type === 'questions') {
      const qHtml = (card.items || []).map((q, i) =>
        `<div style="display:flex;gap:12px;align-items:flex-start;padding:14px 0;${i > 0 ? 'border-top:1px solid var(--border);' : ''}">
          <span style="font-family:var(--mono);font-size:20px;color:var(--green);line-height:1;">?</span>
          <span style="font-size:14px;line-height:1.6;color:var(--gray);">${esc(q)}</span>
        </div>`
      ).join('');
      result.push({
        type: 'questions',
        html: `<div class="card-inner" style="display:flex;flex-direction:column;justify-content:center;gap:12px;max-width:520px;margin:0 auto;">
          <div style="font-size:10px;letter-spacing:2px;text-transform:uppercase;color:var(--muted);">Ask Yourself</div>
          ${qHtml}
          <div style="font-size:11px;color:var(--muted);border-top:1px solid var(--border);padding-top:12px;">Journal these in your <a href="/tools/notebook.html?topic=${encodeURIComponent(title)}" style="color:var(--green);text-decoration:underline;">D2D Notebook</a></div>
        </div>`
      });
    } else if (card.type === 'image') {
      result.push({
        type: 'image',
        html: `<div class="card-inner card-image">
          <img src="${esc(card.src)}" alt="${esc(card.alt)}" loading="lazy" onerror="this.closest('.story-card').style.display='none'">
          ${card.alt ? `<div class="img-caption">${esc(truncate(card.alt, 120))}</div>` : ''}
        </div>`
      });
    }"""

if OLD_IMAGE_BLOCK in html:
    html = html.replace(OLD_IMAGE_BLOCK, NEW_WITH_EDUCATIONAL)
    with open(story_html, "w") as f:
        f.write(html)
    print("✓ Patched story.html — added educational card renderers")
else:
    print("⚠ Couldn't find the exact image block to replace.")
    print("  The file may have been modified. Check story.html manually.")
    sys.exit(1)
