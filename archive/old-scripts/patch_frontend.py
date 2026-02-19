#!/usr/bin/env python3
"""Patch death2data frontend: clickable results, $1/mo gate, live stats"""

changes = 0

# === PATCH index.html ===
with open("index.html", "r") as f:
    idx = f.read()

# 1. Make search results clickable links
old_result = '''return`<div class="r"><div class="r-t">${r.title||''}</div><div class="r-s">${sn}</div></div>`;'''
new_result = '''const url=r.url||'#';
    const domain=url!=='#'?url.replace(/^https?:\\/\\//,'').split('/')[0]:'';
    return`<div class="r"><a class="r-t" href="${url}" target="_blank" rel="noopener">${r.title||''}</a>${domain?`<div class="r-u">${domain}</div>`:''}<div class="r-s">${sn}</div></div>`;'''

if old_result in idx:
    idx = idx.replace(old_result, new_result)
    changes += 1
    print("  [1/4] Made search results clickable")
elif 'r.url||' in idx and 'target="_blank"' in idx:
    print("  [1/4] Results already clickable")
else:
    print("  [1/4] WARNING: Could not find result template")

# 2. Style links
old_style = '''.r-t{color:#0f0;font-size:13px;margin-bottom:4px}
.r-s{color:#555;font-size:11px;line-height:1.5}'''
new_style = '''a.r-t{color:#0f0;font-size:13px;margin-bottom:2px;text-decoration:none;display:block;cursor:pointer}
a.r-t:hover{text-decoration:underline}
.r-u{color:#0a0;font-size:10px;margin-bottom:4px;opacity:0.6}
.r-s{color:#555;font-size:11px;line-height:1.5}'''

if old_style in idx:
    idx = idx.replace(old_style, new_style)
    changes += 1
    print("  [2/4] Updated result link styles")
elif 'a.r-t{' in idx:
    print("  [2/4] Link styles already updated")
else:
    print("  [2/4] WARNING: Could not find style block")

# 3. Fix gate message
old_gate = '''gateBox.querySelector('h2').textContent='ENTER LICENSE KEY';
      gateBox.querySelector('p').textContent='Check your signup email for your key.';'''
new_gate = """gateBox.querySelector('h2').textContent='ENTER LICENSE KEY';
      gateBox.querySelector('p').innerHTML='Have a key? Enter it below.<br><span style=\"color:#555;font-size:11px\">No key? <a href=\"https://buy.stripe.com/cNieVd5Vjb6N2ZY6Fq4wM00\" target=\"_blank\" style=\"color:#0f0\">Get full access for $1/mo</a></span>';"""

if old_gate in idx:
    idx = idx.replace(old_gate, new_gate)
    changes += 1
    print("  [3/4] Updated gate with $1/mo upsell")
elif '$1/mo' in idx:
    print("  [3/4] Gate message already updated")
else:
    print("  [3/4] WARNING: Could not find gate message")

with open("index.html", "w") as f:
    f.write(idx)

# === PATCH about.html ===
with open("about.html", "r") as f:
    abt = f.read()

old_fetch = """fetch('/.netlify/functions/mrr')
  .then(r => r.json())
  .then(d => {
    document.getElementById('member-count').textContent = d.customers;
    document.getElementById('mrr-display').textContent = '$' + d.mrr.toFixed(0);
  })
  .catch(() => {
    document.getElementById('member-count').textContent = '4';
    document.getElementById('mrr-display').textContent = '$4';
  });"""

new_fetch = """fetch('https://fortune0-com.onrender.com/api/public/stats')
  .then(r => r.json())
  .then(d => {
    document.getElementById('member-count').textContent = d.customers;
    document.getElementById('mrr-display').textContent = '$' + d.mrr.toFixed(0);
    const st = document.getElementById('searches-total');
    if(st) st.textContent = d.searches_total.toLocaleString();
  })
  .catch(() => {
    document.getElementById('member-count').textContent = '12';
    document.getElementById('mrr-display').textContent = '$12';
  });"""

if old_fetch in abt:
    abt = abt.replace(old_fetch, new_fetch)
    changes += 1
    print("  [4/4] Pointed about.html at live server stats")
elif 'fortune0-com.onrender.com/api/public/stats' in abt:
    print("  [4/4] About page already points to server")
else:
    print("  [4/4] WARNING: Could not find netlify fetch block")

with open("about.html", "w") as f:
    f.write(abt)

if changes > 0:
    print(f"\nDone! Applied {changes} patches.")
    print("Now run: git add index.html about.html && git commit -m 'fix: clickable results, membership upsell, live stats' && git push")
else:
    print("\nNo changes needed — everything already patched.")
