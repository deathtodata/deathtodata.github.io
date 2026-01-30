// D2D Identity System - ONE source of truth
const D2D = {
    STORAGE_KEY: 'd2d_identity',
    
    getIdentity() {
        const data = localStorage.getItem(this.STORAGE_KEY);
        return data ? JSON.parse(data) : null;
    },
    
    createIdentity() {
        const words = ['GHOST','VOID','NULL','ZERO','DARK','FLUX','WAVE','BOLT','CORE','NODE'];
        const w1 = words[Math.floor(Math.random() * words.length)];
        const w2 = words[Math.floor(Math.random() * words.length)];
        const num = Math.floor(Math.random() * 9000) + 1000;
        
        const identity = {
            anonName: `${w1}-${w2}-${num}`,
            publicKey: crypto.randomUUID().replace(/-/g, '') + crypto.randomUUID().replace(/-/g, ''),
            created: Date.now()
        };
        
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(identity));
        return identity;
    },
    
    getOrCreate() {
        return this.getIdentity() || this.createIdentity();
    },
    
    hasIdentity() {
        return !!this.getIdentity();
    }
};

// Make available globally
window.D2D = D2D;
