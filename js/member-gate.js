// member-gate.js
// Add this to any page you want to protect:
// <script src="/js/member-gate.js"></script>

(function() {
  // Check all possible auth sources (index.html uses sessionStorage, legacy uses localStorage)
  const token = sessionStorage.getItem('d2d_token');
  const email = sessionStorage.getItem('d2d_email');
  const legacyMember = JSON.parse(localStorage.getItem('d2d_member') || 'null');

  // Logged in via search page (primary auth)
  if (token && email) {
    document.body.style.visibility = 'visible';
    const el = document.getElementById('member-status');
    if (el) el.innerHTML = `${email} · <a href="/">Back to Search</a>`;
    return;
  }

  // Legacy auth (localStorage)
  if (legacyMember && legacyMember.expires && legacyMember.expires > Date.now()) {
    document.body.style.visibility = 'visible';
    const el = document.getElementById('member-status');
    if (el) {
      const days = Math.ceil((legacyMember.expires - Date.now()) / (24*60*60*1000));
      el.innerHTML = `${legacyMember.email} · ${days} days left · <a href="/manage.html">Manage</a>`;
    }
    return;
  }

  // Not logged in — redirect to home
  window.location.href = '/?reason=not_member';
})();
