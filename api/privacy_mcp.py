"""
Privacy Domain MCP Backend
Aggregates privacy news, data breach alerts, policy tracking
"""

import sys
import os
from pathlib import Path

# Add feed_engine to path
sys.path.insert(0, str(Path.home() / "Desktop" / "wavgroup" / "feed_engine"))

from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta
from aggregator import FeedAggregator

app = Flask(__name__)

# Privacy news sources
PRIVACY_SOURCES = [
    {'name': 'EFF', 'type': 'rss', 'url': 'https://www.eff.org/rss/updates.xml'},
    {'name': 'Techdirt', 'type': 'rss', 'url': 'https://www.techdirt.com/feed/'},
    {'name': 'Ars Technica Privacy', 'type': 'rss', 'url': 'https://feeds.arstechnica.com/arstechnica/security'},
    {'name': 'Privacy International', 'type': 'rss', 'url': 'https://privacyinternational.org/rss.xml'},
    {'name': 'The Privacy Hub', 'type': 'rss', 'url': 'https://theprivacyhub.com/feed/'},
]


class PrivacyAggregator(FeedAggregator):
    """Extended aggregator with privacy-specific functionality"""

    def get_data_breaches(self, days=30):
        """
        Get recent data breach notifications

        Args:
            days: Number of days to look back

        Returns:
            List of data breaches
        """
        items = []
        try:
            # Note: This would integrate with HaveIBeenPwned API
            # Requires API key from https://haveibeenpwned.com/API/Key

            # For now, filter breach-related content from feeds
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

            results = self.filter({
                'tags': 'breach',
                'date_from': from_date
            }, limit=50)

            # Also search for breach-related content
            breach_results = self.search('breach', limit=50)

            # Combine and deduplicate
            all_results = {item['id']: item for item in results + breach_results}
            items = list(all_results.values())

        except Exception as e:
            print(f"Error fetching data breaches: {e}")

        return items

    def track_privacy_policy(self, domain):
        """
        Track privacy policy changes for a domain

        Args:
            domain: Domain to track

        Returns:
            Policy tracking info
        """
        # This would integrate with the Death2Data platform
        # For now, return placeholder
        return {
            'domain': domain,
            'status': 'tracked',
            'note': 'Requires Death2Data platform integration',
            'related_domains': [
                'deathtodata.com',
                'deathtobigtech.com',
                'deathtotwitter.com'
            ]
        }

    def analyze_privacy_policy(self, url):
        """
        Analyze a privacy policy URL

        Args:
            url: Privacy policy URL

        Returns:
            Analysis results
        """
        # This would use the existing qr-generator and privacy tools
        return {
            'url': url,
            'status': 'analyzed',
            'note': 'Requires integration with Death2Data privacy analysis tools',
            'tools_available': [
                'QR Code Generator',
                'Privacy Policy Analyzer',
                'Cookie Tracker'
            ]
        }

    def get_legislation_updates(self):
        """Get privacy legislation updates (GDPR, CCPA, etc.)"""
        items = []

        # Search for legislation keywords
        keywords = ['GDPR', 'CCPA', 'privacy law', 'data protection']

        for keyword in keywords:
            results = self.search(keyword, limit=10)
            items.extend(results)

        # Deduplicate
        unique_items = {item['id']: item for item in items}
        return list(unique_items.values())


# Create privacy aggregator
privacy_agg = PrivacyAggregator('privacy')
for source in PRIVACY_SOURCES:
    privacy_agg.add_source(source['name'], source['type'], source['url'])


# MCP Tool Definitions
TOOLS = [
    {
        "name": "privacy_feed",
        "description": "Get aggregated privacy news from EFF, Techdirt, Ars Technica, Privacy International",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "number",
                    "description": "Maximum number of items to return",
                    "default": 50
                },
                "offset": {
                    "type": "number",
                    "description": "Offset for pagination",
                    "default": 0
                }
            }
        }
    },
    {
        "name": "privacy_search",
        "description": "Search across all privacy news sources",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "limit": {
                    "type": "number",
                    "description": "Maximum results",
                    "default": 50
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "privacy_breaches",
        "description": "Get recent data breach notifications",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {
                    "type": "number",
                    "description": "Number of days to look back",
                    "default": 30
                }
            }
        }
    },
    {
        "name": "privacy_track_domain",
        "description": "Track privacy policy changes for a domain",
        "inputSchema": {
            "type": "object",
            "properties": {
                "domain": {
                    "type": "string",
                    "description": "Domain to track (e.g., facebook.com)"
                }
            },
            "required": ["domain"]
        }
    },
    {
        "name": "privacy_analyze_policy",
        "description": "Analyze a privacy policy URL",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Privacy policy URL to analyze"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "privacy_legislation",
        "description": "Get updates on privacy legislation (GDPR, CCPA, etc.)",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "privacy_aggregate",
        "description": "Manually trigger feed aggregation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "force": {
                    "type": "boolean",
                    "description": "Force refresh",
                    "default": False
                }
            }
        }
    }
]


