# Death2Data

> Privacy search engine. $1/mo gets your email across 230 domains.

**Live:** [death2data.com](https://death2data.com)

## What It Is

Search the web without being tracked. $1/month unlocks full web results and gives you an email identity across 230+ domains (death2data.com, and growing). Free tier gets basic search + all privacy tools.

## How It Works

```
Search (free) → Story Mode (read any page) → Notebook (save notes)
                                                    ↓
                                            $1/mo for full results
```

- **Search** — privacy-first web search. Free tier shows limited results, $1/mo unlocks everything.
- **Story Mode** — read any webpage in a clean, card-based format. No ads, no tracking.
- **Notebook** — 28-day cycling notebook. Take notes, pin domains, auto-deletes for privacy.
- **Tools** — leak score checker, data sanitizer, QR generator, identity vault. All free, all client-side.

## Stack

| Layer | Tech | Where |
|-------|------|-------|
| Frontend | Static HTML/CSS/JS | GitHub Pages ([deathtodata.github.io](https://github.com/deathtodata/deathtodata.github.io)) |
| Backend | Node.js / Express | Render free tier ([fortune0-site](https://github.com/deathtodata/fortune0-site)) |
| Payments | Stripe ($1/mo) | [Hosted link](https://buy.stripe.com/cNieVd5Vjb6N2ZY6Fq4wM00) |
| Auth | JWT tokens | Backend issues, frontend stores in localStorage |
| Domain | death2data.com | GitHub Pages CNAME |

## Project Structure

```
/                          ← GitHub Pages root
├── index.html             ← Homepage: search + $1 CTA + tool links
├── story.html             ← Story Mode reader
├── about.html             ← About page
├── revenue.html           ← Revenue/transparency
├── tools.html             ← Tools hub
├── tools/
│   ├── notebook.html      ← 28-day notebook
│   ├── leak-score.html    ← HIBP email breach checker
│   ├── sanitizer.html     ← Data sanitizer
│   ├── qr-generator.html  ← QR code generator
│   ├── identity-vault.html← Encrypted local vault
│   ├── notary.html        ← Document notary (Ollama)
│   └── account.html       ← Account settings
├── admin/                 ← Admin dashboard (auth required)
├── marketing/             ← Brochures, handouts, architecture docs
├── docs/                  ← Documentation pages
├── js/                    ← Shared JS (auth, security, env, ollama)
├── css/                   ← Shared CSS
├── images/                ← PWA icons (192, 512)
├── d2d-image.png          ← Shield logo (main brand mark)
├── d2d-logo.svg           ← Eye-X anti-surveillance icon
├── logo.svg               ← Green "DEATH2DATA" wordmark
├── logo-white.svg         ← Light background version
├── favicon.svg            ← Browser tab icon
└── config.js              ← Environment auto-detection
```

## Assets & Branding

| File | What | Use |
|------|------|-----|
| `d2d-image.png` | 3D shield icon | Main brand mark, social, print |
| `d2d-logo.svg` | Eye with X | Anti-surveillance icon |
| `logo.svg` | Green "DEATH2DATA" on black | Header, dark backgrounds |
| `logo-white.svg` | "D2D / DEATH2DATA" | Light backgrounds, print |
| `og-image.png` | Social sharing card | og:image meta tag |
| `favicon.svg` | Green "D2D" on black | Browser tab |
| `apple-touch-icon.png` | App icon | iOS home screen |
| `images/logo-192.png` | 192px icon | PWA manifest |
| `images/logo-512.png` | 512px icon | PWA manifest |

**Colors:**
- Background: `#0a0a0a`
- Green: `#00cc44`
- Surface: `#111`
- Border: `#1e1e1e`
- Text: `#e0e0e0`
- Font: Inter (body), JetBrains Mono (brand)

## What Works Without the Server

These work on GitHub Pages alone (no Render backend needed):

- Notebook (localStorage)
- QR Generator (client-side)
- Data Sanitizer (client-side)
- Leak Score (public HIBP API)
- Identity Vault (client-side encrypted)
- Story Mode for D2D's own pages (same-origin fetch)
- About, Privacy, Terms, Revenue pages

## What Needs the Backend

These hit the Render free tier server (30-50s cold start):

- Search (`/api/search`)
- Story Mode for external URLs (`/fetch`)
- Auth (`/api/signup`, `/api/login`)
- Stripe webhook (`/api/stripe-webhook`)

## Running Locally

```bash
git clone https://github.com/deathtodata/deathtodata.github.io.git
cd deathtodata.github.io
python3 -m http.server 3000
# → http://localhost:3000
```

For backend features, also run [fortune0-site](https://github.com/deathtodata/fortune0-site) locally.

## Stripe

- Payment link: `https://buy.stripe.com/cNieVd5Vjb6N2ZY6Fq4wM00`
- Price: $1/month
- Webhook upgrades user tier from `free` to `active`
- Email pre-filled from auth when possible

## Known Issues

- Render free tier cold starts (30-50s) — search shows warm-up message after 6s
- 9 orphan HTML files need cleanup (see cleanup section below)
- 10+ pages still have inconsistent colors/headers
- Git lock files may need manual cleanup

## Cleanup Needed

**Orphan pages** (not linked from anywhere):
`welcome.html`, `members.html`, `gate.html`, `auth.html`, `onboard.html`, `restore.html`, `index-old.html`, `index-v2.html`, `test-live.html`

**Root-level scripts** (one-time patches, should be deleted or moved):
`check_prod.py`, `patch_frontend.py`, `patch_reauth.py`, `patch_tools_auth.py`, `patch_ux.py`, `update_stats.py`, `add-security-js.sh`, `fix-links.sh`, `reorganize.sh`

**Stale docs:**
`IMPLEMENTATION_SUMMARY.md`, `SECURITY_AUDIT.md`, `SECURITY_FIX_PLAN.md`, `CONTRIBUTING.md`

## License

Apache 2.0 — see [LICENSE](LICENSE)

---

Built by Matt. One person. 230 domains. $1/mo.
