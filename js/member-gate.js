// member-gate.js
// Add this to any page you want to protect:
// <script src="/js/member-gate.js"></script>

(function() {
  const member = JSON.parse(localStorage.getItem('d2d_member') || 'null');
  
  // No member data? Redirect to signup
  if (!member || !member.expires) {
    window.location.href = '/?reason=not_member';
    return;
  }
  
  // Expired? Redirect to renew
  if (member.expires < Date.now()) {
    window.location.href = '/?reason=expired';
    return;
  }
  
  // Valid member - show the page
  document.body.style.visibility = 'visible';
  
  // Optional: show member info
  const el = document.getElementById('member-status');
  if (el) {
    const days = Math.ceil((member.expires - Date.now()) / (24*60*60*1000));
    el.innerHTML = `${member.email} · ${days} days left · <a href="/manage.html">Manage</a>`;
  }
})();
