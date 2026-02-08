# Contributing to Death2Data

Thank you for considering contributing to Death2Data! We welcome contributions from the community.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Browser/environment details
- Screenshots (if applicable)

### Suggesting Features

We welcome feature suggestions! Please:
- Check if the feature has already been requested
- Describe the use case and benefit
- Consider privacy implications
- Keep it aligned with our privacy-first philosophy

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/deathtodata/deathtodata.github.io.git
   cd deathtodata.github.io
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Write clean, readable code
   - Add comments for complex logic
   - Test your changes locally

4. **Run security audit**
   ```bash
   cd .github/scripts
   python site-audit.py
   ```
   Fix any issues reported before submitting.

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

   Use conventional commit messages:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting)
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Describe what your PR does
   - Reference any related issues
   - Include screenshots for UI changes
   - Ensure all checks pass

## Development Guidelines

### Code Style

- **HTML:** Clean, semantic markup
- **CSS:** Mobile-first, accessible styles
- **JavaScript:** Vanilla JS (no frameworks), ES6+ syntax
- **Indentation:** 2 spaces (not tabs)
- **Comments:** Explain "why" not "what"

### Security Requirements

**CRITICAL:** All contributions must follow security best practices:

1. **Never commit secrets**
   - Use environment variables for API keys
   - Check `.gitignore` is working
   - Review git history before pushing

2. **Sanitize user input**
   - Use `D2DSecurity.sanitizeHTML()` for all user-provided text
   - Never use `innerHTML` with untrusted data
   - Validate URLs with `D2DSecurity.validateURL()`

3. **Include security.js**
   - Add `<script src="/js/security.js"></script>` to any page handling user input
   - Use rate limiting for API calls
   - Enforce HTTPS in production

4. **Test for XSS**
   - Try to inject `<script>alert('xss')</script>` in all input fields
   - Verify it's properly escaped
   - Test with browser DevTools console

### File Organization

Follow the repository structure:

```
/public/     - Public-facing pages (homepage, pricing, etc.)
/admin/      - Admin dashboards (requires authentication)
/tools/      - Member tools (QR generator, notebook, etc.)
/docs/       - Documentation
/css/        - Stylesheets
/js/         - JavaScript modules
/k/          - Word of the Day system
/.github/    - CI/CD workflows
```

### Accessibility

- Use semantic HTML (`<nav>`, `<main>`, `<article>`)
- Provide alt text for images
- Ensure keyboard navigation works
- Test with screen readers (if possible)
- Use sufficient color contrast (WCAG AA)

### Performance

- Minimize HTTP requests
- Optimize images (use SVG when possible)
- Avoid external dependencies (except CDN libraries)
- Keep JavaScript files small (<50KB)
- Test on slow connections

### Testing

Before submitting:

1. **Manual Testing**
   - Test in Chrome, Firefox, Safari
   - Test on mobile devices
   - Test with JavaScript disabled (where applicable)
   - Test with ad blockers enabled

2. **Automated Testing**
   ```bash
   python .github/scripts/site-audit.py
   ```
   This checks for:
   - Broken links
   - JavaScript syntax errors
   - Missing security includes
   - Hardcoded secrets

3. **Browser DevTools**
   - Check console for errors
   - Verify no 404s in Network tab
   - Test responsive design

## Privacy Philosophy

Death2Data is privacy-first. All contributions must:

- ✅ **NO tracking** - No analytics, no third-party cookies
- ✅ **NO ads** - No advertising, no affiliate links
- ✅ **NO data collection** - Minimal data storage, user-controlled deletion
- ✅ **Open source** - Code is auditable and transparent
- ✅ **User control** - Users own their data

If your contribution conflicts with these principles, it will not be accepted.

## What We're Looking For

**High Priority:**
- Security improvements
- Bug fixes
- Performance optimizations
- Accessibility improvements
- Documentation updates

**Medium Priority:**
- New privacy-focused tools
- UI/UX improvements
- Mobile responsiveness fixes
- Test coverage

**Low Priority:**
- Marketing materials
- Non-essential features
- Cosmetic changes

## Review Process

1. **Automated checks** - GitHub Actions will run security and link checks
2. **Code review** - Maintainers will review your code
3. **Testing** - We'll test your changes locally
4. **Feedback** - We may request changes or improvements
5. **Merge** - Once approved, we'll merge and deploy

**Typical response time:** 2-5 business days

## Getting Help

- **Documentation:** [docs/](./docs/)
- **Issues:** [GitHub Issues](https://github.com/deathtodata/deathtodata.github.io/issues)
- **Email:** matt@death2data.com

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

**Thank you for contributing to privacy-first software!** 🔒
