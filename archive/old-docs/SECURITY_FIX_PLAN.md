# Security Fix Implementation Plan

This document details HOW to fix each vulnerability identified in `SECURITY_AUDIT.md`.

## Implementation Status (Updated: 2025-02-08)

### ✅ Completed Fixes

- ✅ **Created `.gitignore`** - Prevents secrets, backup files, and environment variables from being committed
- ✅ **Environment variable system** - Created `.env.example` and `js/env.js` for safe configuration management
- ✅ **Removed Stripe keys from config.js** - Replaced hardcoded keys with environment variable references
- ✅ **Security.js exists and is included in browse.html** - XSS protection utilities available
- ✅ **Removed backup files** - Deleted `.bak` and `.backup` files from repository
- ✅ **Added robots.txt protection** - Search engines blocked from indexing admin pages
- ✅ **CI/CD security checks** - GitHub Actions workflow now checks for hardcoded secrets
- ✅ **Documentation added** - README.md, LICENSE, CONTRIBUTING.md created

### 🚧 In Progress

- 🚧 **Repository reorganization** - Moving files to `public/`, `admin/`, `tools/` folders
- 🚧 **Broken link fixes** - Need to run audit and fix after reorganization
- 🚧 **Security.js application** - Need to add to more pages handling user input

### ⏳ Planned (Backend Required)

- ⏳ **Server-side authentication** - Replace client-side localStorage auth with JWT tokens
- ⏳ **Cloudflare Workers backend** - Create `/api/auth/verify` endpoint
- ⏳ **Admin page protection** - Move admin pages behind server-side auth

### ⚠️ Known Limitations

**CRITICAL:** Client-side authentication is still insecure. Users can bypass by editing localStorage:
```javascript
localStorage.setItem('d2d_member', JSON.stringify({tier: 'premium'}));
```
This requires backend implementation (Cloudflare Workers) to fix properly.

---

## Phase 1: Critical XSS Fixes (30 minutes)

### Fix 1: Create Sanitization Helper

**File:** Create `/js/security.js`

```javascript
// ================================================================
// D2D Security Utilities
// ================================================================

/**
 * Sanitize HTML to prevent XSS
 * Escapes all HTML entities
 */
function sanitizeHTML(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/**
 * Validate URL to prevent SSRF
 * Only allow http:// and https:// protocols
 * Block internal IP addresses
 */
function validateURL(url) {
  try {
    const parsed = new URL(url);

    // Only allow HTTP/HTTPS
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return { valid: false, error: 'Only HTTP and HTTPS protocols allowed' };
    }

    // Block internal IPs
    const hostname = parsed.hostname.toLowerCase();
    const blocked = [
      'localhost',
      '127.0.0.1',
      '0.0.0.0',
      '::1',
      /^10\./,          // 10.0.0.0/8
      /^172\.(1[6-9]|2[0-9]|3[01])\./, // 172.16.0.0/12
      /^192\.168\./,    // 192.168.0.0/16
      /^169\.254\./,    // 169.254.0.0/16 (AWS metadata)
    ];

    for (const pattern of blocked) {
      if (typeof pattern === 'string' && hostname === pattern) {
        return { valid: false, error: 'Internal URLs not allowed' };
      }
      if (pattern instanceof RegExp && pattern.test(hostname)) {
        return { valid: false, error: 'Internal URLs not allowed' };
      }
    }

    return { valid: true, url: parsed.toString() };
  } catch (e) {
    return { valid: false, error: 'Invalid URL format' };
  }
}

/**
 * Validate input length
 */
function validateLength(str, maxLength, fieldName = 'Input') {
  if (!str) return { valid: false, error: `${fieldName} is required` };
  if (str.length > maxLength) {
    return { valid: false, error: `${fieldName} too long (max ${maxLength} characters)` };
  }
  return { valid: true };
}

/**
 * Rate limiter (client-side basic check)
 * Server should also enforce this
 */
class RateLimiter {
  constructor(maxRequests, windowMs) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
    this.requests = [];
  }

  check(key) {
    const now = Date.now();
    const storageKey = `ratelimit_${key}`;

    // Load from localStorage
    const stored = localStorage.getItem(storageKey);
    if (stored) {
      this.requests = JSON.parse(stored).filter(t => now - t < this.windowMs);
    }

    // Check limit
    if (this.requests.length >= this.maxRequests) {
      const oldestRequest = Math.min(...this.requests);
      const waitTime = Math.ceil((this.windowMs - (now - oldestRequest)) / 1000);
      return { allowed: false, waitTime };
    }

    // Add request
    this.requests.push(now);
    localStorage.setItem(storageKey, JSON.stringify(this.requests));
    return { allowed: true };
  }
}

// Export globally
window.D2DSecurity = {
  sanitizeHTML,
  validateURL,
  validateLength,
  RateLimiter
};
```

