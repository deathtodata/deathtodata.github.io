// ================================================================
// D2D OLLAMA INTEGRATION
// ================================================================
// Usage:
//   <script src="/js/ollama.js"></script>
//   
//   const ollama = new D2DOllama();
//   const available = await ollama.check();
//   const response = await ollama.generate("Hello!");
// ================================================================

class D2DOllama {
  constructor(baseUrl = 'http://localhost:11434') {
    this.baseUrl = baseUrl;
    this.defaultModel = 'llama3.2';
    this.available = null;
    this.models = [];
  }

  // ----------------------------------------------------------------
  // Check if Ollama is running
  // ----------------------------------------------------------------
  async check() {
    try {
      const response = await fetch(`${this.baseUrl}/api/tags`, {
        method: 'GET',
        signal: AbortSignal.timeout(3000) // 3 second timeout
      });
      
      if (!response.ok) {
        this.available = false;
        return false;
      }
      
      const data = await response.json();
      this.models = data.models || [];
      this.available = true;
      
      // Set default model if available
      if (this.models.length > 0) {
        // Prefer llama3.2, fall back to first available
        const preferred = this.models.find(m => m.name.includes('llama3.2'));
        this.defaultModel = preferred ? preferred.name : this.models[0].name;
      }
      
      return true;
    } catch (error) {
      this.available = false;
      this.models = [];
      return false;
    }
  }

  // ----------------------------------------------------------------
  // Generate text (non-streaming)
  // ----------------------------------------------------------------
  async generate(prompt, options = {}) {
    if (this.available === null) {
      await this.check();
    }
    
    if (!this.available) {
      throw new Error('Ollama is not available. Please install and run Ollama.');
    }
    
    const model = options.model || this.defaultModel;
    const systemPrompt = options.system || '';
    
    try {
      const response = await fetch(`${this.baseUrl}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: model,
          prompt: prompt,
          system: systemPrompt,
          stream: false,
          options: {
            temperature: options.temperature || 0.7,
            num_predict: options.maxTokens || 500
          }
        })
      });
      
      if (!response.ok) {
        throw new Error(`Ollama error: ${response.status}`);
      }
      
      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Ollama generate error:', error);
      throw error;
    }
  }

  // ----------------------------------------------------------------
  // Generate text (streaming)
  // ----------------------------------------------------------------
  async *generateStream(prompt, options = {}) {
    if (this.available === null) {
      await this.check();
    }
    
    if (!this.available) {
      throw new Error('Ollama is not available');
    }
    
    const model = options.model || this.defaultModel;
    const systemPrompt = options.system || '';
    
    const response = await fetch(`${this.baseUrl}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: model,
        prompt: prompt,
        system: systemPrompt,
        stream: true,
        options: {
          temperature: options.temperature || 0.7,
          num_predict: options.maxTokens || 500
        }
      })
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter(line => line.trim());
      
      for (const line of lines) {
        try {
          const data = JSON.parse(line);
          if (data.response) {
            yield data.response;
          }
        } catch (e) {
          // Skip invalid JSON
        }
      }
    }
  }

  // ----------------------------------------------------------------
  // Chat format (for multi-turn conversations)
  // ----------------------------------------------------------------
  async chat(messages, options = {}) {
    if (this.available === null) {
      await this.check();
    }
    
    if (!this.available) {
      throw new Error('Ollama is not available');
    }
    
    const model = options.model || this.defaultModel;
    
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: model,
        messages: messages,
        stream: false,
        options: {
          temperature: options.temperature || 0.7,
          num_predict: options.maxTokens || 500
        }
      })
    });
    
    if (!response.ok) {
      throw new Error(`Ollama chat error: ${response.status}`);
    }
    
    const data = await response.json();
    return data.message.content;
  }

  // ----------------------------------------------------------------
  // Get embeddings
  // ----------------------------------------------------------------
  async embed(text, model = 'nomic-embed-text') {
    if (this.available === null) {
      await this.check();
    }
    
    if (!this.available) {
      throw new Error('Ollama is not available');
    }
    
    const response = await fetch(`${this.baseUrl}/api/embeddings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: model,
        prompt: text
      })
    });
    
    if (!response.ok) {
      throw new Error(`Ollama embed error: ${response.status}`);
    }
    
    const data = await response.json();
    return data.embedding;
  }

  // ----------------------------------------------------------------
  // Get available models
  // ----------------------------------------------------------------
  getModels() {
    return this.models.map(m => ({
      name: m.name,
      size: this.formatBytes(m.size),
      family: m.details?.family || 'unknown'
    }));
  }

  // ----------------------------------------------------------------
  // Helper: Format bytes
  // ----------------------------------------------------------------
  formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
  }
}

// ----------------------------------------------------------------
// UI Helper: Show Ollama status
// ----------------------------------------------------------------
async function showOllamaStatus(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  const ollama = new D2DOllama();
  const available = await ollama.check();
  
  if (available) {
    container.innerHTML = `
      <div style="color: #00ff00; font-size: 12px;">
        ● Ollama connected (${ollama.models.length} models)
      </div>
    `;
  } else {
    container.innerHTML = `
      <div style="color: #888; font-size: 12px;">
        ○ Ollama not running
        <a href="https://ollama.ai" target="_blank" style="color: #666; margin-left: 8px;">Install</a>
      </div>
    `;
  }
}

// Make globally available
window.D2DOllama = D2DOllama;
window.showOllamaStatus = showOllamaStatus;
