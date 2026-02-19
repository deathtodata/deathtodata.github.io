/**
 * ollama-tools.js — Document analysis tool chain for IPOMyAgent notary
 *
 * Wraps D2DOllama (ollama.js) with 4 sequential tool functions:
 *   1. parseDocument(text)    → { parties, dates, doc_type, word_count }
 *   2. suggestTags(parsed)    → string[]
 *   3. extractClauses(text)   → [{ clause, risk }]
 *   4. summarize(text)        → string
 *
 * Usage:
 *   const tools = new OllamaTools();
 *   if (await tools.isAvailable()) {
 *     const result = await tools.analyze(text);
 *   }
 */

class OllamaTools {
    constructor(baseUrl = 'http://localhost:11434') {
        // D2DOllama must be loaded first (ollama.js)
        this.ollama = new D2DOllama(baseUrl);
        this.model = 'llama3.2';
    }

    async isAvailable() {
        return await this.ollama.check();
    }

    /**
     * Step 1: Parse document structure.
     * Returns { parties, dates, doc_type, word_count }
     */
    async parseDocument(text) {
        const truncated = text.slice(0, 3000);
        const word_count = text.trim().split(/\s+/).length;

        const prompt = `Analyze this document excerpt and respond with ONLY valid JSON (no markdown, no explanation):
{
  "parties": ["name1", "name2"],
  "dates": ["YYYY-MM-DD"],
  "doc_type": "Contract|Lease|NDA|Invoice|Agreement|Letter|Other"
}

Document:
${truncated}`;

        try {
            const raw = await this.ollama.generate(prompt, {
                model: this.model,
                system: 'You are a document parser. Respond with only valid JSON.',
                temperature: 0.1,
                maxTokens: 200,
            });
            const json = this._extractJSON(raw);
            return { ...json, word_count };
        } catch (e) {
            return { parties: [], dates: [], doc_type: 'Unknown', word_count };
        }
    }

    /**
     * Step 2: Suggest tags based on parsed metadata.
     * Returns string[] of 3–8 tags.
     */
    async suggestTags(parsed) {
        const prompt = `Given this document metadata, suggest 3 to 8 short tags.
Respond with ONLY a JSON array of strings, no explanation.

Metadata: ${JSON.stringify(parsed)}

Example response: ["Real Estate", "Lease", "Residential", "2026"]`;

        try {
            const raw = await this.ollama.generate(prompt, {
                model: this.model,
                system: 'You are a document tagger. Respond with only a JSON array of strings.',
                temperature: 0.2,
                maxTokens: 100,
            });
            const arr = this._extractJSON(raw);
            if (Array.isArray(arr)) return arr.slice(0, 8).map(t => String(t).slice(0, 50));
            return [];
        } catch (e) {
            return [];
        }
    }

    /**
     * Step 3: Extract key clauses and flag risk level.
     * Returns [{ clause: string, risk: 'low'|'medium'|'high' }]
     */
    async extractClauses(text) {
        const truncated = text.slice(0, 4000);

        const prompt = `Extract the 3 most important clauses from this document.
Respond with ONLY valid JSON array, no explanation:
[
  { "clause": "short description of clause", "risk": "low" },
  { "clause": "another clause", "risk": "medium" },
  { "clause": "risky clause", "risk": "high" }
]

Risk levels: low = standard/routine, medium = notable, high = unusual/restrictive

Document:
${truncated}`;

        try {
            const raw = await this.ollama.generate(prompt, {
                model: this.model,
                system: 'You are a legal document analyst. Respond with only valid JSON.',
                temperature: 0.2,
                maxTokens: 400,
            });
            const arr = this._extractJSON(raw);
            if (Array.isArray(arr)) {
                return arr.slice(0, 5).map(c => ({
                    clause: String(c.clause || '').slice(0, 200),
                    risk: ['low', 'medium', 'high'].includes(c.risk) ? c.risk : 'low',
                }));
            }
            return [];
        } catch (e) {
            return [];
        }
    }

    /**
     * Step 4: Generate a plain-English summary (1 paragraph).
     */
    async summarize(text) {
        const truncated = text.slice(0, 4000);

        const prompt = `Summarize this document in one plain-English paragraph (2–4 sentences).
Be factual and neutral. Do not use bullet points.

Document:
${truncated}`;

        try {
            const raw = await this.ollama.generate(prompt, {
                model: this.model,
                system: 'You are a document summarizer. Write one concise paragraph.',
                temperature: 0.3,
                maxTokens: 200,
            });
            return raw.trim().slice(0, 600);
        } catch (e) {
            return '';
        }
    }

    /**
     * Run full 4-step pipeline. Returns all results.
     * onProgress(step, total) called after each step.
     */
    async analyze(text, onProgress = null) {
        const results = { parsed: null, tags: [], clauses: [], summary: '' };

        results.parsed = await this.parseDocument(text);
        if (onProgress) onProgress(1, 4);

        results.tags = await this.suggestTags(results.parsed);
        if (onProgress) onProgress(2, 4);

        results.clauses = await this.extractClauses(text);
        if (onProgress) onProgress(3, 4);

        results.summary = await this.summarize(text);
        if (onProgress) onProgress(4, 4);

        return results;
    }

    /** Extract JSON from LLM output that may have surrounding text */
    _extractJSON(raw) {
        // Try direct parse first
        try { return JSON.parse(raw.trim()); } catch (_) {}
        // Find first { or [ and last } or ]
        const startObj = raw.indexOf('{');
        const startArr = raw.indexOf('[');
        let start = -1;
        let endChar = '';
        if (startObj !== -1 && (startArr === -1 || startObj < startArr)) {
            start = startObj; endChar = '}';
        } else if (startArr !== -1) {
            start = startArr; endChar = ']';
        }
        if (start === -1) return null;
        const end = raw.lastIndexOf(endChar);
        if (end <= start) return null;
        try { return JSON.parse(raw.slice(start, end + 1)); } catch (_) { return null; }
    }
}
