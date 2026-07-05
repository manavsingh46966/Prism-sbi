const BASE = 'http://localhost:8000/api';

export const api = {
  get: async (path) => {
    const res = await fetch(`${BASE}${path}`);
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return res.json();
  },
  post: async (path, body = {}) => {
    const res = await fetch(`${BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return res.json();
  },
};

export const usePersonaColor = (persona) => {
  const map = {
    farmer: '#00d4a0',
    gig_worker: '#f5a623',
    kirana: '#4f7cff',
    first_timer: '#b47ef5',
    nri: '#ff4757',
  };
  return map[persona] || '#8b9cc8';
};

export const useScoreColor = (score) => {
  if (score >= 70) return '#00d4a0';
  if (score >= 50) return '#f5a623';
  return '#ff4757';
};

export const formatPersona = (p) => ({
  farmer: '🌾 Farmer',
  gig_worker: '🛵 Gig Worker',
  kirana: '🏪 Kirana Owner',
  first_timer: '👤 First Timer',
  nri: '✈️ NRI',
}[p] || p);

export const formatChannel = (c) => ({
  voice: '📞 Voice Call',
  whatsapp: '💬 WhatsApp',
  ussd: '📱 USSD',
  in_app: '🔔 In-App',
}[c] || c);
