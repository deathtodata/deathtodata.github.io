// member-gate.js
// Add this to any page you want to protect:
// <script src="/js/member-gate.js" defer></script>

(function() {
  function checkAuth() {
    // Primary: localStorage (set by index.html login)
    const token = localStorage.getItem('d2d_token');
    const email = localStorage.getItem('d2d_email');

    if (token && email) {
      document.body.style.visibility = 'visible';
      const el = document.getElementById('member-status');
      if (el) el.innerHTML = `${email} &middot; <a href="/">Back to Search</a>`;
      return;
    }

    // Legacy: old localStorage format
    const legacyMember = JSON.parse(localStorage.getItem('d2d_member') || 'null');
    if (legacyMember && legacyMember.expires && legacyMember.expires > Date.now()) {
      document.body.style.visibility = 'visible';
      const el = document.getElementById('member-status');
      if (el) {
        const days = Math.ceil((legacyMember.expires - Date.now()) / (24*60*60*1000));
        el.innerHTML = `${legacyMember.email} &middot; ${days} days left &middot; <a href="/manage.html">Manage</a>`;
      }
      return;
    }

    // Not logged in — redirect to home
    window.location.href = '/?reason=not_member';
  }

  // Wait for DOM if body isn't ready yet
  if (document.body) {
    checkAuth();
  } else {
    document.addEventListener('DOMContentLoaded', checkAuth);
  }
})();
