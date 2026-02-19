#!/usr/bin/env python3
"""Fix tools.html and member-gate.js: they check localStorage, but login saves to sessionStorage.

Root cause: index.html saves auth to sessionStorage (d2d_token, d2d_email).
But member-gate.js checks localStorage.d2d_member — never set by login.
And tools.html checks localStorage.d2d_paid — also never set.

Result: Every paid member who clicks "tools" gets redirected to /?reason=not_member.

Fix: Both now check sessionStorage first (primary), localStorage second (legacy).
"""

import os

changes = 0

# 1. Fix member-gate.js
gate_path = "js/member-gate.js"
if os.path.exists(gate_path):
    with open(gate_path) as f:
        code = f.read()

    if "sessionStorage.getItem('d2d_token')" in code:
        print("  [1/2] member-gate.js already fixed")
    elif "localStorage.getItem('d2d_member')" in code:
        new_code = """// member-gate.js
// Add this to any page you want to protect:
// <script src="/js/member-gate.js"></script>

(function() {
  // Check all possible auth sources (index.html uses sessionStorage, legacy uses localStorage)
  const token = sessionStorage.getItem('d2d_token');
  const email = sessionStorage.getItem('d2d_email');
  const legacyMember = JSON.parse(localStorage.getItem('d2d_member') || 'null');

  // Logged in via search page (primary auth)
  if (token && email) {
    document.body.style.visibility = 'visible';
    const el = document.getElementById('member-status');
    if (el) el.innerHTML = `${email} · <a href="/">Back to Search</a>`;
    return;
  }

  // Legacy auth (localStorage)
  if (legacyMember && legacyMember.expires && legacyMember.expires > Date.now()) {
    document.body.style.visibility = 'visible';
    const el = document.getElementById('member-status');
    if (el) {
      const days = Math.ceil((legacyMember.expires - Date.now()) / (24*60*60*1000));
      el.innerHTML = `${legacyMember.email} · ${days} days left · <a href="/manage.html">Manage</a>`;
    }
    return;
  }

  // Not logged in — redirect to home
  window.location.href = '/?reason=not_member';
})();
"""
        with open(gate_path, "w") as f:
            f.write(new_code)
        changes += 1
        print("  [1/2] Fixed member-gate.js — now checks sessionStorage first")
    else:
        print("  [1/2] WARNING: member-gate.js has unexpected content")
else:
    print("  [1/2] WARNING: js/member-gate.js not found")

# 2. Fix tools.html validateToken
tools_path = "tools.html"
if os.path.exists(tools_path):
    with open(tools_path) as f:
        code = f.read()

    if "sessionStorage.getItem('d2d_token')" in code:
        print("  [2/2] tools.html already fixed")
    elif "localStorage.getItem('d2d_paid')" in code:
        old_validate = """async function validateToken() {
  // Check if user is logged in
  const paid = localStorage.getItem('d2d_paid');
  const email = localStorage.getItem('d2d_email');

  if (!paid || !email) {
    showAccessDenied('Please log in first');
    return;
  }

  if (paid) {
    showTools(email);
  } else {
    showAccessDenied('Invalid token');
  }
}"""
        new_validate = """async function validateToken() {
  const token = sessionStorage.getItem('d2d_token');
  const email = sessionStorage.getItem('d2d_email') || localStorage.getItem('d2d_email');
  const legacyPaid = localStorage.getItem('d2d_paid');

  if (token && email) {
    showTools(email);
    return;
  }

  if (legacyPaid && email) {
    showTools(email);
    return;
  }

  showAccessDenied('Sign in on the search page first');
}"""
        if old_validate in code:
            code = code.replace(old_validate, new_validate)
            with open(tools_path, "w") as f:
                f.write(code)
            changes += 1
            print("  [2/2] Fixed tools.html — now checks sessionStorage first")
        else:
            print("  [2/2] WARNING: Could not find validateToken in tools.html")
    else:
        print("  [2/2] WARNING: tools.html has unexpected content")
else:
    print("  [2/2] WARNING: tools.html not found")

if changes > 0:
    print(f"\nDone! Fixed {changes} file(s)")
    print("\nRun:")
    print("  git add js/member-gate.js tools.html && git commit -m 'fix: tools page redirect — auth was checking wrong storage' && git push")
else:
    print("\nNo changes needed — everything already patched.")
