/**
 * D2D Analytics - Tracking Script
 * 
 * Privacy-first, no cookies, no PII
 * Drop this on any domain to track pageviews
 * 
 * Usage:
 *   <script src="https://analytics.death2data.com/t.js" data-site="cringe"></script>
 */

(function() {
  'use strict';

  // Config - override with data attributes
  const script = document.currentScript;
  const ENDPOINT = script?.getAttribute('data-endpoint') || 'https://analytics.death2data.com/collect';
  const SITE = script?.getAttribute('data-site') || window.location.hostname;

  // Generate anonymous session ID (not stored, just for grouping hits in same session)
  // Uses day + rough fingerprint, no tracking across days
  function getSessionId() {
    const today = new Date().toISOString().split('T')[0];
    const rough = [
      navigator.language,
      screen.width + 'x' + screen.height,
      new Date().getTimezoneOffset()
    ].join('|');
    
    // Simple hash
    let hash = 0;
    const str = today + rough;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i);
      hash = hash & hash;
    }
    return Math.abs(hash).toString(36);
  }

  // Get UTM params
  function getUtm() {
    const params = new URLSearchParams(window.location.search);
    return {
      source: params.get('utm_source') || params.get('ref') || null,
      medium: params.get('utm_medium') || null,
      campaign: params.get('utm_campaign') || null,
    };
  }

  // Get referrer domain only (not full URL for privacy)
  function getReferrer() {
    if (!document.referrer) return null;
    try {
      const url = new URL(document.referrer);
      // Don't track internal referrers
      if (url.hostname === window.location.hostname) return null;
      return url.hostname;
    } catch {
      return null;
    }
  }

  // Collect event data
  function collect(eventType, eventData = {}) {
    const data = {
      // Site/page
      site: SITE,
      path: window.location.pathname,
      
      // Event
      event: eventType,
      data: eventData,
      
      // Session (anonymous, not persistent)
      session: getSessionId(),
      
      // Attribution
      referrer: getReferrer(),
      utm: getUtm(),
      
      // Device (non-identifying)
      screen: screen.width + 'x' + screen.height,
      lang: navigator.language?.split('-')[0],
      
      // Timestamp
      ts: Date.now()
    };

    // Send via beacon (doesn't block page)
    if (navigator.sendBeacon) {
      navigator.sendBeacon(ENDPOINT, JSON.stringify(data));
    } else {
      // Fallback for older browsers
      fetch(ENDPOINT, {
        method: 'POST',
        body: JSON.stringify(data),
        keepalive: true
      }).catch(() => {});
    }
  }

  // Track pageview
  function trackPageview() {
    collect('pageview');
  }

  // Track custom events
  function trackEvent(name, data = {}) {
    collect('event', { name, ...data });
  }

  // Track outbound links
  function trackOutbound(url) {
    collect('outbound', { url });
  }

  // Auto-track SPA navigation
  function setupSpaTracking() {
    let lastPath = window.location.pathname;
    
    // History API
    const originalPushState = history.pushState;
    history.pushState = function() {
      originalPushState.apply(this, arguments);
      if (window.location.pathname !== lastPath) {
        lastPath = window.location.pathname;
        trackPageview();
      }
    };

    // Popstate (back/forward)
    window.addEventListener('popstate', () => {
      if (window.location.pathname !== lastPath) {
        lastPath = window.location.pathname;
        trackPageview();
      }
    });
  }

  // Auto-track outbound links
  function setupOutboundTracking() {
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a');
      if (!link) return;
      
      const href = link.getAttribute('href');
      if (!href) return;
      
      try {
        const url = new URL(href, window.location.origin);
        if (url.hostname !== window.location.hostname) {
          trackOutbound(url.hostname);
        }
      } catch {}
    });
  }

  // Initialize
  function init() {
    // Don't track if DNT is enabled (respect user preference)
    if (navigator.doNotTrack === '1') {
      console.log('[D2D Analytics] Respecting Do Not Track');
      return;
    }

    // Don't track localhost/dev
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      console.log('[D2D Analytics] Skipping localhost');
      return;
    }

    // Track initial pageview
    trackPageview();

    // Setup auto-tracking
    setupSpaTracking();
    setupOutboundTracking();

    // Expose API for manual tracking
    window.d2d = {
      track: trackEvent,
      pageview: trackPageview
    };
  }

  // Run when DOM ready
  if (document.readyState === 'complete') {
    init();
  } else {
    window.addEventListener('load', init);
  }
})();
