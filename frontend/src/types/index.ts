/**
 * SatyaKavach - TypeScript Types
 */

export interface User {
  user_id: string;
  email?: string;
  phone_number?: string;
  full_name?: string;
  preferred_language: 'hi' | 'en';
  role: string;
  is_anonymous: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface MediaUploadResponse {
  media_id: string;
  media_type: string;
  status: string;
  message: string;
  created_at: string;
}

export interface VerificationStatusResponse {
  media_id: string;
  status: 'queued' | 'preprocessing' | 'analyzing' | 'scoring' | 'complete' | 'failed';
  progress: string;
  trust_score?: number;
  verdict?: string;
}

export interface TrustScoreResult {
  record_id: string;
  media_id: string;
  media_type: string;
  trust_score: number;
  verdict: 'HIGH_TRUST' | 'UNCERTAIN' | 'LOW_TRUST';
  recommended_action: string;
  model_breakdown: Record<string, any>;
  evidence_report: EvidenceReport;
  confidence?: number;
  analysis_duration_ms?: number;
  created_at: string;
}

export interface EvidenceReport {
  trust_score: number;
  verdict: string;
  summary_en: string;
  summary_hi: string;
  findings: Finding[];
  artifacts: string[];
  signals_analyzed: string[];
  analysis_completeness: string;
}

export interface Finding {
  signal: string;
  severity: 'high' | 'low' | 'medium';
  message: string;
  models?: string[];
  vendors?: string[];
}

export interface VerificationHistoryResponse {
  records: TrustScoreResult[];
  total: number;
  page: number;
  page_size: number;
}