---

### Fix 2: Update browse.html

**File:** `/browse.html`

**Line 364 - Fix XSS:**
```javascript
// BEFORE:
document.getElementById('error-msg').innerHTML = msg;

// AFTER:
document.getElementById('error-msg').textContent = msg;
```

**Lines 273-278 - Add URL validation:**
```javascript
// Add at start of loadRemotePage():
async function loadRemotePage() {
  const urlInput = document.getElementById('url-input').value.trim();
  if (!urlInput) return;

  // SECURITY: Validate URL
  const validation = D2DSecurity.validateURL(urlInput);
  if (!validation.valid) {
    showError(validation.error);
    return;
  }
  const url = validation.url;

  // ... rest of function
}
```

**Add security.js include in `<head>`:**
```html
<script src="/js/security.js"></script>
```

---

### Fix 3: Update keyword.html

**File:** `/keyword.html`

**Lines 104-133 - Add validation and rate limiting:**
```javascript
// Add at top after keyword definition:
const perspectiveRateLimiter = new D2DSecurity.RateLimiter(10, 60 * 60 * 1000); // 10/hour

async function submit() {
  const btn = document.getElementById('submit-btn');
  const response = document.getElementById('response').value.trim();

  // SECURITY: Validate length
  const lengthCheck = D2DSecurity.validateLength(response, 5000, 'Perspective');
  if (!lengthCheck.valid) {
    alert(lengthCheck.error);
    return;
  }

  // SECURITY: Rate limiting
  const rateLimitCheck = perspectiveRateLimiter.check('perspective_submit');
  if (!rateLimitCheck.allowed) {
    alert(`Rate limit exceeded. Please wait ${rateLimitCheck.waitTime} seconds.`);
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Saving...';

  try {
    const response_api = await fetch('https://api.death2data.com/perspective', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        keyword: sanitizeHTML(keyword),
        perspective: sanitizeHTML(response) // Client-side sanitization (server must also sanitize!)
      })
    });

    if (!response_api.ok) {
      throw new Error('Server rejected submission');
    }

    // ... rest of function
  } catch (e) {
    btn.disabled = false;
    btn.textContent = 'Submit Anonymously';
    // SECURITY: Generic error message
    alert('Failed to save. Please try again later.');
    console.error('Submission error:', e); // Detailed error only in console
  }
}
```

**Add security.js include:**
```html
<script src="/js/security.js"></script>
```

---

### Fix 4: Update ALL innerHTML uses

**Files to update:** `revenue.html`, `admin.html`, `dashboard.html`, `notebook.html`, etc.

**Pattern to find and replace:**
```javascript
// UNSAFE:
element.innerHTML = userData;

// SAFE:
element.textContent = userData;

// OR if HTML structure is needed:
element.innerHTML = D2DSecurity.sanitizeHTML(userData);
```

**Script to help find all instances:**
```bash
cd /Users/matthewmauer/Desktop/deathtodata.github.io
grep -rn "innerHTML.*=" . --include="*.html" --include="*.js" > innerHTML_audit.txt
# Manually review each and fix
```

---

## Phase 2: Authentication Hardening (2-4 hours)

### Background: Why Client-Only Auth is Broken

Current system:
```
User creates token in localStorage → Client checks token → Access granted
```

Problem: Anyone can fake a token:
```javascript
localStorage.setItem('d2d_member', JSON.stringify({expires: Date.now() + 999999999}));
```

### Solution: Server-Side Token Validation

**New flow:**
```
1. User logs in → Server creates JWT → Returns to client
2. Client stores JWT in HttpOnly cookie (not localStorage)
3. Every API request → Client sends JWT → Server validates signature
4. Invalid/expired JWT → 401 Unauthorized → Redirect to login
```

