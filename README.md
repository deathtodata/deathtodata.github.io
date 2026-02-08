# Death2Data - Privacy-First Search & Tools

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Live Site](https://img.shields.io/badge/live-death2data.com-brightgreen)](https://death2data.com)

> Privacy-focused search engine and digital toolkit. No tracking. No ads. No data collection.

## What is Death2Data?

Death2Data is a privacy-first platform offering:

- **Private Search** - Browse the web without being tracked
- **QR Code Generator** - Create QR codes for any URL
- **PDF Processor** - Process PDFs without uploading to third-party servers
- **Digital Notebook** - 28-day cycling notebook (automatic data deletion)
- **Identity Vault** - Secure storage for personal information
- **Word of the Day** - Daily privacy & security terms

## Membership

**$1 every 28 days** for full access to all tools.

- No contracts or commitments
- Cancel anytime
- All tools included
- No hidden fees

## Tech Stack

- **Frontend:** Static HTML/CSS/JavaScript hosted on GitHub Pages
- **Backend:** Cloudflare Workers API (`d2d-api.mattmauersp.workers.dev`)
- **Payments:** Stripe ($1 every 28 days)
- **Hosting:** GitHub Pages (frontend) + Cloudflare Workers (backend)
- **CI/CD:** GitHub Actions for automated testing and deployment

## Project Structure

```
/
├── public/              # Public-facing site pages
│   ├── index.html      # Homepage
│   ├── browse.html     # Private browsing
│   ├── join.html       # Signup page
│   └── pricing.html    # Pricing info
│
├── admin/              # Admin dashboards (requires auth)
│   ├── dashboard.html  # Main admin dashboard
│   ├── admin.html      # Admin controls
│   └── manage.html     # User management
│
├── tools/              # Member tools
│   ├── qr-generator.html
│   ├── identity-vault.html
│   └── account.html
│
├── docs/               # Documentation
│   ├── faq.html
│   └── guides/
│
├── k/                  # Word of the Day system
│   └── index.html
│
├── css/                # Stylesheets
├── js/                 # JavaScript modules
│   ├── auth.js        # Authentication
│   ├── security.js    # Security utilities (XSS protection, etc.)
│   └── env.js         # Environment configuration
│
└── .github/            # CI/CD workflows
```

## Getting Started

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/deathtodata/deathtodata.github.io.git
   cd deathtodata.github.io
   ```

2. Set up environment variables (copy `.env.example` to `.env`):
   ```bash
   cp .env.example .env
   ```

3. Edit `.env` with your local configuration:
   ```env
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   D2D_API_URL=http://localhost:8787
   NODE_ENV=development
   ```

4. Serve the site locally:
   ```bash
   python3 -m http.server 3000
   # or
   npx serve .
   ```

5. Visit `http://localhost:3000`

### Environment Variables

The site uses environment variables for sensitive configuration:

- `STRIPE_PUBLISHABLE_KEY` - Stripe publishable key (pk_live_... or pk_test_...)
- `STRIPE_PRICE_ID` - Stripe price ID for the $1/28-day subscription
- `D2D_API_URL` - Backend API URL (defaults to production Cloudflare Worker)
- `NODE_ENV` - Environment (development/staging/production)

See `.env.example` for the complete list and `js/env.js` for how they're loaded.

## Security

Death2Data takes security seriously:

- ✅ All secrets stored as environment variables (never committed to git)
- ✅ XSS protection via `js/security.js` sanitization
- ✅ HTTPS enforced on all production pages
- ✅ Client-side rate limiting (server-side enforcement required)
- ✅ URL validation to prevent SSRF attacks
- 🚧 **TODO:** Server-side authentication (currently client-side only)

**Found a security vulnerability?** Please report it privately to: matt@death2data.com

See [SECURITY_FIX_PLAN.md](SECURITY_FIX_PLAN.md) for ongoing security improvements.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Quick start:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run security audit: `python .github/scripts/site-audit.py`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Testing

Run the automated site audit:

```bash
cd .github/scripts
python site-audit.py
```

This checks for:
- Broken links
- JavaScript syntax errors
- Missing security.js includes
- Hardcoded secrets
- Accessibility issues

## Deployment

The site automatically deploys to GitHub Pages when changes are pushed to the `main` branch.

**Production URL:** https://death2data.com
**Staging URL:** https://staging.death2data.com (if configured)

## Roadmap

- [x] Privacy-first search engine
- [x] QR code generator
- [x] 28-day cycling notebook
- [x] Word of the Day system
- [ ] Server-side authentication (currently client-side only)
- [ ] PDF processor (offline mode)
- [ ] Browser extension
- [ ] Mobile apps (iOS/Android)
- [ ] Multi-language support

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation:** [docs/](./docs/)
- **FAQ:** [docs/faq.html](./docs/faq.html)
- **Email:** matt@death2data.com
- **Issues:** [GitHub Issues](https://github.com/deathtodata/deathtodata.github.io/issues)

## Philosophy

Death2Data believes in:
- **Privacy by Default** - No tracking, no ads, no data collection
- **Simplicity** - Clean, fast, accessible tools
- **Transparency** - Open source, auditable code
- **Affordability** - $1/month for everything
- **User Control** - Your data, your choice

---

**Built with ❤️ for privacy advocates everywhere.**
