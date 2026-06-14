import axios from 'axios';

// ── Base Configuration ────────────────────────────────────────────────────────
// Nginx (port 80) proxies /api/v1/ → http://backend:8000/api/v1/ inside Docker
const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// ── Request Interceptor: Attach Bearer Token ──────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Response Interceptor: Handle 401 Globally ─────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ── Helper: decode user ID from JWT sub claim ─────────────────────────────────
export const getUserIdFromToken = () => {
  const token = localStorage.getItem('token');
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return parseInt(payload.sub, 10);
  } catch (e) {
    return null;
  }
};

// ── Auth API ──────────────────────────────────────────────────────────────────
export const authAPI = {
  // POST /auth/login — backend uses OAuth2PasswordRequestForm (multipart)
  login: (credentials) => {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);
    return api.post('/auth/login', formData);
  },
  // POST /auth/register — backend expects { email, password }
  register: (userData) => api.post('/auth/register', userData),
};

// ── Chat API ──────────────────────────────────────────────────────────────────
// Backend ChatMessageCreate schema: { role, content, user_id, daily_plan_id? }
export const chatAPI = {
  getMessages: (journeyId = null) => api.get('/chat-messages/', { params: journeyId ? { journey_id: journeyId } : {} }),
  sendMessage: (content, role = 'user', dailyPlanId = null, journeyId = null) => {
    const user_id = getUserIdFromToken();
    const payload = { role, content, user_id };
    if (dailyPlanId !== null) payload.daily_plan_id = dailyPlanId;
    if (journeyId !== null) payload.journey_id = journeyId;
    return api.post('/chat-messages/', payload);
  },
  requestHint: (dailyPlanId, userQuery) => api.post(`/chat-messages/${dailyPlanId}/hint`, null, { params: { user_query: userQuery } }),
};

// ── Journey API ───────────────────────────────────────────────────────────────
// Backend JourneyGenerateRequest schema: { prompt, target_days }
export const journeyAPI = {
  getJourneys: () => api.get('/journeys/'),
  getJourney: (id) => api.get(`/journeys/${id}`),
  // generate expects { prompt: string, target_days: number }
  generate: (prompt, targetDays) =>
    api.post('/journeys/generate', { prompt, target_days: targetDays }),
  checkSimilarity: (prompt, targetDays) =>
    api.post('/journeys/check-similarity', { prompt, target_days: targetDays }),
  clone: (sourceJourneyId, newPrompt) =>
    api.post('/journeys/clone', { source_journey_id: sourceJourneyId, new_prompt: newPrompt }),
  modify: (id, prompt) => 
    api.post(`/journeys/${id}/modify`, { prompt }),
  exportPdf: (id) => api.get(`/journeys/${id}/export-pdf`, { responseType: 'blob' }),
  delete: (id) => api.delete(`/journeys/${id}`),
};

// ── Daily Plan API ────────────────────────────────────────────────────────────
export const dailyPlanAPI = {
  getDailyPlan: (id) => api.get(`/daily-plans/${id}`),
  generateContent: (id) => api.post(`/daily-plans/${id}/generate-content`),
  getJourneyDailyPlans: (journeyId) => api.get(`/daily-plans/journey/${journeyId}`),
  markAsCompleted: (id) => api.patch(`/daily-plans/${id}/complete`)
};

// ── Task API ──────────────────────────────────────────────────────────────────
export const taskAPI = {
  getDailyPlanTasks: (dailyPlanId) => api.get(`/tasks/daily-plan/${dailyPlanId}`)
};

// ── Submission API ────────────────────────────────────────────────────────────
export const submissionAPI = {
  submitCode: (taskId, code, languageId = 71) => {
    const user_id = getUserIdFromToken();
    return api.post('/submissions/', { 
      task_id: taskId, 
      submitted_code: code, 
      language_id: languageId,
      user_id: user_id,
      result_status: 'pending'
    });
  },
  getMySubmissions: (skip = 0, limit = 100) => api.get(`/submissions/user?skip=${skip}&limit=${limit}`),
  getStatistics: () => api.get('/submissions/user/statistics')
};

// ── Knowledge Source API ────────────────────────────────────────────────────────
export const knowledgeSourceAPI = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/knowledge-sources/upload', formData);
  },
  getKnowledgeSources: (skip = 0, limit = 100) => api.get(`/knowledge-sources/?skip=${skip}&limit=${limit}`)
};

// ── Favorites API ─────────────────────────────────────────────────────────────
export const favoritesAPI = {
  addFavorite: (data) => api.post(`/favorites/`, data),
  removeFavorite: (sourceId) => api.delete(`/favorites/${sourceId}`),
  getFavorites: (skip = 0, limit = 100) => api.get(`/favorites/?skip=${skip}&limit=${limit}`)
};

// ── Demo API ────────────────────────────────────────────────────────
export const demoAPI = {
  startDemo: () => api.post('/demo/start'),
  solveTask: (taskDescription, starterCode = null) => api.post('/demo/solve-task', { task_description: taskDescription, starter_code: starterCode })
};

// ── Hints API (Idle Assistance) ────────────────────────────────────────────────
export const hintsAPI = {
  generateHint: (request) => api.post('/hints/generate-hint', request),
  dismissHint: (hintId) => api.patch(`/hints/dismiss-hint/${hintId}`)
};

export const journeysAPI = {
  getJourneys: () => api.get('/journeys/'),
  getJourney: (id) => api.get(`/journeys/${id}`),
  generateJourney: (data) => api.post('/journeys/generate', data),
};

export default api;
