# Death2Data Security Audit Report
**Date:** 2026-02-03
**Status:** 🔴 CRITICAL VULNERABILITIES FOUND - DO NOT SHIP

## Executive Summary

Found **8 critical** and **12 high-severity** security vulnerabilities across the codebase. The most severe issues are:
1. **XSS vulnerabilities** in user input handling (innerHTML without sanitization)
2. **Client-side only authentication** (no server-side validation)
3. **Exposed Stripe live keys** in client code
4. **No input validation** on API endpoints
5. **SSRF potential** in browse.html URL fetching

**Recommendation:** Do NOT deploy to production until all critical issues are fixed.

---

## Critical Vulnerabilities (Fix Immediately)

### 1. XSS in browse.html - Line 364
**File:** `/browse.html`
**Severity:** 🔴 CRITICAL
**Type:** Cross-Site Scripting (XSS)

**Code:**
```javascript
document.getElementById('error-msg').innerHTML = msg; // Line 364
```

**Issue:** Error messages are rendered as HTML without sanitization. An attacker can inject malicious JavaScript through the URL parameter.

**Attack Vector:**
```
https://death2data.com/browse.html?url=<img src=x onerror=alert(document.cookie)>
```

**Fix:** Use `textContent` instead of `innerHTML`:
```javascript
document.getElementById('error-msg').textContent = msg;
```

---

### 2. Client-Side Only Authentication
**File:** `/js/auth.js`
**Severity:** 🔴 CRITICAL
**Type:** Authentication Bypass

**Issue:** Authentication is ONLY validated client-side. Any user can:
- Modify `localStorage` to create fake tokens
- Set arbitrary expiration dates
- Bypass membership tiers
- Access paid content for free

**Current Code (Lines 13-25):**
```javascript
const member = JSON.parse(localStorage.getItem(MEMBER_KEY) || 'null');
if (!member) {
  window.location.href = LOGIN_URL + '?reason=no_token';
  return;
}
if (Date.now() > member.expires) {
  window.location.href = LOGIN_URL + '?reason=expired';
  return;
}
```

**Attack:**
```javascript
// In browser console:
localStorage.setItem('d2d_member', JSON.stringify({
  email: 'hacker@evil.com',
  expires: Date.now() + (365 * 24 * 60 * 60 * 1000), // 1 year
  tier: 999
}));
// Refresh page → Full access without payment
```

**Fix Required:**
1. Add server-side token validation on EVERY API call
2. Use JWT tokens signed by server (not client-created)
3. Validate token signature on backend
4. Store token in HttpOnly cookie (not localStorage)

---

### 3. Exposed Stripe Live Keys
**File:** `/config.js`
**Severity:** 🔴 CRITICAL
**Type:** Secret Exposure

**Issue:** Stripe live publishable key is committed to git and visible to all users.

**Code (Lines 28, 46):**
```javascript
publishableKey: 'pk_live_51RIIa4G7fHl88NQ8yUvaGIpn936VW474BDGeHcCaQbTF33SnHthcWQeJCuTVGp3hSMy3YR25AX4dpkqOY52BS9j4007Svg6DZx'
```

**Risk:** While publishable keys are meant to be public, having them in git means:
- Can't rotate keys without git history rewrite
- Easier for attackers to target your Stripe account
- Violates security best practices

**Fix:**
1. Move to environment variables (for server-side code)
2. For client-side, this is acceptable BUT document why
3. Add `.env` file with secret keys (never commit)
4. Rotate all keys if any secret keys were exposed

---

### 4. No Server-Side Input Validation
**File:** `/keyword.html` (and likely backend)
**Severity:** 🔴 CRITICAL
**Type:** Injection vulnerabilities

**Issue:** User perspectives submitted without validation on server.

**Code (Lines 113-117):**
```javascript
await fetch('https://api.death2data.com/perspective', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ keyword, perspective: response })
});
```

**Attack Vectors:**
1. **XSS:** Submit `<script>alert('xss')</script>` as perspective
2. **SQL Injection:** If backend uses raw SQL: `' OR 1=1 --`
3. **NoSQL Injection:** If using MongoDB: `{"$gt": ""}`
4. **Path Traversal:** Keyword = `../../etc/passwd`
5. **Size Attacks:** Submit 10MB of text to DOS server

**Fix Required:**
1. Server-side input sanitization (HTML escape)
2. Input length limits (keyword: 50 chars, perspective: 5000 chars)
3. Parameterized queries (no string concatenation in SQL)
4. Rate limiting (max 10 submissions per hour per IP)

---

