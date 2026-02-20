// ================================================================
// D2D AUTH - Include this on EVERY protected page
// ================================================================
// Usage: <script src="/js/auth.js"></script>
//        Put this in the <head> BEFORE anything else
// ================================================================

(function() {
  const MEMBER_KEY = 'd2d_member';
  const LOGIN_URL = '/';
  
  // Check for token
  const member = JSON.parse(localStorage.getItem(MEMBER_KEY) || 'null');
  
  // No token = not logged in
  if (!member) {
    window.location.href = LOGIN_URL + '?reason=no_token';
    return;
  }
  
  // Token expired
  if (Date.now() > member.expires) {
    window.location.href = LOGIN_URL + '?reason=expired';
    return;
  }
  
  // Calculate days left
  const daysLeft = Math.ceil((member.expires - Date.now()) / (24 * 60 * 60 * 1000));
  
  // Make member data available globally
  window.D2D = {
    member: member,
    daysLeft: daysLeft,
    isActive: true
  };
  
  // Add member bar to page when DOM is ready
  document.addEventListener('DOMContentLoaded', function() {
    // Only add if there isn't already one
    if (!document.getElementById('d2d-member-bar')) {
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
            background: #00cc44;
            border-radius: 50%;
          }
          #d2d-member-bar .status {
            color: #888;
          }
          #d2d-member-bar .days {
            color: #00cc44;
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
          <span class="days">${daysLeft} days left</span>
        </div>
        <div class="right">
          <a href="/tools.html">Tools</a>
          &nbsp;·&nbsp;
          <a href="/manage.html">Account</a>
        </div>
      `;
      document.body.appendChild(bar);
      
      // Add padding to body so content isn't hidden behind bar
      document.body.style.paddingBottom = '50px';
    }
  });
})();