### Implementation

#### Step 1: Backend API Changes (Pseudocode - Adapt to your backend)

**File:** Backend API (e.g., `d2d.py` or Cloudflare Worker)

```python
import jwt
import datetime
from functools import wraps

SECRET_KEY = os.getenv('JWT_SECRET')  # MUST be in environment, not code!

def create_token(email, tier, stripe_customer_id):
    """Create JWT token after successful Stripe payment"""
    payload = {
        'email': email,
        'tier': tier,
        'customer_id': stripe_customer_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=28),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token signature"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return {'valid': True, 'payload': payload}
    except jwt.ExpiredSignatureError:
        return {'valid': False, 'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'valid': False, 'error': 'Invalid token'}

def require_auth(f):
    """Decorator to protect API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('d2d_token')  # From HttpOnly cookie
        if not token:
            return jsonify({'error': 'Not authenticated'}), 401

        verification = verify_token(token)
        if not verification['valid']:
            return jsonify({'error': verification['error']}), 401

        # Add user info to request
        request.user = verification['payload']
        return f(*args, **kwargs)

    return decorated_function

# Example protected endpoint:
@app.route('/api/search')
@require_auth
def search():
    user = request.user  # From decorator
    query = request.args.get('q', '')

    # User is authenticated - proceed
    results = perform_search(query, user['tier'])
    return jsonify(results)

# Login endpoint (called after Stripe success):
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    stripe_customer_id = data.get('customer_id')

    # Verify with Stripe that this customer has active subscription
    customer = stripe.Customer.retrieve(stripe_customer_id)
    if not customer or not customer.subscriptions.data:
        return jsonify({'error': 'No active subscription'}), 403

    # Create JWT
    token = create_token(email, tier=1, stripe_customer_id=stripe_customer_id)

    # Set HttpOnly cookie
    response = jsonify({'success': True})
    response.set_cookie(
        'd2d_token',
        token,
        httponly=True,  # Prevent JavaScript access
        secure=True,    # HTTPS only
        samesite='Strict',  # Prevent CSRF
        max_age=28*24*60*60  # 28 days
    )
    return response
```

#### Step 2: Update Frontend Auth

**File:** `/js/auth.js` (complete rewrite)

```javascript
// ================================================================
// D2D AUTH - Server-Validated Tokens
// ================================================================
// Now checks with server instead of trusting localStorage
// ================================================================

(function() {
  const LOGIN_URL = '/';

  // Check authentication status with server
  async function checkAuth() {
    try {
      const response = await fetch('https://api.death2data.com/auth/check', {
        credentials: 'include'  // Send cookies
      });

      if (!response.ok) {
        // Not authenticated
        const reason = response.status === 401 ? 'expired' : 'error';
        window.location.href = LOGIN_URL + '?reason=' + reason;
        return;
      }

      const data = await response.json();

      // Make user data available globally
      window.D2D = {
        member: {
          email: data.email,
          tier: data.tier,
          expires: data.expires
        },
        daysLeft: Math.ceil((data.expires - Date.now()) / (24 * 60 * 60 * 1000)),
        isActive: true
      };

      // Add member bar when DOM ready
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addMemberBar);
      } else {
        addMemberBar();
      }

    } catch (e) {
      console.error('Auth check failed:', e);
      window.location.href = LOGIN_URL + '?reason=error';
    }
  }

  function addMemberBar() {
    if (document.getElementById('d2d-member-bar') || !window.D2D) return;

    const bar = document.createElement('div');
    bar.id = 'd2d-member-bar';
    bar.innerHTML = `
      <style>
        #d2d-member-bar {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          background: #111;
          border-top: 1px solid #222;
          padding: 8px 20px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-family: monospace;
          font-size: 12px;
          z-index: 9999;
        }
        #d2d-member-bar .left {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        #d2d-member-bar .dot {
          width: 8px;
          height: 8px;
          background: #00ff00;
          border-radius: 50%;
        }
        #d2d-member-bar .status {
          color: #888;
        }
        #d2d-member-bar .days {
          color: #00ff00;
        }
        #d2d-member-bar a {
          color: #666;
          text-decoration: none;
        }
        #d2d-member-bar a:hover {
          color: #888;
        }
      </style>
      <div class="left">
        <span class="dot"></span>
        <span class="status">D2D Member</span>
        <span class="days">${window.D2D.daysLeft} days left</span>
      </div>
      <div class="right">
        <a href="/tools.html">Tools</a>
        &nbsp;·&nbsp;
        <a href="/manage.html">Account</a>
        &nbsp;·&nbsp;
        <a href="#" onclick="D2D.logout(); return false;">Logout</a>
      </div>
    `;
    document.body.appendChild(bar);
    document.body.style.paddingBottom = '50px';
  }

  // Logout function
  window.D2D = window.D2D || {};
  window.D2D.logout = async function() {
    try {
      await fetch('https://api.death2data.com/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
    } catch (e) {
      console.error('Logout error:', e);
    }
    window.location.href = '/';
  };

  // Run auth check immediately
  checkAuth();
})();
```