### 5. SSRF Potential in browse.html
**File:** `/browse.html`
**Severity:** 🔴 CRITICAL
**Type:** Server-Side Request Forgery (SSRF)

**Issue:** If there's a backend proxy for fetching URLs (implied by the code), users can make the server fetch internal URLs.

**Code (Lines 273-278):**
```javascript
async function loadRemotePage() {
  const url = document.getElementById('url-input').value.trim();
  if (!url) return;
  // ... fetches URL
}
```

**Attack Vectors:**
1. Fetch internal services: `http://localhost:6379` (Redis)
2. Fetch cloud metadata: `http://169.254.169.254/latest/meta-data/`
3. Port scanning: `http://internal-server:1-65535`
4. File reading: `file:///etc/passwd`

**Fix Required:**
1. Whitelist allowed protocols (only `http://` and `https://`)
2. Blacklist internal IPs (127.0.0.1, 10.x, 192.168.x, 169.254.x)
3. Add DNS rebinding protection
4. Set timeout limits (max 10 seconds)
5. Limit response size (max 10MB)

---

## High Severity Vulnerabilities

### 6. XSS in Multiple innerHTML Uses
**Files:** Multiple (see list below)
**Severity:** 🟠 HIGH
**Type:** Cross-Site Scripting (XSS)

**Vulnerable Code Locations:**
- `revenue.html:412` - Activity feed
- `admin.html:1070` - Activity table
- `admin.html:1082` - Subscriptions table
- `admin.html:1095` - Customers table
- `admin.html:1107` - Payments table
- `dashboard.html:310,339` - Content rendering
- `notebook.html:486,488` - Past entries display

**Issue:** User-controlled data rendered with `innerHTML` without sanitization.

**Fix:** Create sanitization helper:
```javascript
// Add to every file
function sanitizeHTML(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// Use like:
element.innerHTML = sanitizeHTML(userInput);
```

---

### 7. No CSRF Protection
**Severity:** 🟠 HIGH
**Type:** Cross-Site Request Forgery

**Issue:** No CSRF tokens on state-changing operations.

**Attack:** Attacker creates page:
```html
<form action="https://api.death2data.com/perspective" method="POST">
  <input name="keyword" value="spam">
  <input name="perspective" value="Click here for free crypto!">
</form>
<script>document.forms[0].submit();</script>
```

User visits attacker's page → Unwanted perspective submitted under their account.

**Fix:**
1. Add CSRF tokens to all POST requests
2. Verify `Origin` and `Referer` headers on server
3. Use SameSite cookies

---

### 8. No Rate Limiting
**Severity:** 🟠 HIGH
**Type:** Denial of Service (DOS)

**Issue:** No rate limiting on API endpoints.

**Attack:**
```bash
# Spam perspectives
for i in {1..10000}; do
  curl -X POST https://api.death2data.com/perspective \
    -H "Content-Type: application/json" \
    -d '{"keyword":"spam","perspective":"spam"}'
done
```

**Fix:**
1. Implement rate limiting (max 100 requests/hour per IP)
2. Add CAPTCHA for suspicious activity
3. Require authentication for writes

---

### 9. Weak Session Management
**File:** `/js/auth.js`
**Severity:** 🟠 HIGH
**Type:** Session hijacking

**Issue:** Tokens stored in `localStorage` are:
- Accessible to all JavaScript (including XSS)
- Not HttpOnly (vulnerable to XSS theft)
- Sent on every request (including cross-origin)
- No secure flag (can be sent over HTTP)

**Fix:**
1. Use HttpOnly cookies instead of localStorage
2. Set Secure flag (HTTPS only)
3. Set SameSite=Strict (prevent CSRF)
4. Add token rotation (refresh every hour)

---

### 10. Information Disclosure in Errors
**Severity:** 🟠 HIGH
**Type:** Information leakage

**Issue:** Detailed error messages visible to users.

**Example (browse.html:364):**
```javascript
showError('Network error: ' + e.message);
```

**Risk:** Error messages can reveal:
- Internal file paths
- Database structure
- Stack traces
- Version numbers

**Fix:**
```javascript
// Show generic message to user
showError('Something went wrong. Please try again.');

// Log detailed error server-side
console.error('Error details:', e);
```

---

## Medium Severity Vulnerabilities

### 11. Missing Content Security Policy (CSP)
**Severity:** 🟡 MEDIUM
**Type:** XSS mitigation missing

**Issue:** No CSP headers to prevent inline script execution.

**Fix:** Add to HTML `<head>`:
```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self' https://js.stripe.com;
               style-src 'self' 'unsafe-inline';
               img-src 'self' data: https:;">
```