@app.route('/mcp', methods=['POST'])
def mcp_handler():
    """MCP protocol handler"""
    data = request.get_json()

    method = data.get('method')
    params = data.get('params', {})

    # List available tools
    if method == 'tools/list':
        return jsonify({"tools": TOOLS})

    # Call tool
    if method == 'tools/call':
        tool_name = params.get('name')
        arguments = params.get('arguments', {})

        if tool_name == 'privacy_feed':
            limit = arguments.get('limit', 50)
            offset = arguments.get('offset', 0)
            items = privacy_agg.get_feed(limit=limit, offset=offset)

            return jsonify({
                "content": [{
                    "type": "text",
                    "text": f"Found {len(items)} privacy news items:\n\n" +
                           "\n\n".join([
                               f"**{item['title']}**\n{item['source']} | {item['published']}\n{item['url']}\n{item['content'][:200]}..."
                               for item in items
                           ])
                }]
            })

        elif tool_name == 'privacy_search':
            query = arguments.get('query')
            limit = arguments.get('limit', 50)
            results = privacy_agg.search(query, limit=limit)

            return jsonify({
                "content": [{
                    "type": "text",
                    "text": f"Found {len(results)} results for '{query}':\n\n" +
                           "\n\n".join([
                               f"**{item['title']}**\n{item['source']} | {item['published']}\n{item['url']}"
                               for item in results
                           ])
                }]
            })

        elif tool_name == 'privacy_breaches':
            days = arguments.get('days', 30)
            breaches = privacy_agg.get_data_breaches(days=days)

            return jsonify({
                "content": [{
                    "type": "text",
                    "text": f"Data Breaches (last {days} days):\n\n" +
                           "\n\n".join([
                               f"**{item['title']}**\n{item['source']} | {item['published']}\n{item['url']}"
                               for item in breaches
                           ]) if breaches else "No recent data breach notifications found."
                }]
            })

        elif tool_name == 'privacy_track_domain':
            domain = arguments.get('domain')
            result = privacy_agg.track_privacy_policy(domain)

            return jsonify({
                "content": [{
                    "type": "text",
                    "text": f"Privacy Policy Tracking: {domain}\n\n" +
                           f"Status: {result['status']}\n" +
                           f"Note: {result['note']}\n\n" +
                           f"Related Death2Data domains:\n" +
                           "\n".join([f"- {d}" for d in result['related_domains']])
                }]
            })

        elif tool_name == 'privacy_analyze_policy':
            url = arguments.get('url')
            result = privacy_agg.analyze_privacy_policy(url)

            return jsonify({
                "content": [{
                    "type": "text",
                    "text": f"Privacy Policy Analysis: {url}\n\n" +
                           f"Status: {result['status']}\n" +
                           f"Note: {result['note']}\n\n" +
                           f"Available tools:\n" +
                           "\n".join([f"- {t}" for t in result['tools_available']])
                }]
            })

        elif tool_name == 'privacy_legislation':
            updates = privacy_agg.get_legislation_updates()

            return jsonify({
                "content": [{
                    "type": "text",
                    "text": "Privacy Legislation Updates:\n\n" +
                           "\n\n".join([
                               f"**{item['title']}**\n{item['source']} | {item['published']}\n{item['url']}"
                               for item in updates[:20]
                           ]) if updates else "No recent legislation updates found."
                }]
            })

        elif tool_name == 'privacy_aggregate':
            force = arguments.get('force', False)
            stats = privacy_agg.aggregate(force=force)

            return jsonify({
                "content": [{
                    "type": "text",
                    "text": f"Aggregation complete:\n- Fetched: {stats['fetched']} items\n- New: {stats['new']} items"
                }]
            })

        return jsonify({"error": f"Unknown tool: {tool_name}"}), 400

    return jsonify({"error": f"Unknown method: {method}"}), 400


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "domain": "privacy"})


if __name__ == '__main__':
    print("Starting Privacy MCP Backend...")
    print("Running initial aggregation...")
    stats = privacy_agg.aggregate()
    print(f"Initial aggregation: {stats['fetched']} fetched, {stats['new']} new")

    app.run(host='0.0.0.0', port=5003, debug=True)
