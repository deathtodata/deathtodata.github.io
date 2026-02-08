#!/bin/bash
# Death2Data Repository Reorganization Script
# IMPORTANT: GitHub Pages requires index.html in root, so we keep main pages there

set -e  # Exit on error

echo "🔧 Death2Data Repository Reorganization"
echo "========================================"
echo ""
echo "NOTE: Keeping main pages in root for GitHub Pages compatibility"
echo ""

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p admin
echo "✅ Directories created"
echo ""

# Move admin pages to admin/
echo "🔐 Moving admin pages to admin/..."
ADMIN_PAGES=(
  "admin.html"
  "dashboard.html"
  "manage.html"
  "analytics.html"
  "revenue.html"
  "grants.html"
  "grant-materials.html"
  "business-cards.html"
  "event-display.html"
  "widget.html"
  "debug.html"
  "check.html"
  "keyword.html"
)

for file in "${ADMIN_PAGES[@]}"; do
  if [ -f "$file" ]; then
    mv "$file" "admin/"
    echo "  ✓ Moved $file to admin/"
  fi
done
echo ""

# Move notebook and qr-generator to tools/ (if not already there)
echo "🛠️  Moving tools to tools/..."
if [ -f "notebook.html" ] && [ ! -f "tools/notebook.html" ]; then
  mv "notebook.html" "tools/"
  echo "  ✓ Moved notebook.html to tools/"
fi
if [ -f "qr-generator.html" ] && [ ! -f "tools/qr-generator.html" ]; then
  mv "qr-generator.html" "tools/"
  echo "  ✓ Moved qr-generator.html to tools/"
fi
echo ""

# Move template files
echo "📋 Moving template files..."
if [ -f "_template.html" ]; then
  mkdir -p .templates
  mv "_template.html" ".templates/"
  echo "  ✓ Moved _template.html to .templates/"
fi
echo ""

# Keep public pages in root for GitHub Pages
echo "🌐 Public pages kept in root (GitHub Pages requirement):"
PUBLIC_PAGES=(
  "index.html"
  "join.html"
  "pricing.html"
  "browse.html"
  "terms.html"
  "privacy.html"
  "welcome.html"
  "success.html"
  "checkout.html"
  "auth.html"
  "gate.html"
  "me.html"
  "members.html"
  "onboard.html"
  "recover.html"
  "restore.html"
  "tools.html"
)

for file in "${PUBLIC_PAGES[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✓ $file (public-facing, kept in root)"
  fi
done
echo ""

# Keep tools/, docs/, k/ folders as-is
echo "📚 Existing organized directories:"
echo "  ✓ tools/ (member tools)"
echo "  ✓ docs/ (documentation)"
echo "  ✓ k/ (Word of the Day)"
echo "  ✓ css/ (stylesheets)"
echo "  ✓ js/ (JavaScript modules)"
echo "  ✓ .github/ (CI/CD)"
echo ""

# Root files that should stay
echo "📄 Root configuration files:"
ROOT_FILES=(
  "404.html"
  "CNAME"
  "README.md"
  "LICENSE"
  "CONTRIBUTING.md"
  "SECURITY_FIX_PLAN.md"
  "SECURITY_AUDIT.md"
  "config.js"
  "d2d.js"
  "robots.txt"
  ".gitignore"
  ".env.example"
)

for file in "${ROOT_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✓ $file"
  fi
done
echo ""

echo "✨ Reorganization complete!"
echo ""
echo "📊 New structure:"
echo "  / (root)        - Public pages (index.html, join.html, etc.)"
echo "  /admin/         - Admin dashboards and internal tools"
echo "  /tools/         - Member tools (QR generator, notebook, etc.)"
echo "  /docs/          - Documentation"
echo "  /k/             - Word of the Day system"
echo "  /css/           - Stylesheets"
echo "  /js/            - JavaScript modules"
echo ""
echo "⚠️  Next steps:"
echo "  1. Review the changes: git status"
echo "  2. Update any links pointing to moved admin pages"
echo "  3. Test the site locally: python3 -m http.server 3000"
echo "  4. Run audit: python .github/scripts/site-audit.py"
echo "  5. Commit: git add . && git commit -m 'refactor: move admin pages to admin/ folder'"
