import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const startResearch = async (researchGoal) => {
  const response = await api.post('/research/start', {
    research_goal: researchGoal,
  });
  return response.data;
};

export const executeStep = async (sessionId, selectedGap = null) => {
  const response = await api.post('/research/step', {
    session_id: sessionId,
    selected_gap: selectedGap,
  });
  return response.data;
};

export const getResearchState = async (sessionId) => {
  const response = await api.get(`/research/state?session_id=${sessionId}`);
  return response.data;
};

export default api;
