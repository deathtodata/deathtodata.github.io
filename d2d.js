/**
 * D2D Pixel - Privacy-First Analytics
 * ====================================
 * 
 * COLLECTS: path, referrer domain, device type, bot classification
 * NEVER COLLECTS: IP, cookies, fingerprints, user IDs, query params
 * 
 * Size target: < 2KB gzipped
 * Execution: < 20ms
 * Blocking: NONE
 * 
 * @version 1.0.0
 * @license MIT
 */

(function(window, document) {
  'use strict';

  // ═══════════════════════════════════════════════════════════════════════════
  // CONFIGURATION
  // ═══════════════════════════════════════════════════════════════════════════
  
  var CONFIG = window.D2D_CONFIG || {};
  var ENDPOINT = CONFIG.endpoint || 'https://death2data.com/api/collect';
  var SITE_ID = CONFIG.site_id || 'd2d_default';

  // ═══════════════════════════════════════════════════════════════════════════
  // BOT DETECTION
  // ═══════════════════════════════════════════════════════════════════════════
  
  var BOT_PATTERNS = {
    // AI Crawlers (primary interest)
    'gptbot': /gptbot|chatgpt-user/i,
    'claudebot': /claudebot|claude-web|anthropic-ai/i,
    'perplexity': /perplexitybot/i,
    'cohere': /cohere-ai/i,
    'bytedance': /bytespider/i,
    'meta-ai': /meta-externalagent/i,
    
    // Search engines
    'googlebot': /googlebot|google-extended/i,
    'bingbot': /bingbot|msnbot/i,
    'duckduckgo': /duckduckbot/i,
    'yandex': /yandexbot/i,
    'baidu': /baiduspider/i,
    
    // Social
    'facebook': /facebookexternalhit|facebot/i,
    'twitter': /twitterbot/i,
    'linkedin': /linkedinbot/i,
    'discord': /discordbot/i,
    'slack': /slackbot/i,
    
    // Generic bot patterns
    'unknown': /bot|crawler|spider|scraper|fetch|wget|curl|python|java\/|go-http|node-fetch|headless|phantom|selenium|puppeteer/i
  };

  function detectBot(ua) {
    if (!ua || ua.length === 0) return 'unknown';
    
    var uaLower = ua.toLowerCase();
    
    // Check specific bots first (in order of priority)
    var botTypes = [
      'gptbot', 'claudebot', 'perplexity', 'cohere', 'bytedance', 'meta-ai',
      'googlebot', 'bingbot', 'duckduckgo', 'yandex', 'baidu',
      'facebook', 'twitter', 'linkedin', 'discord', 'slack',
      'unknown'
    ];
    
    for (var i = 0; i < botTypes.length; i++) {
      if (BOT_PATTERNS[botTypes[i]].test(uaLower)) {
        return botTypes[i];
      }
    }
    
    return null; // Human
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // DATA SANITIZATION
  // ═══════════════════════════════════════════════════════════════════════════
  
  function sanitizePath(path) {
    if (!path) return '/';
    
    // Remove query string
    var clean = path.split('?')[0];
    
    // Remove hash
    clean = clean.split('#')[0];
    
    // Remove potential PII patterns
    clean = clean
      .replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[email]')
      .replace(/\d{3}[-.\s]?\d{3}[-.\s]?\d{4}/g, '[phone]')
      .replace(/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/g, '[ip]');
    
    // Limit length
    if (clean.length > 200) {
      clean = clean.substring(0, 200);
    }
    
    return clean || '/';
  }

  function sanitizeReferrer(ref, siteDomain) {
    if (!ref) return 'direct';
    
    try {
      var url = new URL(ref);
      var domain = url.hostname.replace(/^www\./, '');
      
      // Check if same-site
      if (siteDomain && domain === siteDomain.replace(/^www\./, '')) {
        return 'internal';
      }
      
      return domain;
    } catch (e) {
      return 'direct';
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // DEVICE DETECTION
  // ═══════════════════════════════════════════════════════════════════════════
  
  function detectDevice() {
    var ua = navigator.userAgent || '';
    
    if (/mobile|android|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(ua)) {
      return /ipad|tablet/i.test(ua) ? 'tablet' : 'mobile';
    }
    
    return 'desktop';
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // EVENT TRANSMISSION
  // ═══════════════════════════════════════════════════════════════════════════
  
  function sendEvent(data) {
    // Use sendBeacon for reliability (fire-and-forget)
    if (navigator.sendBeacon) {
      var blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
      navigator.sendBeacon(ENDPOINT, blob);
      return;
    }
    
    // Fallback to fetch with keepalive
    if (window.fetch) {
      fetch(ENDPOINT, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: { 'Content-Type': 'application/json' },
        keepalive: true,
        mode: 'cors'
      }).catch(function() {});
      return;
    }
    
    // Last resort: XHR
    try {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', ENDPOINT, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify(data));
    } catch (e) {}
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // MAIN
  // ═══════════════════════════════════════════════════════════════════════════
  
  function collect() {
    var ua = navigator.userAgent || '';
    var bot = detectBot(ua);
    
    var event = {
      v: 1,                                              // Schema version
      site_id: SITE_ID,                                  // Site identifier
      path: sanitizePath(window.location.pathname),      // Page path (sanitized)
      ref: sanitizeReferrer(document.referrer, window.location.hostname), // Referrer domain only
      device: detectDevice(),                            // mobile|desktop|tablet
      bot: bot                                           // Bot name or null
      // NOTE: No IP, no cookies, no fingerprint, no timestamp (server adds)
    };
    
    sendEvent(event);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // INITIALIZATION
  // ═══════════════════════════════════════════════════════════════════════════
  
  // Run when DOM is ready (non-blocking)
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(collect, 0);
  } else {
    document.addEventListener('DOMContentLoaded', collect);
  }

  // Expose for testing (optional)
  window.__d2d = {
    detectBot: detectBot,
    sanitizePath: sanitizePath,
    sanitizeReferrer: sanitizeReferrer,
    detectDevice: detectDevice
  };

})(window, document);
