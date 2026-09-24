import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to handle NaN/nulls securely
const sanitizeResponse = (data) => {
    if (typeof data === 'number' && Number.isNaN(data)) return null;
    if (Array.isArray(data)) return data.map(sanitizeResponse);
    if (data !== null && typeof data === 'object') {
        const sanitized = {};
        for (const [k, v] of Object.entries(data)) {
            sanitized[k] = sanitizeResponse(v);
        }
        return sanitized;
    }
    return data;
};

export const api = {
  getHealth: async () => sanitizeResponse((await apiClient.get('/health')).data),
  getPlatformSummary: async () => sanitizeResponse((await apiClient.get('/platform-summary')).data),
  getPipelines: async () => sanitizeResponse((await apiClient.get('/pipelines')).data),
  getLatestQuality: async () => sanitizeResponse((await apiClient.get('/quality/latest')).data),
  getAnomalies: async () => sanitizeResponse((await apiClient.get('/anomalies')).data),
  getMetrics: async () => sanitizeResponse((await apiClient.get('/metrics')).data),
  getLineage: async () => sanitizeResponse((await apiClient.get('/lineage')).data),
  chatWithAgent: async (query) => sanitizeResponse((await apiClient.post('/agent/chat', { query })).data)
};