#### Step 3: Add Backend Auth Check Endpoint

```python
@app.route('/auth/check')
def auth_check():
    """Return current user info if authenticated"""
    token = request.cookies.get('d2d_token')
    if not token:
        return jsonify({'error': 'Not authenticated'}), 401

    verification = verify_token(token)
    if not verification['valid']:
        return jsonify({'error': verification['error']}), 401

    payload = verification['payload']
    return jsonify({
        'email': payload['email'],
        'tier': payload['tier'],
        'expires': payload['exp'] * 1000  # Convert to milliseconds
    })

@app.route('/auth/logout', methods=['POST'])
def auth_logout():
    """Clear authentication cookie"""
    response = jsonify({'success': True})
    response.set_cookie('d2d_token', '', expires=0)
    return response
```

---

## Phase 3: Input Validation & Rate Limiting (1-2 hours)

### Server-Side Validation (Required!)

**All API endpoints must validate:**

```python
from bleach import clean  # pip install bleach

def sanitize_input(text, max_length=5000):
    """Sanitize user input"""
    if not text:
        raise ValueError("Input required")

    # Remove HTML tags
    text = clean(text, tags=[], strip=True)

    # Check length
    if len(text) > max_length:
        raise ValueError(f"Input too long (max {max_length} chars)")

    return text

@app.route('/perspective', methods=['POST'])
@require_auth  # Must be authenticated
def submit_perspective():
    data = request.json

    try:
        keyword = sanitize_input(data.get('keyword', ''), max_length=50)
        perspective = sanitize_input(data.get('perspective', ''), max_length=5000)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # Check rate limit (server-side)
    user_id = request.user['email']
    if not check_rate_limit(user_id, 'perspective', max_requests=10, window_seconds=3600):
        return jsonify({'error': 'Rate limit exceeded'}), 429

    # Save to database
    save_perspective(keyword, perspective, user_id)
    return jsonify({'success': True})
```

### Rate Limiting Implementation

```python
from datetime import datetime, timedelta
import redis

# Use Redis for rate limiting (or SQLite if no Redis)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def check_rate_limit(user_id, action, max_requests, window_seconds):
    """Check if user exceeded rate limit"""
    key = f"ratelimit:{user_id}:{action}"
    now = datetime.now()
    window_start = now - timedelta(seconds=window_seconds)

    # Remove old requests
    redis_client.zremrangebyscore(key, 0, window_start.timestamp())

    # Count requests in window
    request_count = redis_client.zcard(key)

    if request_count >= max_requests:
        return False

    # Add current request
    redis_client.zadd(key, {now.timestamp(): now.timestamp()})
    redis_client.expire(key, window_seconds)

    return True
```

---

## Phase 4: Additional Security Headers (30 minutes)

### Add Security Headers

**Option A: Via HTML Meta Tags** (if no server control)

Add to all HTML `<head>` sections:

```html
<!-- Content Security Policy -->
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self' https://js.stripe.com https://cdn.jsdelivr.net;
               style-src 'self' 'unsafe-inline';
               img-src 'self' data: https:;
               connect-src 'self' https://api.death2data.com;
               frame-src https://js.stripe.com;">

<!-- Prevent clickjacking -->
<meta http-equiv="X-Frame-Options" content="DENY">

<!-- Force HTTPS -->
<script>
  if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
    location.replace('https:' + window.location.href.substring(window.location.protocol.length));
  }
</script>
```

