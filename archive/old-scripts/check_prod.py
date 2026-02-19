#!/usr/bin/env python3
"""
Death2Data Production Health Check
Run: python3 check_prod.py

Checks everything a paying customer touches:
  1. Can someone reach the site?
  2. Can they sign in?
  3. Can they search?
  4. Can they reach tools?
  5. Is the server awake and returning real data?
  6. Are the pages consistent (brand, links)?

No arguments needed. Uses a test email to avoid touching real accounts.
"""

import urllib.request
import urllib.error
import json
import time
import sys
import re

API = "https://fortune0-com.onrender.com"
SITE = "https://death2data.com"
TEST_EMAIL = "healthcheck@death2data.com"

results = []
warnings = []

def check(name, passed, detail="", warn=""):
    status = "PASS" if passed else "FAIL"
    results.append((name, status, detail))
    if warn:
        warnings.append(warn)
    print(f"  {'✓' if passed else '✗'} {name}" + (f" — {detail}" if detail else ""))

def fetch(url, timeout=15, method="GET", data=None, headers=None):
    """Simple fetch that returns (status_code, body_text, error_string)"""
    req = urllib.request.Request(url, method=method)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    if data:
        req.data = json.dumps(data).encode()
        req.add_header("Content-Type", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        body = resp.read().decode()
        return resp.status, body, None
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return e.code, body, str(e)
    except Exception as e:
        return 0, "", str(e)

# ─── 1. WAKE THE SERVER ───
print("\n1. Server")
print("  Waking up Render (may take 15s)...")

awake = False
for attempt in range(3):
    code, body, err = fetch(f"{API}/health", timeout=20)
    if code == 200:
        awake = True
        break
    time.sleep(5)

check("Server responds", awake,
      "fortune0-com.onrender.com is up" if awake else "Server didn't wake after 3 tries")

# ─── 2. PUBLIC STATS ───
print("\n2. Stats (real Stripe data)")
if awake:
    code, body, err = fetch(f"{API}/api/public/stats")
    if code == 200:
        try:
            stats = json.loads(body)
            members = stats.get("customers", "?")
            mrr = stats.get("mrr", "?")
            searches = stats.get("searches_today", "?")
            check("Public stats endpoint", True, f"Members: {members} | MRR: ${mrr} | Searches today: {searches}")

            # Sanity checks
            if isinstance(members, (int, float)) and members == 0:
                warnings.append("0 members reported — run sync-stripe or check webhook")
            if isinstance(mrr, (int, float)) and members and mrr < members * 0.5:
                warnings.append(f"MRR (${mrr}) seems low for {members} members — check for canceled subscriptions")
        except:
            check("Public stats endpoint", False, "Returned non-JSON")
    else:
        check("Public stats endpoint", False, f"HTTP {code}: {err}")
else:
    check("Public stats endpoint", False, "Server not awake")

# ─── 3. LOGIN FLOW ───
print("\n3. Login flow")
if awake:
    code, body, err = fetch(f"{API}/api/signup", method="POST",
                            data={"email": TEST_EMAIL, "source_domain": "death2data.com"})
    if code == 200:
        try:
            d = json.loads(body)
            token = d.get("token")
            tier = d.get("tier", "unknown")
            check("Login (signup endpoint)", True, f"Got token, tier={tier}")
        except:
            token = None
            check("Login (signup endpoint)", False, "Non-JSON response")
    else:
        token = None
        check("Login (signup endpoint)", False, f"HTTP {code}")
else:
    token = None
    check("Login (signup endpoint)", False, "Server not awake")

# ─── 4. SEARCH ───
print("\n4. Search")
if token and awake:
    code, body, err = fetch(f"{API}/api/search?q=test",
                            headers={"Authorization": f"Bearer {token}"})
    if code == 200:
        try:
            d = json.loads(body)
            authed = d.get("authed", False)
            result_count = len(d.get("results", []))
            domain_count = len(d.get("domain_results", []))
            check("Authenticated search", True,
                  f"authed={authed} | {result_count} web results | {domain_count} domain results")
        except:
            check("Authenticated search", False, "Non-JSON response")
    else:
        check("Authenticated search", False, f"HTTP {code}")

    # Anonymous search
    code2, body2, err2 = fetch(f"{API}/api/search?q=test")
    if code2 == 200:
        try:
            d2 = json.loads(body2)
            check("Anonymous search", True,
                  f"authed={d2.get('authed', '?')} | {len(d2.get('results', []))} results")
        except:
            check("Anonymous search", False, "Non-JSON response")
    else:
        check("Anonymous search", False, f"HTTP {code2}")
else:
    check("Authenticated search", False, "No token")
    check("Anonymous search", False, "Server not awake")

# ─── 5. FRONTEND PAGES ───
print("\n5. Frontend pages")
pages = {
    "Home (index.html)": f"{SITE}/",
    "About": f"{SITE}/about.html",
    "Tools": f"{SITE}/tools.html",
}

for name, url in pages.items():
    code, body, err = fetch(url, timeout=10)
    if code == 200:
        has_inter = "Inter" in body
        has_localstorage = "localStorage" in body
        has_nav = "D2D" in body
        issues = []
        if not has_inter:
            issues.append("missing Inter font")
        if "sessionStorage" in body and "localStorage" not in body:
            issues.append("still using sessionStorage!")
        if not has_nav:
            issues.append("missing D2D nav")

        if issues:
            check(name, True, f"Loaded but: {', '.join(issues)}")
            for issue in issues:
                warnings.append(f"{name}: {issue}")
        else:
            check(name, True, "Brand consistent (Inter + localStorage + D2D nav)")
    else:
        check(name, False, f"HTTP {code}")

# ─── 6. STRIPE PAYMENT LINK ───
print("\n6. Stripe")
# Check the about page for the payment link
code, body, err = fetch(f"{SITE}/about.html", timeout=10)
if code == 200:
    has_stripe = "buy.stripe.com" in body
    check("Stripe payment link on About page", has_stripe,
          "Payment link found" if has_stripe else "No buy.stripe.com link found!")
    if not has_stripe:
        warnings.append("About page has no Stripe payment link — customers can't pay")
else:
    check("Stripe payment link", False, "Couldn't load about page")

# ─── SUMMARY ───
print("\n" + "=" * 50)
passed = sum(1 for _, s, _ in results if s == "PASS")
failed = sum(1 for _, s, _ in results if s == "FAIL")
print(f"  {passed} passed, {failed} failed")

if warnings:
    print(f"\n  Warnings ({len(warnings)}):")
    for w in warnings:
        print(f"    → {w}")

if failed == 0 and not warnings:
    print("\n  Everything looks good. Product is shippable.")
elif failed == 0:
    print("\n  All checks passed but review the warnings above.")
else:
    print(f"\n  {failed} check(s) failed. Fix those before handing someone your business card.")

print()
