// Death2Data Environment Configuration
// Auto-detects environment and provides correct settings
//
// IMPORTANT: Stripe keys are loaded from environment variables.
// Set these in your build system (Cloudflare Pages) or locally:
//   window.ENV_STRIPE_PUBLISHABLE_KEY = 'pk_live_...'
//   window.ENV_STRIPE_PRICE_ID = 'price_...'
//
// See .env.example for template and js/env.js for loader

const D2D_CONFIG = {
  // Development (localhost)
  dev: {
    env: 'development',
    apiUrl: 'http://localhost:8787',
    siteUrl: 'http://localhost:3000',
    stripe: {
      publishableKey: 'pk_test_YOUR_KEY_HERE',
      priceIds: {
        monthly: 'price_test_...'
      }
    },
    features: {
      debugMode: true,
      mockPayments: true
    }
  },

  // Staging (staging.death2data.com or GitHub staging branch)
  staging: {
    env: 'staging',
    apiUrl: 'https://fortune0-com.onrender.com',
    siteUrl: 'https://staging.death2data.com',
    stripe: {
      publishableKey: window.ENV_STRIPE_PUBLISHABLE_KEY || '',
      priceIds: {
        monthly: window.ENV_STRIPE_PRICE_ID || 'price_1SuZaSG7fHl88NQ80GLFU5Q9' // $1 every 28 days
      },
      hostedLink: 'https://buy.stripe.com/cNieVd5Vjb6N2ZY6Fq4wM00'
    },
    features: {
      debugMode: true,
      mockPayments: false
    }
  },

  // Production (death2data.com)
  prod: {
    env: 'production',
    apiUrl: 'https://fortune0-com.onrender.com',
    siteUrl: 'https://death2data.com',
    stripe: {
      publishableKey: window.ENV_STRIPE_PUBLISHABLE_KEY || '',
      priceIds: {
        monthly: window.ENV_STRIPE_PRICE_ID || 'price_1SuZaSG7fHl88NQ80GLFU5Q9' // $1 every 28 days
      },
      hostedLink: 'https://buy.stripe.com/cNieVd5Vjb6N2ZY6Fq4wM00'
    },
    features: {
      debugMode: false,
      mockPayments: false
    }
  }
};

// Auto-detect environment based on hostname
function getEnvironment() {
  const hostname = window.location.hostname;

  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'dev';
  } else if (hostname.includes('staging')) {
    return 'staging';
  } else {
    return 'prod';
  }
}

// Export active configuration
const config = D2D_CONFIG[getEnvironment()];

// Debug logging (only in dev/staging)
if (config.features.debugMode) {
  console.log('🔧 D2D Environment:', config.env);
  console.log('🌐 API URL:', config.apiUrl);
  console.log('💳 Stripe Mode:', config.stripe.publishableKey.includes('test') ? 'TEST' : 'LIVE');
}

// Make config globally available
window.D2D = { config };
