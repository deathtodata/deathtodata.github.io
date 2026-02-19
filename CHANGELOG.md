# Death2Data Changelog

## Feb 19, 2026 — Repo Reorganization

### What changed
Reorganized the entire repo. Root level went from 57 files to 16. Everything else archived or sorted.

### Folder structure now

```
/                        ← Live pages only (16 files)
├── tools/               ← All privacy tools
├── admin/               ← Admin dashboard + internal tools
├── assets/              ← ALL logos, icons, images (consolidated)
├── archive/             ← Old versions, scripts, docs (nothing deleted)
│   ├── old-pages/       ← 15 HTML pages no longer linked from anywhere
│   ├── old-scripts/     ← 9 one-time Python/shell patches
│   └── old-docs/        ← 4 stale markdown docs + 3 old JSON files
├── marketing/           ← Brochures, handouts, architecture PDFs
├── docs/                ← Documentation pages (faq, guides, etc.)
├── js/                  ← Shared JavaScript modules
├── css/                 ← Shared stylesheets
├── images/              ← PWA icons (legacy path, kept for manifest)
└── k/                   ← Word of the Day system
```

### Live pages (what visitors can reach)

| Page | Purpose |
|------|---------|
| index.html | Homepage: search bar + $1 join CTA + tool links |
| story.html | Story Mode: read any page in card format |
| about.html | About Death2Data |
| revenue.html | Revenue transparency |
| tools.html | Tools hub page |
| privacy.html | Privacy policy |
| terms.html | Terms of service |
| success.html | Post-payment success page |
| 404.html | Error page |
| tools/notebook.html | 28-day cycling notebook |
| tools/leak-score.html | Email breach checker (HIBP) |
| tools/sanitizer.html | Data sanitizer |
| tools/qr-generator.html | QR code generator |
| tools/identity-vault.html | Encrypted local vault |
| tools/notary.html | Document notary (Ollama) |
| tools/account.html | Account settings |

### Archived pages (in archive/old-pages/)

| Page | What it was | Why archived |
|------|-------------|--------------|
| index-old.html | Original homepage (815 lines, discovery feed) | Replaced by current minimal homepage |
| index-v2.html | Second homepage iteration | Replaced by current version |
| welcome.html | Post-signup welcome screen | Not linked from anywhere |
| members.html | Members-only gate page | Not linked from anywhere |
| gate.html | Auth gate | Not linked from anywhere |
| auth.html | Standalone auth page | Auth now inline on homepage |
| onboard.html | Onboarding flow | Not linked from anywhere |
| restore.html | Account restore | Not linked from anywhere |
| me.html | User profile page | Not linked from anywhere |
| join.html | Signup page | Join CTA now on homepage |
| checkout.html | Checkout flow | Using Stripe hosted link instead |
| browse.html | Private browsing | Replaced by Story Mode |
| recover.html | Account recovery | Not linked from anywhere |
| test-live.html | Testing page | Dev only |
| qr-generator.html | Root-level QR generator | Duplicate of tools/qr-generator.html |

### Archived scripts (in archive/old-scripts/)

| Script | What it did |
|--------|-------------|
| check_prod.py | One-time production check |
| patch_frontend.py | One-time frontend patch |
| patch_reauth.py | One-time re-auth fix |
| patch_tools_auth.py | One-time tools auth fix |
| patch_ux.py | One-time UX patch |
| update_stats.py | Stats updater (replaced by /health endpoint) |
| add-security-js.sh | One-time security.js injection |
| fix-links.sh | One-time link fixer |
| reorganize.sh | One-time file mover |

### Archived docs (in archive/old-docs/)

| File | What it was |
|------|-------------|
| IMPLEMENTATION_SUMMARY.md | Old implementation notes |
| SECURITY_AUDIT.md | Old security audit |
| SECURITY_FIX_PLAN.md | Old security fix plan |
| CONTRIBUTING.md | Contribution guide (premature for solo project) |
| audit-report.json | Old audit data |
| d2d-insights.json | Old insights data |
| products.json | Old product catalog |

### Assets consolidated (in assets/)

All logos, icons, and images now have a single home in `assets/`. Original files kept at root paths too (favicon.svg, apple-touch-icon.png, etc.) because live pages reference them there.

| Asset | Description |
|-------|-------------|
| d2d-image.png | Shield logo (main brand mark, 500KB) |
| d2d-logo.svg | Eye-X anti-surveillance icon |
| logo.svg | Green "DEATH2DATA" wordmark on black |
| logo-white.svg | "D2D / DEATH2DATA" for light backgrounds |
| og-image.png/svg | Social sharing card |
| favicon.svg/ico | Browser tab icon |
| favicon-32.png | 32px favicon |
| apple-touch-icon.png/svg | iOS home screen icon |
| logo-192.png | 192px PWA icon |
| logo-512.png | 512px PWA icon |

---

## Feb 19, 2026 — Homepage Stripped to Essentials

### What changed
- Homepage rewritten: search bar → $1 join box → tool links. That's it.
- No personal emails displayed anywhere (placeholder: you@example.com)
- $1 Stripe CTA front and center (was buried in search results paywall)
- Copy simplified to "Search is free. Full web results are $1/mo."

### What changed in Story Mode
- Same-origin fetch for D2D's own pages (no Render server needed)
- "Start a notebook on this" button on end card
- Warm-up message after 6 seconds if server is cold

### What changed in Notebook
- "Search D2D for this" and "Read in Story Mode" links added
- Connects back to the search → story → notebook flow

---

## Feb 18, 2026 — Tools and Auth

### What changed
- Leak score, sanitizer, notebook rewritten with D2D styling
- Tools page auth gate
- CSS shared stylesheet created
- Member gate JS module

---

## Pre-Feb 18 — Original Build

- 25+ HTML pages built
- Stripe integration (hosted payment link)
- Auth system (JWT via Render backend)
- Admin dashboard
- Marketing materials (28 brochure/handout variants)
- Privacy tools suite (notebook, QR, sanitizer, vault, notary)
- Word of the Day system
