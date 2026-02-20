# Death2Data Naming & Structure Conventions

## The Rule

**One rule: kebab-case (dashes) for everything visible. Snake_case (underscores) for everything stored.**

| What | Convention | Example |
|------|-----------|---------|
| HTML files | kebab-case | `leak-score.html`, `qr-generator.html` |
| CSS classes | kebab-case | `join-btn`, `card-title`, `hd-logo` |
| CSS IDs | kebab-case | `join-box`, `auth-area` |
| JS files | kebab-case | `member-gate.js`, `ollama-tools.js` |
| Folders | lowercase, no separators | `tools/`, `admin/`, `assets/`, `archive/` |
| localStorage keys | snake_case with `d2d_` prefix | `d2d_token`, `d2d_email`, `d2d_tier` |
| API endpoints | kebab-case with `/api/` prefix | `/api/search`, `/api/login`, `/api/domain-info` |
| URL slugs | kebab-case | `/tools/leak-score.html` |
| Python files | snake_case | `update_stats.py` (Python convention) |
| Environment vars | SCREAMING_SNAKE | `STRIPE_SECRET_KEY`, `D2D_API_URL` |

## Product Names

| Name | When to use |
|------|-------------|
| Death2Data | Full name, marketing, about page, legal |
| D2D | Short name, code prefixes, logo, favicon |
| death2data.com | The domain, URLs |
| d2d | Prefix for localStorage, CSS, internal references |

Do NOT use: death-2-data, death_2_data, d-2-d, Death2data, DEATH2DATA (except in logo SVG)

## Repo Names

| Repo | What | Why named this way |
|------|------|-------------------|
| deathtodata.github.io | Frontend (GitHub Pages) | GitHub requires `{org}.github.io` format |
| fortune0-site | Backend (Render) | Legacy name from fortune0 product. Serves D2D API too. |

These can't easily change (deploy URLs depend on them). Live with it.

## Brand Tokens (Single Source of Truth)

**Every page must import:**
```html
<link rel="stylesheet" href="/css/brand.css">
```

This file defines ALL colors, fonts, layout vars, reset, and base body styles. Never hardcode `#00cc44`, `#0a0a0a`, or font stacks inline — use the CSS variables.

| Token | Value | Use |
|-------|-------|-----|
| `--green` | `#00cc44` | Primary brand color, links, CTAs |
| `--green-hover` | `#00e64d` | Hover states |
| `--green-dim` | `#004d1a` | Subtle backgrounds |
| `--green-alpha` | `rgba(0,204,68,0.1)` | Transparent overlays |
| `--bg` | `#0a0a0a` | Page background |
| `--surface` | `#111111` | Card/section background |
| `--border` | `#1e1e1e` | Borders |
| `--white` | `#e0e0e0` | Primary text |
| `--gray` | `#b0b0b0` | Secondary text |
| `--muted` | `#666666` | Tertiary text, labels |
| `--dim` | `#444444` | Disabled/faint text |
| `--font` | Inter stack | Body text |
| `--mono` | JetBrains Mono | Logo, code, monospace |
| `--serif` | Georgia stack | Story Mode reading |

**Do NOT use:** `#0f0`, `#00ff00`, `system-ui` alone, `SF Mono`, `Courier New`, `monospace` alone.

## Backend URLs

**Use only ONE backend URL:**
```
https://fortune0-com.onrender.com
```

The old Cloudflare worker (`d2d-api.mattmauersp.workers.dev`) is deprecated. Any file still referencing it needs updating.

## localStorage Keys (Complete List)

### Auth
- `d2d_token` — JWT auth token
- `d2d_email` — user's email
- `d2d_tier` — subscription tier (free/active)
- `d2d_paid` — payment status
- `d2d_created` — account creation date
- `d2d_customer_id` — Stripe customer ID

### Usage
- `d2d_searches` — search count (for paywall)
- `d2d_browse_usage` — browse count
- `d2d_browse_date` — last browse date

### Tools
- `d2d_notebook` — notebook data
- `d2d_notes` — notes data
- `d2d_pending_topic` — topic passed between pages
- `d2d_keyword` — last keyword

### Crypto/Identity
- `d2d_public_key` — public key (identity vault)
- `d2d_private_key` — private key (identity vault)
- `d2d_trust_circle` — trust circle data
- `d2d_anon_name` — anonymous display name

### Admin/Internal
- `d2d_access` — access level
- `d2d_access_token` — admin access token
- `d2d_grant_materials` — grant materials state
- `d2d_perspectives` — perspectives data
- `d2d_payment_timestamp` — last payment time
- `d2d_referrer` — who referred them
- `d2d_referrer_time` — when referred

### Fortune0 (legacy, from fortune0 integration)
- `f0_token` — fortune0 auth token
- `f0_referral_code` — fortune0 referral code

## File That Breaks Convention (Fix Later)

| File | Problem | Should Be |
|------|---------|-----------|
| config.js (references workers.dev) | Wrong backend URL | Update to onrender.com |
| css/fortune0.css | Named after wrong product | Rename to `d2d-base.css` or merge into style.css |
| d2d.js (root level) | Should be in js/ folder | Move to js/d2d.js |
| api/privacy_mcp.py | Underscore in folder that uses dashes | Fine (Python convention) |

## Folder Structure

```
/                        ← Live pages (kebab-case.html)
├── tools/               ← Privacy tools
├── admin/               ← Admin pages
├── assets/              ← All logos, icons, images
├── archive/             ← Old versions (organized by type)
│   ├── old-pages/
│   ├── old-scripts/
│   └── old-docs/
├── marketing/           ← Print/PDF materials
├── docs/                ← Documentation pages
├── js/                  ← Shared JavaScript (kebab-case.js)
├── css/                 ← Shared CSS
├── images/              ← PWA icons (legacy path)
└── k/                   ← Word of the Day
```