**Option B: Via Server/CDN** (recommended)

If using Cloudflare, add Page Rules or use Workers:

```javascript
// Cloudflare Worker example
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const response = await fetch(request)
  const newResponse = new Response(response.body, response)

  // Add security headers
  newResponse.headers.set('X-Frame-Options', 'DENY')
  newResponse.headers.set('X-Content-Type-Options', 'nosniff')
  newResponse.headers.set('Referrer-Policy', 'no-referrer')
  newResponse.headers.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
  newResponse.headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')

  // CSP header
  newResponse.headers.set('Content-Security-Policy',
    "default-src 'self'; " +
    "script-src 'self' https://js.stripe.com; " +
    "style-src 'self' 'unsafe-inline'; " +
    "img-src 'self' data: https:; " +
    "connect-src 'self' https://api.death2data.com;"
  )

  return newResponse
}
```

---

## Phase 5: Testing (1-2 hours)

### Manual Security Tests

**Test 1: XSS Prevention**
```javascript
// Try submitting this in perspective form:
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>

// Expected: Text should be escaped, no alert shown
```

**Test 2: Authentication Bypass**
```javascript
// In browser console, try to fake authentication:
localStorage.setItem('d2d_member', JSON.stringify({expires: 9999999999999}));
// Refresh page
// Expected: Should still redirect to login (server validates, not client)
```

**Test 3: Rate Limiting**
```bash
# Submit 11 perspectives in 1 minute:
for i in {1..11}; do
  curl -X POST https://api.death2data.com/perspective \
    -H "Content-Type: application/json" \
    -d '{"keyword":"test","perspective":"test"}' \
    --cookie "d2d_token=YOUR_TOKEN"
done
# Expected: 11th request should return 429 Too Many Requests
```

**Test 4: SSRF Prevention**
```javascript
// Try browsing internal URLs:
// In browse.html, enter:
http://localhost:6379
http://169.254.169.254/latest/meta-data/
// Expected: Error "Internal URLs not allowed"
```

**Test 5: IDOR Prevention**
```bash
# Try accessing another user's data:
curl https://api.death2data.com/api/note/1 \
  --cookie "d2d_token=YOUR_TOKEN"
# Expected: 404 or 403 if note doesn't belong to you
```

### Automated Security Scanning

```bash
# Run OWASP ZAP
docker run -v $(pwd):/zap/wrk:rw -t owasp/zap2docker-stable zap-baseline.py \
  -t https://death2data.com \
  -r zap-report.html

# Check for secrets in git
cd /Users/matthewmauer/Desktop/deathtodata.github.io
git secrets --scan

# Check dependencies (if using npm)
npm audit --audit-level=moderate
```

---

## Deployment Checklist

Before deploying to production:

- [ ] All XSS vulnerabilities fixed (innerHTML replaced)
- [ ] Server-side authentication implemented
- [ ] JWT tokens used instead of localStorage
- [ ] HttpOnly cookies configured
- [ ] Input validation on all API endpoints
- [ ] Rate limiting implemented
- [ ] SSRF protection in URL fetching
- [ ] Security headers added (CSP, X-Frame-Options, etc.)
- [ ] HTTPS enforced (no HTTP access)
- [ ] All secrets in environment variables (not code)
- [ ] Error messages generic (no stack traces to users)
- [ ] Monitoring/alerting set up
- [ ] Security tests passing
- [ ] OWASP ZAP scan shows no critical issues
- [ ] Penetration test completed (if possible)

---

## Monitoring & Alerting

After deployment, monitor for:

1. **Failed authentication attempts** (potential brute force)
2. **Rate limit hits** (potential abuse)
3. **Unusual traffic patterns** (potential DDoS)
4. **Error rate spikes** (potential attacks or bugs)
5. **Suspicious user agents** (potential bots)

Set up alerts:
```python
# Example: Alert on 10+ failed logins in 1 minute
if failed_logins_last_minute > 10:
    send_alert("Potential brute force attack", user_id)

# Example: Alert on rate limit violations
if rate_limit_violations_last_hour > 50:
    send_alert("High rate limit violations", None)
```

---

**Next:** Start with Phase 1 (XSS fixes), then move to Phase 2 (authentication). Don't skip to later phases without completing earlier ones - they build on each other!
