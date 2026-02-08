/**
 * Environment variable loader for Death2Data
 *
 * This file provides safe access to environment variables.
 * In production (Cloudflare Pages), these are injected as environment variables.
 * In development, they should be loaded from .env file (not committed to git).
 *
 * Never commit actual API keys to this file.
 */

const ENV = {
  // Stripe Configuration
  // In production, this will be injected by the build system
  STRIPE_PUBLISHABLE_KEY: typeof process !== 'undefined' && process.env?.STRIPE_PUBLISHABLE_KEY
    ? process.env.STRIPE_PUBLISHABLE_KEY
    : window.ENV_STRIPE_PUBLISHABLE_KEY || '',

  // API Configuration
  D2D_API_URL: typeof process !== 'undefined' && process.env?.D2D_API_URL
    ? process.env.D2D_API_URL
    : window.ENV_D2D_API_URL || 'https://d2d-api.mattmauersp.workers.dev',

  // Environment type
  ENVIRONMENT: typeof process !== 'undefined' && process.env?.NODE_ENV
    ? process.env.NODE_ENV
    : window.ENV_NODE_ENV || 'production',

  /**
   * Check if we're running in development mode
   */
  isDevelopment() {
    return this.ENVIRONMENT === 'development';
  },

  /**
   * Check if we're running in production mode
   */
  isProduction() {
    return this.ENVIRONMENT === 'production';
  },

  /**
   * Validate that all required environment variables are set
   * @throws {Error} If required variables are missing
   */
  validate() {
    const required = ['STRIPE_PUBLISHABLE_KEY', 'D2D_API_URL'];
    const missing = required.filter(key => !this[key]);

    if (missing.length > 0) {
      throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }
  }
};

// Make ENV available globally
if (typeof window !== 'undefined') {
  window.D2D_ENV = ENV;
}

// For Node.js environments (build tools, tests)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ENV;
}