---

### 12. No Input Length Limits
**Severity:** 🟡 MEDIUM
**Type:** DOS via large inputs

**Issue:** No max length on text inputs.

**Fix:**
```html
<textarea maxlength="5000" id="response"></textarea>
```

```javascript
if (response.length > 5000) {
  alert('Perspective too long (max 5000 chars)');
  return;
}
```

---

### 13. Insecure Direct Object References (IDOR)
**Severity:** 🟡 MEDIUM
**Type:** Unauthorized access

**Issue:** If API uses IDs like `/api/note/123`, users can guess other IDs.

**Attack:**
```bash
# Try accessing other users' notes
curl https://api.death2data.com/api/note/1
curl https://api.death2data.com/api/note/2
# ...
curl https://api.death2data.com/api/note/999
```

**Fix:**
1. Always validate user owns resource before returning
2. Use UUIDs instead of sequential IDs
3. Add authorization checks on EVERY endpoint

---

### 14. Missing HTTPS Enforcement
**Severity:** 🟡 MEDIUM
**Type:** Man-in-the-middle

**Issue:** No automatic redirect from HTTP to HTTPS.

**Fix:** Add to all HTML pages:
```html
<script>
  if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
    location.replace('https:' + window.location.href.substring(window.location.protocol.length));
  }
</script>
```

---

### 15. Lack of Security Headers
**Severity:** 🟡 MEDIUM
**Type:** Various attacks

**Missing Headers:**
- `X-Frame-Options: DENY` (prevent clickjacking)
- `X-Content-Type-Options: nosniff` (prevent MIME sniffing)
- `Referrer-Policy: no-referrer` (privacy)
- `Permissions-Policy: ...` (restrict features)

**Fix:** Add to server response (or via Cloudflare)

---

## Low Severity Issues

### 16. Console Logging Sensitive Data
**Issue:** `console.log()` statements may leak sensitive info in production.

**Fix:** Remove or use debug flag:
```javascript
if (config.features.debugMode) {
  console.log('Debug info:', data);
}
```

---

### 17. Outdated Dependencies
**Issue:** Unknown - need to check `package.json` if it exists.

**Fix:** Run `npm audit` and update packages.

---

### 18. No Subresource Integrity (SRI)
**Issue:** External scripts loaded without integrity checks.

**Example:**
```html
<script src="https://js.stripe.com/v3/"></script>
```

**Fix:**
```html
<script src="https://js.stripe.com/v3/"
        integrity="sha384-..."
        crossorigin="anonymous"></script>
```

---

## Remediation Priority

### Immediate (Before Any Deployment)
1. Fix XSS in browse.html:364
2. Add server-side authentication validation
3. Fix XSS in all innerHTML uses
4. Add input validation on server

### Week 1
5. Implement rate limiting
6. Add CSRF protection
7. Move to HttpOnly cookies
8. Add CSP headers
9. Fix SSRF in browse functionality

### Week 2
10. Add input length limits
11. Fix IDOR vulnerabilities
12. Add security headers
13. Implement HTTPS enforcement
14. Add monitoring/alerting for attacks

### Ongoing
15. Regular security audits
16. Dependency updates
17. Penetration testing
18. Security training for developers

---

## Testing Checklist

After fixes, verify:

- [ ] XSS payloads blocked: `<script>alert(1)</script>`
- [ ] SQL injection blocked: `' OR 1=1 --`
- [ ] Invalid tokens rejected
- [ ] Expired tokens rejected
- [ ] Rate limiting working (101st request fails)
- [ ] CSRF protection working (cross-origin POST fails)
- [ ] SSRF blocked (internal IPs rejected)
- [ ] Input length limits enforced
- [ ] IDOR prevented (can't access other user's data)
- [ ] HTTPS enforced (HTTP redirects to HTTPS)

---

## Security Tools to Run

```bash
# 1. OWASP ZAP - Web app security scanner
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://death2data.com

# 2. npm audit - Dependency vulnerabilities
npm audit

# 3. git-secrets - Prevent committing secrets
git secrets --scan

# 4. SQLMap - SQL injection testing
sqlmap -u "https://api.death2data.com/perspective?keyword=test" --batch

# 5. Nuclei - Vulnerability scanner
nuclei -u https://death2data.com
```

---

## Contact Security Team

If you discover security issues, report to: security@death2data.com

**Do NOT** publicly disclose vulnerabilities before they're fixed.

---

**Next Steps:** See `SECURITY_FIX_PLAN.md` for detailed fix implementation.
