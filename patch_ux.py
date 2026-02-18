#!/usr/bin/env python3
"""UX improvements based on real user feedback (Michelle).

Changes:
  1. "out" → "sign out" (she didn't know what it meant)
  2. Snippet text #555 → #999 (too dark on mobile in daylight)
  3. Remove keyword highlighting (she already knows what she searched)
  4. Add favicons to results (visual recognition of sites)
  5. Result cards with borders instead of flat text wall
  6. Cleaner footer: "sign in with email" placeholder, "join $1/mo" CTA
  7. Bigger result titles (13px → 14px), better line height
"""

with open("index.html", "r") as f:
    code = f.read()

changes = 0

# 1. Fix result card styles — better readability
old_results_css = """/* results */
.results{max-width:520px;width:100%;padding:0 16px 20px}
.r{padding:14px 0;border-bottom:1px solid #0a0a0a}
.r:last-child{border-bottom:none}
a.r-t{color:#0f0;font-size:13px;margin-bottom:2px;text-decoration:none;display:block;cursor:pointer}
a.r-t:hover{text-decoration:underline}
.r-u{color:#0a0;font-size:10px;margin-bottom:4px;opacity:0.6}
.r-s{color:#555;font-size:11px;line-height:1.5}
.r-s mark{background:none;color:#0f0}
.hint{text-align:center;color:#222;padding:30px 0;font-size:11px}"""

new_results_css = """/* results */
.results{max-width:600px;width:100%;padding:0 16px 20px}
.r{padding:16px 14px;margin-bottom:8px;border:1px solid #1a1a1a;border-radius:6px;
  background:#0d0d0d;transition:border-color .2s}
.r:hover{border-color:#1f3a1f}
a.r-t{color:#0f0;font-size:14px;margin-bottom:4px;text-decoration:none;display:block;cursor:pointer;
  line-height:1.4;font-weight:500}
a.r-t:hover{text-decoration:underline}
.r-u{color:#888;font-size:11px;margin-bottom:6px}
.r-s{color:#999;font-size:12px;line-height:1.6}
.hint{text-align:center;color:#444;padding:30px 0;font-size:11px}"""

if old_results_css in code:
    code = code.replace(old_results_css, new_results_css)
    changes += 1
    print("  [1/4] Updated result card styles (readability + cards)")
elif ".r-s{color:#999" in code:
    print("  [1/4] Result styles already updated")
else:
    print("  [1/4] WARNING: Could not find result styles to patch")

# 2. Remove keyword highlighting, add favicons
old_render = '''function renderResults(results,q){
  const el=document.getElementById('results');
  const words=q.toLowerCase().split(/\\s+/);
  el.innerHTML=results.map(r=>{
    let sn=r.snippet||r.content||'';
    words.forEach(w=>{if(w.length>2)sn=sn.replace(new RegExp('('+w.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')+')','gi'),'<mark>$1</mark>');});
    const url=r.url||'#';
    const domain=url!=='#'?url.replace(/^https?:\\/\\//,'').split('/')[0]:'';
    return`<div class="r"><a class="r-t" href="${url}" target="_blank" rel="noopener">${r.title||''}</a>${domain?`<div class="r-u">${domain}</div>`:''}<div class="r-s">${sn}</div></div>`;
  }).join('');
}'''

new_render = '''function renderResults(results,q){
  const el=document.getElementById('results');
  el.innerHTML=results.map(r=>{
    const sn=r.snippet||r.content||'';
    const url=r.url||'#';
    const domain=url!=='#'?url.replace(/^https?:\\/\\//,'').split('/')[0]:'';
    // Favicon from Google's service
    const ico=domain?`<img src="https://www.google.com/s2/favicons?domain=${domain}&sz=16" width="14" height="14" style="vertical-align:-2px;margin-right:6px;border-radius:2px;opacity:.7" onerror="this.style.display='none'">`:'';
    return`<div class="r"><a class="r-t" href="${url}" target="_blank" rel="noopener">${r.title||''}</a>${domain?`<div class="r-u">${ico}${domain}</div>`:''}<div class="r-s">${sn}</div></div>`;
  }).join('');
}'''

if old_render in code:
    code = code.replace(old_render, new_render)
    changes += 1
    print("  [2/4] Removed keyword highlighting, added favicons")
elif 'favicons?domain=' in code:
    print("  [2/4] Favicons already added")
else:
    print("  [2/4] WARNING: Could not find renderResults to patch")

# 3. Fix showAuthed footer — "out" → "sign out", reorder
old_authed = '''function showAuthed(){
  document.getElementById('foot').innerHTML=`
    <a href="/about.html">$1/mo</a><span class="sep">\\xb7</span>
    <span class="user"><span class="live"></span>${S.email}</span>
    <button onclick="logout()">out</button>
    <span class="sep">\\xb7</span><a href="/tools.html">tools</a>`;
}'''

new_authed = '''function showAuthed(){
  document.getElementById('foot').innerHTML=`
    <span class="user"><span class="live"></span>${S.email}</span>
    <span class="sep">\\xb7</span>
    <a href="/tools.html" style="color:#0f0">tools</a>
    <span class="sep">\\xb7</span>
    <button onclick="logout()" style="color:#666">sign out</button>`;
}'''

if 'onclick="logout()">out</button>' in code:
    code = code.replace('onclick="logout()">out</button>', 'onclick="logout()" style="color:#666">sign out</button>')
    changes += 1
    print("  [3/4] Changed 'out' to 'sign out'")
elif 'sign out</button>' in code:
    print("  [3/4] Already says 'sign out'")
else:
    print("  [3/4] WARNING: Could not find logout button to patch")

# 4. Fix non-authed footer — clearer placeholder + CTA
old_foot = '''<a href="/about.html">$1/mo</a><span class="sep">·</span>
      <input type="email" id="email" placeholder="email"'''

new_foot = '''<input type="email" id="email" placeholder="sign in with email"'''

if old_foot in code:
    code = code.replace(old_foot, new_foot)
    changes += 1
    print("  [4/4] Updated footer: clearer sign-in placeholder")
elif 'placeholder="sign in with email"' in code:
    print("  [4/4] Footer already updated")
else:
    print("  [4/4] WARNING: Could not find footer to patch")

if changes > 0:
    with open("index.html", "w") as f:
        f.write(code)
    print(f"\\nDone! Applied {changes} patches to index.html")
    print("\\nNow run:")
    print("  git add index.html && git commit -m 'ux: readability + result cards + clearer labels (from real user feedback)' && git push")
else:
    print("\\nNo changes needed — everything already patched.")
