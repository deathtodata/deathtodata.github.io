#!/bin/bash
# Script to add security.js to pages that handle user input
# This prevents XSS vulnerabilities

echo "Adding security.js to vulnerable pages..."

# List of pages that need security.js
PAGES=(
  "search.html"
  "admin.html"
  "dashboard.html"
  "manage.html"
  "auth.html"
  "gate.html"
  "tools/account.html"
  "tools/identity-vault.html"
  "analytics.html"
)

for page in "${PAGES[@]}"; do
  if [ -f "$page" ]; then
    # Check if security.js is already included
    if grep -q "security.js" "$page"; then
      echo "  ✓ $page already includes security.js"
    else
      # Add security.js after the first <head> tag
      # This is a simple approach - may need manual adjustment
      sed -i.bak '/<head>/a\
    <script src="/js/security.js"></script>' "$page"
      echo "  ✓ Added security.js to $page"
    fi
  else
    echo "  ⚠ $page not found"
  fi
done

echo ""
echo "Done! Review the changes and test before committing."
echo "Note: browse.html already includes security.js"
