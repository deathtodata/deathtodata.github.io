// ================================================================
// D2D Security Utilities
// Include this on pages that handle user input
// ================================================================
// Usage: <script src="/js/security.js"></script>
// ================================================================

/**
 * Sanitize HTML to prevent XSS attacks
 * Converts special characters to HTML entities
 * Example: "<script>alert('xss')</script>" → "&lt;script&gt;alert('xss')&lt;/script&gt;"
 */
function sanitizeHTML(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;  // Browser automatically escapes HTML
  return div.innerHTML;
}

/**
 * Validate URL to prevent SSRF attacks
 * Only allows http:// and https:// protocols
 * Blocks internal/private IP addresses
 */
function validateURL(url) {
  if (!url || typeof url !== 'string') {
    return { valid: false, error: 'URL is required' };
  }

  try {
    const parsed = new URL(url);

    // Only allow HTTP/HTTPS protocols
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return { valid: false, error: 'Only HTTP and HTTPS URLs allowed' };
    }

    // Block internal/private IP addresses
    const hostname = parsed.hostname.toLowerCase();
    const blocked = [
      // Localhost variations
      'localhost',
      '127.0.0.1',
      '0.0.0.0',
      '::1',
      '[::1]',
      // Private IP ranges (regex patterns)
      /^10\./,                    // 10.0.0.0/8
      /^172\.(1[6-9]|2[0-9]|3[01])\./, // 172.16.0.0/12
      /^192\.168\./,              // 192.168.0.0/16
      /^169\.254\./,              // 169.254.0.0/16 (AWS metadata service)
      /^fd[0-9a-f]{2}:/i,         // IPv6 unique local addresses
      /^fe80:/i,                  // IPv6 link-local addresses
    ];

    for (const pattern of blocked) {
      if (typeof pattern === 'string' && hostname === pattern) {
        return { valid: false, error: 'Internal/private URLs not allowed' };
      }
      if (pattern instanceof RegExp && pattern.test(hostname)) {
        return { valid: false, error: 'Internal/private URLs not allowed' };
      }
    }

    return { valid: true, url: parsed.toString() };

  } catch (e) {
    return { valid: false, error: 'Invalid URL format' };
  }
}

/**
 * Validate text input length
 * Prevents DOS attacks via oversized inputs
 */
function validateLength(str, maxLength, fieldName = 'Input') {
  if (!str || str.trim().length === 0) {
    return { valid: false, error: `${fieldName} is required` };
  }
  if (str.length > maxLength) {
    return { valid: false, error: `${fieldName} too long (max ${maxLength} characters)` };
  }
  if (str.trim().length < 1) {
    return { valid: false, error: `${fieldName} cannot be empty` };
  }
  return { valid: true };
}

/**
 * Simple rate limiter (client-side check only)
 * Server MUST also enforce rate limits - this is just UX
 */
class RateLimiter {
  constructor(maxRequests, windowMs) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
  }

  check(key) {
    const now = Date.now();
    const storageKey = `ratelimit_${key}`;

    try {
      // Load request history from localStorage
      const stored = localStorage.getItem(storageKey);
      let requests = stored ? JSON.parse(stored) : [];

      // Remove requests outside the time window
      requests = requests.filter(timestamp => now - timestamp < this.windowMs);

      // Check if limit exceeded
      if (requests.length >= this.maxRequests) {
        const oldestRequest = Math.min(...requests);
        const waitTime = Math.ceil((this.windowMs - (now - oldestRequest)) / 1000);
        return { allowed: false, waitTime };
      }

      // Add current request
      requests.push(now);
      localStorage.setItem(storageKey, JSON.stringify(requests));

      return { allowed: true };

    } catch (e) {
      // If localStorage fails, allow the request (server will enforce)
      console.warn('Rate limiter error:', e);
      return { allowed: true };
    }
  }

  reset(key) {
    const storageKey = `ratelimit_${key}`;
    localStorage.removeItem(storageKey);
  }
}

/**
 * Enforce HTTPS in production
 * Automatically redirects HTTP to HTTPS (except localhost)
 */
function enforceHTTPS() {
  if (location.protocol !== 'https:' &&
      location.hostname !== 'localhost' &&
      location.hostname !== '127.0.0.1') {
    location.replace('https:' + window.location.href.substring(window.location.protocol.length));
  }
}

/**
 * Validate email format (basic check)
 */
function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email || !emailRegex.test(email)) {
    return { valid: false, error: 'Invalid email format' };
  }
  if (email.length > 254) {
    return { valid: false, error: 'Email too long' };
  }
  return { valid: true };
}

/**
 * Prevent multiple rapid submissions (button debounce)
 */
function debounceButton(button, durationMs = 2000) {
  button.disabled = true;
  const originalText = button.textContent;

  setTimeout(() => {
    button.disabled = false;
    button.textContent = originalText;
  }, durationMs);
}

// ================================================================
// Export utilities globally
// ================================================================
window.D2DSecurity = {
  sanitizeHTML,
  validateURL,
  validateLength,
  validateEmail,
  enforceHTTPS,
  debounceButton,
  RateLimiter
};

// Auto-enforce HTTPS on load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', enforceHTTPS);
} else {
  enforceHTTPS();
}
