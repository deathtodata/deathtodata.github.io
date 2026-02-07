#!/usr/bin/env python3
"""
D2D Site Audit - CI Version
Runs on every push to catch broken links, JS errors, etc.
"""

import os
import re
import json
import sys
from pathlib import Path
from collections import defaultdict

class SiteAudit:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.html_files = []
        self.issues = defaultdict(list)
        self.all_files = set()

    def scan_files(self):
        for f in self.repo_path.rglob('*'):
            if f.is_file() and not any(p.startswith('.') for p in f.parts):
                rel = str(f.relative_to(self.repo_path))
                self.all_files.add(rel)
                if f.suffix == '.html':
                    self.html_files.append(f)
        print(f"Scanned {len(self.html_files)} HTML files")

    def check_links(self, html_file):
        content = html_file.read_text(errors='ignore')
        rel_path = str(html_file.relative_to(self.repo_path))

        hrefs = re.findall(r'href=["\']([^"\']+)["\']', content)
        srcs = re.findall(r'src=["\']([^"\']+)["\']', content)

        for link in hrefs + srcs:
            if link.startswith(('http://', 'https://', '#', 'javascript:', 'mailto:', 'tel:', 'data:')):
                continue

            target = link.lstrip('/').split('?')[0].split('#')[0]
            if not target:
                continue

            # Check if file exists (with or without .html)
            if target not in self.all_files:
                if target + '.html' not in self.all_files:
                    if target + '/index.html' not in self.all_files:
                        if not (self.repo_path / target).is_dir():
                            self.issues['broken_links'].append({
                                'file': rel_path,
                                'link': link,
                                'resolved': target
                            })

    def check_js_syntax(self, html_file):
        content = html_file.read_text(errors='ignore')
        rel_path = str(html_file.relative_to(self.repo_path))

        # Check for tagged template literal misuse
        bad_patterns = [
            (r'(?<![a-zA-Z])alert`', 'alert` should be alert('),
            (r'(?<![a-zA-Z])fetch`', 'fetch` should be fetch('),
            (r'console\.log`', 'console.log` should be console.log('),
        ]

        for pattern, msg in bad_patterns:
            if re.search(pattern, content):
                self.issues['js_syntax'].append({
                    'file': rel_path,
                    'issue': msg
                })

    def check_api_consistency(self, html_file):
        content = html_file.read_text(errors='ignore')
        rel_path = str(html_file.relative_to(self.repo_path))

        # Look for hardcoded API URLs (exclude fonts)
        apis = re.findall(r'["\']https?://[^"\']*api[^"\']*["\']', content, re.I)
        apis = [a for a in apis if 'fonts.googleapis' not in a]

        uses_config = 'config.js' in content or 'D2D_CONFIG' in content

        if apis and not uses_config:
            for api in apis:
                self.issues['api_hardcoded'].append({
                    'file': rel_path,
                    'url': api
                })

    def run_audit(self):
        self.scan_files()
        for html_file in self.html_files:
            self.check_links(html_file)
            self.check_js_syntax(html_file)
            self.check_api_consistency(html_file)
        return self.issues

    def print_report(self, ci_mode=False):
        total = sum(len(v) for v in self.issues.values())

        if ci_mode:
            print(f"\n{'='*60}")
            print("AUDIT RESULTS")
            print(f"{'='*60}")

        if self.issues['js_syntax']:
            print(f"\n🔴 JS SYNTAX ERRORS: {len(self.issues['js_syntax'])}")
            for i in self.issues['js_syntax']:
                print(f"   {i['file']}: {i['issue']}")

        if self.issues['api_hardcoded']:
            print(f"\n🟠 HARDCODED APIs: {len(self.issues['api_hardcoded'])}")
            for i in self.issues['api_hardcoded'][:5]:
                print(f"   {i['file']}")

        if self.issues['broken_links']:
            print(f"\n🟡 BROKEN LINKS: {len(self.issues['broken_links'])}")
            for i in self.issues['broken_links'][:10]:
                print(f"   {i['file']} → {i['link']}")
            if len(self.issues['broken_links']) > 10:
                print(f"   ... and {len(self.issues['broken_links']) - 10} more")

        print(f"\nTOTAL ISSUES: {total}")
        return total

    def save_report(self, path='audit-report.json'):
        report = {
            'total_files': len(self.html_files),
            'issues': dict(self.issues),
            'summary': {k: len(v) for k, v in self.issues.items()}
        }
        with open(path, 'w') as f:
            json.dump(report, f, indent=2)


if __name__ == '__main__':
    repo_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    ci_mode = '--ci' in sys.argv

    audit = SiteAudit(repo_path)
    audit.run_audit()
    total = audit.print_report(ci_mode)
    audit.save_report()

    # Exit with error if critical issues in CI mode
    if ci_mode and audit.issues['js_syntax']:
        sys.exit(1)
