#!/bin/bash
# Fix broken links after repository reorganization

echo "🔗 Fixing broken links after reorganization..."
echo ""

# Map of old paths to new paths
declare -A LINK_MAP=(
  ["/admin.html"]="/admin/admin.html"
  ["/dashboard.html"]="/admin/dashboard.html"
  ["/manage.html"]="/admin/manage.html"
  ["/analytics.html"]="/admin/analytics.html"
  ["/revenue.html"]="/admin/revenue.html"
  ["/grants.html"]="/admin/grants.html"
  ["/grant-materials.html"]="/admin/grant-materials.html"
  ["/business-cards.html"]="/admin/business-cards.html"
  ["/event-display.html"]="/admin/event-display.html"
  ["/widget.html"]="/admin/widget.html"
  ["/debug.html"]="/admin/debug.html"
  ["/check.html"]="/admin/check.html"
  ["/keyword.html"]="/admin/keyword.html"
  ["/notebook.html"]="/tools/notebook.html"
  ["/qr-generator.html"]="/tools/qr-generator.html"
)

# Also handle paths without leading slash and relative paths
declare -A RELATIVE_MAP=(
  ["manage.html"]="admin/manage.html"
  ["dashboard.html"]="admin/dashboard.html"
  ["admin.html"]="admin/admin.html"
  ["analytics.html"]="admin/analytics.html"
  ["revenue.html"]="admin/revenue.html"
  ["grants.html"]="admin/grants.html"
  ["notebook.html"]="tools/notebook.html"
  ["qr-generator.html"]="tools/qr-generator.html"
)

# Files to update (all HTML files in root, docs, k, tools)
FILES_TO_UPDATE=$(find . -maxdepth 1 -name "*.html" -o -path "./docs/*.html" -o -path "./k/*.html" -o -path "./tools/*.html")

# Create backups directory
mkdir -p .link-fix-backups

for file in $FILES_TO_UPDATE; do
  if [ -f "$file" ]; then
    # Create backup
    cp "$file" ".link-fix-backups/$(basename $file).bak"

    # Replace absolute paths (/path.html)
    for old_path in "${!LINK_MAP[@]}"; do
      new_path="${LINK_MAP[$old_path]}"
      # Use sed with different delimiters to avoid escaping issues
      sed -i.tmp "s|href=\"$old_path\"|href=\"$new_path\"|g" "$file"
      sed -i.tmp "s|href='$old_path'|href='$new_path'|g" "$file"
      sed -i.tmp "s|location='$old_path'|location='$new_path'|g" "$file"
      sed -i.tmp "s|location=\"$old_path\"|location=\"$new_path\"|g" "$file"
      sed -i.tmp "s|window.location='$old_path'|window.location='$new_path'|g" "$file"
      sed -i.tmp "s|window.location=\"$old_path\"|window.location=\"$new_path\"|g" "$file"
      sed -i.tmp "s|window.location.href='$old_path'|window.location.href='$new_path'|g" "$file"
      sed -i.tmp "s|window.location.href=\"$old_path\"|window.location.href=\"$new_path\"|g" "$file"
    done

    # Replace relative paths (path.html without /)
    for old_path in "${!RELATIVE_MAP[@]}"; do
      new_path="${RELATIVE_MAP[$old_path]}"
      # Only replace when it's not already prefixed with admin/ or tools/
      sed -i.tmp "s|href=\"$old_path\"|href=\"$new_path\"|g" "$file"
      sed -i.tmp "s|href='$old_path'|href='$new_path'|g" "$file"
    done

    # Clean up temporary files
    rm -f "$file.tmp"

    echo "  ✓ Updated links in $file"
  fi
done

echo ""
echo "✨ Link fixing complete!"
echo ""
echo "Backups saved to .link-fix-backups/"
echo ""
echo "Next steps:"
echo "  1. Test the site locally: python3 -m http.server 3000"
echo "  2. Run audit again: python .github/scripts/site-audit.py"
echo "  3. If issues found, check .link-fix-backups/ for originals"
