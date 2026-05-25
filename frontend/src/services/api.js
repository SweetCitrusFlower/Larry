import axios from 'axios';

// ── Base Configuration ────────────────────────────────────────────────────────
// Nginx (port 80) proxies /api/v1/ → http://backend:8000/api/v1/ inside Docker
const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
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
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  // POST /auth/register — backend expects { email, password }
  register: (userData) => api.post('/auth/register', userData),
};

// ── Chat API ──────────────────────────────────────────────────────────────────
// Backend ChatMessageCreate schema: { role, content, user_id, daily_plan_id? }
export const chatAPI = {
  getMessages: () => api.get('/chat-messages/'),
  sendMessage: (content, role = 'user', dailyPlanId = null) => {
    const user_id = getUserIdFromToken();
    const payload = { role, content, user_id };
    if (dailyPlanId !== null) payload.daily_plan_id = dailyPlanId;
    return api.post('/chat-messages/', payload);
  },
};

// ── Journey API ───────────────────────────────────────────────────────────────
// Backend JourneyGenerateRequest schema: { prompt, target_days }
export const journeyAPI = {
  getJourneys: () => api.get('/journeys/'),
  getJourney: (id) => api.get(`/journeys/${id}`),
  // generate expects { prompt: string, target_days: number }
  generate: (prompt, targetDays) =>
    api.post('/journeys/generate', { prompt, target_days: targetDays }),
  exportPdf: (id) => api.get(`/journeys/${id}/export-pdf`, { responseType: 'blob' }),
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
  getMySubmissions: (skip = 0, limit = 100) => api.get(`/submissions/user?skip=${skip}&limit=${limit}`)
};

// ── Knowledge Source API ────────────────────────────────────────────────────────
export const knowledgeSourceAPI = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/knowledge-sources/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  }
};

export const journeysAPI = {
  getJourneys: () => api.get('/journeys/'),
  getJourney: (id) => api.get(`/journeys/${id}`),
  generateJourney: (data) => api.post('/journeys/generate', data),
};

export default api;
