const BASE = '/api';
const TOKEN_KEY = 'pdx_token';
const EMAIL_KEY = 'pdx_email';

export interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'user';
  is_active: boolean;
  terms_accepted: boolean;
  quota_daily: number;
  quota_daily_used: number;
  quota_monthly: number;
  quota_monthly_used: number;
  allowed_sources: string[] | null;
  can_download_pdf: boolean;
  can_download_json: boolean;
  expires_at: string | null;
  api_key: string | null;
  created_at: string;
  updated_at: string;
  total_searches: number;
}

export interface SystemStats {
  total_users: number;
  active_users: number;
  total_searches_all_time: number;
  searches_today: number;
}

export interface UserListResponse {
  items: AdminUser[];
  total: number;
  page: number;
  page_size: number;
}

export interface SearchHistoryItem {
  id: string;
  cedula: string;
  sources: string[];
  success_count: number;
  total_count: number;
  cached: boolean;
  created_at: string;
}

export interface SearchHistoryResponse {
  items: SearchHistoryItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface CreateUserPayload {
  email: string;
  full_name: string;
  password: string;
  role: 'admin' | 'user';
  quota_daily: number;
  quota_monthly: number;
  allowed_sources: string[] | null;
  can_download_pdf: boolean;
  can_download_json: boolean;
  expires_at: string | null;
}

export interface UpdateUserPayload {
  full_name?: string;
  role?: 'admin' | 'user';
  is_active?: boolean;
  expires_at?: string | null;
  quota_daily?: number;
  quota_monthly?: number;
  allowed_sources?: string[] | null;
  can_download_pdf?: boolean;
  can_download_json?: boolean;
}

export interface ListUsersParams {
  page?: number;
  page_size?: number;
  search?: string;
  role?: string;
  is_active?: string;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      // keep default
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredEmail(): string | null {
  return localStorage.getItem(EMAIL_KEY);
}

export function authHeaders(): Record<string, string> {
  const token = getToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

export async function login(email: string, password: string): Promise<{ access_token: string; refresh_token: string }> {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`${BASE}/auth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  });
  const data = await handleResponse<{ access_token: string; refresh_token: string }>(res);
  localStorage.setItem(TOKEN_KEY, data.access_token);
  localStorage.setItem(EMAIL_KEY, email);
  return data;
}

export function logout(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(EMAIL_KEY);
}

export async function getStats(): Promise<SystemStats> {
  const res = await fetch(`${BASE}/admin/stats`, {
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
  });
  return handleResponse<SystemStats>(res);
}

export async function listUsers(params: ListUsersParams = {}): Promise<UserListResponse> {
  const qs = new URLSearchParams();
  if (params.page !== undefined) qs.set('page', String(params.page));
  if (params.page_size !== undefined) qs.set('page_size', String(params.page_size));
  if (params.search) qs.set('search', params.search);
  if (params.role) qs.set('role', params.role);
  if (params.is_active !== undefined && params.is_active !== '') qs.set('is_active', params.is_active);
  const res = await fetch(`${BASE}/admin/users?${qs.toString()}`, {
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
  });
  return handleResponse<UserListResponse>(res);
}

export async function getUser(id: string): Promise<AdminUser> {
  const res = await fetch(`${BASE}/admin/users/${id}`, {
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
  });
  return handleResponse<AdminUser>(res);
}

export async function createUser(data: CreateUserPayload): Promise<AdminUser> {
  const res = await fetch(`${BASE}/admin/users`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse<AdminUser>(res);
}

export async function updateUser(id: string, data: UpdateUserPayload): Promise<AdminUser> {
  const res = await fetch(`${BASE}/admin/users/${id}`, {
    method: 'PATCH',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return handleResponse<AdminUser>(res);
}

export async function deleteUser(id: string): Promise<void> {
  const res = await fetch(`${BASE}/admin/users/${id}`, {
    method: 'DELETE',
    headers: { ...authHeaders() },
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail ?? JSON.stringify(body);
    } catch {
      // keep default
    }
    throw new Error(detail);
  }
}

export async function resetQuota(
  id: string,
  options: { reset_daily?: boolean; reset_monthly?: boolean },
): Promise<AdminUser> {
  const res = await fetch(`${BASE}/admin/users/${id}/reset-quota`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(options),
  });
  return handleResponse<AdminUser>(res);
}

export async function generateApiKey(id: string): Promise<{ api_key: string }> {
  const res = await fetch(`${BASE}/admin/users/${id}/generate-api-key`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
  });
  return handleResponse<{ api_key: string }>(res);
}

export async function getUserHistory(id: string, page = 1): Promise<SearchHistoryResponse> {
  const res = await fetch(`${BASE}/admin/users/${id}/history?page=${page}&page_size=10`, {
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
  });
  return handleResponse<SearchHistoryResponse>(res);
}
