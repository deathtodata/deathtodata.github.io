#!/usr/bin/env python3
"""Patch death2data frontend: auto-reauth when server token dies.

When Render cold-starts or deploys, in-memory tokens become invalid.
Even with DB-persisted sessions, there's a window where tokens can die.

This patch adds:
  1. doSearch() detects dead tokens (authed===false) and auto-re-logins
  2. Page load proactively verifies the token and refreshes if dead

Result: Customers stay logged in seamlessly, never see fake placeholder results.
"""

with open("index.html", "r") as f:
    code = f.read()

changes = 0

# 1. Patch doSearch to detect dead tokens and auto-reauth
old_search = '''async function doSearch(){
  const q=document.getElementById('q').value.trim();
  if(!q)return;
  S.searches++;updateCounter();
  document.getElementById('mid').classList.remove('center');
  document.getElementById('results').innerHTML='<div class="hint">searching...</div>';
  let results;
  try{
    const h={};if(S.token)h['Authorization']='Bearer '+S.token;
    const r=await fetch(API+'/api/search?q='+encodeURIComponent(q),{headers:h});
    const d=await r.json();
    if(d.results&&d.results.length>0){
      results=d.results;
      // If web results are locked, hint at upgrade
      if(d.web_locked){
        results.push({title:'Web results available',snippet:'Sign in with your license key for full web search results.',engine:'info'});
      }
    }
    else results=localResults(q);
  }catch(e){results=localResults(q);}
  renderResults(results,q);
}'''

new_search = '''async function doSearch(){
  const q=document.getElementById('q').value.trim();
  if(!q)return;
  S.searches++;updateCounter();
  document.getElementById('mid').classList.remove('center');
  document.getElementById('results').innerHTML='<div class="hint">searching...</div>';
  let results;
  try{
    const h={};if(S.token)h['Authorization']='Bearer '+S.token;
    const r=await fetch(API+'/api/search?q='+encodeURIComponent(q),{headers:h});
    const d=await r.json();
    // If we thought we were logged in but server says no, token is dead — auto-reauth
    if(S.token && d.authed===false && S.email && !S._reauthing){
      S._reauthing=true;
      try{
        const ar=await fetch(API+'/api/signup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:S.email,source_domain:'death2data.com'})});
        const ad=await ar.json();
        if(ad.token){
          S.token=ad.token;S.tier=ad.tier;
          sessionStorage.setItem('d2d_token',ad.token);
          showAuthed();updateCounter();
          S._reauthing=false;
          return doSearch(); // retry with new token
        }
      }catch(re){}
      S._reauthing=false;
    }
    if(d.results&&d.results.length>0){
      results=d.results;
      // If web results are locked, hint at upgrade
      if(d.web_locked){
        results.push({title:'Web results available',snippet:'Sign in with your license key for full web search results.',engine:'info'});
      }
    }
    else results=localResults(q);
  }catch(e){results=localResults(q);}
  renderResults(results,q);
}'''

if old_search in code:
    code = code.replace(old_search, new_search)
    changes += 1
    print("  [1/2] Added dead-token detection + auto-reauth to doSearch()")
elif 'S._reauthing' in code:
    print("  [1/2] doSearch() already has auto-reauth")
else:
    print("  [1/2] WARNING: Could not find doSearch() to patch")

# 2. Patch init() to proactively verify token on page load
old_init = '''(function init(){
  const t=sessionStorage.getItem('d2d_token'), e=sessionStorage.getItem('d2d_email');
  if(t&&e){ S.token=t; S.email=e; S.maxFree=Infinity; }
  const hasQ = new URLSearchParams(location.search).get('q');
  if(sessionStorage.getItem('d2d_entered') || S.token || hasQ){
    activate();
    if(hasQ){ document.getElementById('q').value=hasQ; doSearch(); }
  }
})();'''

new_init = '''(function init(){
  const t=sessionStorage.getItem('d2d_token'), e=sessionStorage.getItem('d2d_email');
  if(t&&e){ S.token=t; S.email=e; S.maxFree=Infinity; }
  const hasQ = new URLSearchParams(location.search).get('q');
  if(sessionStorage.getItem('d2d_entered') || S.token || hasQ){
    activate();
    if(hasQ){ document.getElementById('q').value=hasQ; doSearch(); }
  }
  // Proactively verify session on load — re-auth if token is dead
  if(S.token && S.email){
    fetch(API+'/api/search?q=ping',{headers:{'Authorization':'Bearer '+S.token}})
      .then(r=>r.json()).then(d=>{
        if(d.authed===false){
          // Token is dead — try to get a new one
          fetch(API+'/api/signup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:S.email,source_domain:'death2data.com'})})
            .then(r=>r.json()).then(ad=>{
              if(ad.token){ S.token=ad.token;S.tier=ad.tier;sessionStorage.setItem('d2d_token',ad.token);showAuthed();updateCounter(); }
            }).catch(()=>{});
        }
      }).catch(()=>{});
  }
})();'''

if old_init in code:
    code = code.replace(old_init, new_init)
    changes += 1
    print("  [2/2] Added proactive token verification on page load")
elif 'Proactively verify session' in code:
    print("  [2/2] Token verification already added")
else:
    print("  [2/2] WARNING: Could not find init() to patch")

if changes > 0:
    with open("index.html", "w") as f:
        f.write(code)
    print(f"\nDone! Applied {changes} patches to index.html")
    print("\nWhat this fixes:")
    print("  - If a customer's token dies (cold start, deploy), search auto-re-authenticates")
    print("  - On page load, if token is saved but dead, refreshes it in the background")
    print("  - Customers never see fake 'overview/about/more results' placeholders")
    print("\nNow run:")
    print("  cd deathtodata.github.io")
    print("  git add index.html && git commit -m 'fix: auto-reauth when server token expires' && git push")
else:
    print("\nNo changes needed — everything already patched.")
