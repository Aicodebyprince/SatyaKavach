/**
 * SatyaKavach - API Client Service
 */

import axios from 'axios';
import type {
  TokenResponse,
  MediaUploadResponse,
  VerificationStatusResponse,
  TrustScoreResult,
  VerificationHistoryResponse,
} from '../types';

const API_BASE = (import.meta.env.VITE_API_URL || '') + '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('satyakavach_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auto-provision an anonymous session on the first 401, then retry once —
// lets citizens use verification & history without registering first.
let ensuringAnon: Promise<void> | null = null;

function ensureAnonymousToken(): Promise<void> {
  if (!ensuringAnon) {
    ensuringAnon = api
      .post<{ token: string }>('/auth/anonymous')
      .then((res) => {
        localStorage.setItem('satyakavach_token', res.data.token);
      })
      .finally(() => {
        ensuringAnon = null;
      });
  }
  return ensuringAnon;
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const config = error?.config as
      | ((typeof error.config) & { _retriedAfterAnon?: boolean })
      | undefined;
    const url = String(config?.url ?? '');
    if (
      error?.response?.status === 401 &&
      config &&
      !config._retriedAfterAnon &&
      !url.startsWith('/auth/')
    ) {
      config._retriedAfterAnon = true;
      await ensureAnonymousToken();
      return api.request(config);
    }
    return Promise.reject(error);
  }
);

// ── Auth ────────────────────────────────────────────────────────────
export const authAPI = {
  register: async (data: { email?: string; phone_number?: string; password: string; full_name?: string }) => {
    const res = await api.post<TokenResponse>('/auth/register', data);
    localStorage.setItem('satyakavach_token', res.data.access_token);
    return res.data;
  },

  login: async (data: { email?: string; phone_number?: string; password: string }) => {
    const res = await api.post<TokenResponse>('/auth/login', data);
    localStorage.setItem('satyakavach_token', res.data.access_token);
    return res.data;
  },

  anonymous: async () => {
    const res = await api.post<{ user_id: string; token: string }>('/auth/anonymous');
    localStorage.setItem('satyakavach_token', res.data.token);
    return res.data;
  },

  logout: () => {
    localStorage.removeItem('satyakavach_token');
  },
};

// ── Upload & Verification ───────────────────────────────────────────
export const uploadAPI = {
  uploadFile: async (file: File, language?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (language) formData.append('language', language);

    const res = await api.post<MediaUploadResponse>('/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  submitLink: async (url: string, language?: string) => {
    const res = await api.post<MediaUploadResponse>('/upload/link', { url, language });
    return res.data;
  },
};

// ── Results ─────────────────────────────────────────────────────────
export const verificationAPI = {
  getStatus: async (mediaId: string) => {
    const res = await api.get<VerificationStatusResponse>(`/verification/${mediaId}/status`);
    return res.data;
  },

  getResult: async (mediaId: string) => {
    const res = await api.get<TrustScoreResult>(`/verification/${mediaId}/result`);
    return res.data;
  },

  getHistory: async (page = 1, pageSize = 20) => {
    const res = await api.get<VerificationHistoryResponse>('/verification/history', {
      params: { page, page_size: pageSize },
    });
    return res.data;
  },
};
