export interface ScraperResult {
  source: string;
  source_name: string;
  success: boolean;
  data: Record<string, unknown>;
  fetched_at: string;
  error?: string;
  duration_ms: number;
}

export interface SearchResponse {
  cedula: string;
  results: ScraperResult[];
  generated_at: string;
  total_sources: number;
  successful_sources: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? '';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY ?? '';

function buildHeaders(extra?: Record<string, string>): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(API_KEY ? { 'X-API-Key': API_KEY } : {}),
    ...extra,
  };
  return headers;
}

export async function searchByCedula(cedula: string): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE}/api/v1/search`, {
    method: 'POST',
    headers: buildHeaders(),
    body: JSON.stringify({ cedula }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(
      `Error ${response.status}: ${text || response.statusText}`
    );
  }

  return response.json() as Promise<SearchResponse>;
}

export async function downloadReport(
  cedula: string,
  format: 'pdf' | 'json'
): Promise<Blob> {
  const response = await fetch(`${API_BASE}/api/v1/reports/${cedula}/${format}`, {
    method: 'GET',
    headers: buildHeaders({ 'Content-Type': 'application/octet-stream' }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(
      `Error ${response.status}: ${text || response.statusText}`
    );
  }

  return response.blob();
}
