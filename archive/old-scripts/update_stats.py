#!/usr/bin/env python3
"""
Update stats.json with real numbers from Stripe.

Usage:
  python3 update_stats.py              # uses STRIPE_SECRET_KEY from env
  python3 update_stats.py sk_live_xxx  # pass key directly

Updates stats.json, then you push:
  git add stats.json && git commit -m 'update stats' && git push
"""

import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone

key = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("STRIPE_SECRET_KEY", "")
if not key:
    print("Need STRIPE_SECRET_KEY. Pass as argument or set in env.")
    print("  python3 update_stats.py sk_live_YOUR_KEY_HERE")
    sys.exit(1)

def stripe_get(endpoint, params=None):
    url = f"https://api.stripe.com/v1/{endpoint}"
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {key}")
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"Stripe API error: {e.code} {e.read().decode()[:200]}")
        return None

# Count active subscriptions
print("Fetching active subscriptions...")
subs_data = stripe_get("subscriptions", {"status": "active", "limit": 100})
if not subs_data:
    print("Failed to fetch subscriptions")
    sys.exit(1)

active_subs = subs_data.get("data", [])
active_count = len(active_subs)

# Calculate MRR from actual subscription amounts
mrr = 0
emails = []
for sub in active_subs:
    for item in sub.get("items", {}).get("data", []):
        amount = item.get("price", {}).get("unit_amount", 0) / 100
        mrr += amount
    # Get customer email
    cust_id = sub.get("customer", "")
    if cust_id:
        cust = stripe_get(f"customers/{cust_id}")
        if cust and cust.get("email"):
            emails.append(cust["email"])

# Count canceled (for context)
print("Fetching canceled subscriptions...")
canceled_data = stripe_get("subscriptions", {"status": "canceled", "limit": 100})
canceled_count = len(canceled_data.get("data", [])) if canceled_data else 0

# Build stats
stats = {
    "mrr": round(mrr, 2),
    "customers": active_count,
    "canceled": canceled_count,
    "searches_total": 0,
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "source": "stripe"
}

# Write
with open("stats.json", "w") as f:
    json.dump(stats, f)

print(f"\nStats updated:")
print(f"  Active subscribers: {active_count}")
print(f"  MRR: ${mrr:.2f}")
print(f"  Canceled: {canceled_count}")
print(f"  Emails: {', '.join(emails[:5])}{'...' if len(emails) > 5 else ''}")
print(f"\nNext: git add stats.json && git commit -m 'update stats' && git push")
