import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  getUser,
  updateUser,
  resetQuota,
  generateApiKey,
  getUserHistory,
  type AdminUser,
  type SearchHistoryResponse,
  type UpdateUserPayload,
} from '@/lib/api';
import { SOURCES, SOURCE_NAMES } from '@/lib/sources';
import Toggle from '@/components/Toggle';
import Badge from '@/components/Badge';

function maskApiKey(key: string): string {
  if (key.length <= 10) return key;
  return `${key.slice(0, 7)}****…****${key.slice(-4)}`;
}

export default function UserDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [user, setUser] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);

  // Form state
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<'admin' | 'user'>('user');
  const [isActive, setIsActive] = useState(true);
  const [expiresAt, setExpiresAt] = useState('');
  const [quotaDaily, setQuotaDaily] = useState(50);
  const [quotaMonthly, setQuotaMonthly] = useState(500);
  const [selectedSources, setSelectedSources] = useState<string[]>([...SOURCES]);
  const [canPdf, setCanPdf] = useState(true);
  const [canJson, setCanJson] = useState(true);

  // History state
  const [history, setHistory] = useState<SearchHistoryResponse | null>(null);
  const [histPage, setHistPage] = useState(1);
  const [histLoading, setHistLoading] = useState(false);

  const loadUser = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const u = await getUser(id);
      setUser(u);
      setFullName(u.full_name);
      setRole(u.role);
      setIsActive(u.is_active);
      setExpiresAt(u.expires_at ? u.expires_at.slice(0, 10) : '');
      setQuotaDaily(u.quota_daily);
      setQuotaMonthly(u.quota_monthly);
      setSelectedSources(u.allowed_sources ?? [...SOURCES]);
      setCanPdf(u.can_download_pdf);
      setCanJson(u.can_download_json);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar usuario');
    } finally {
      setLoading(false);
    }
  }, [id]);

  const loadHistory = useCallback(async () => {
    if (!id) return;
    setHistLoading(true);
    try {
      const h = await getUserHistory(id, histPage);
      setHistory(h);
    } catch {
      // non-critical
    } finally {
      setHistLoading(false);
    }
  }, [id, histPage]);

  useEffect(() => { void loadUser(); }, [loadUser]);
  useEffect(() => { void loadHistory(); }, [loadHistory]);

  async function handleSave() {
    if (!id) return;
    setSaving(true);
    setSaveMsg(null);
    try {
      const payload: UpdateUserPayload = {
        full_name: fullName,
        role,
        is_active: isActive,
        expires_at: expiresAt ? expiresAt : null,
        quota_daily: quotaDaily,
        quota_monthly: quotaMonthly,
        allowed_sources: selectedSources.length === SOURCES.length ? null : selectedSources,
        can_download_pdf: canPdf,
        can_download_json: canJson,
      };
      const updated = await updateUser(id, payload);
      setUser(updated);
      setSaveMsg('Guardado correctamente');
    } catch (err) {
      setSaveMsg(err instanceof Error ? err.message : 'Error al guardar');
    } finally {
      setSaving(false);
    }
  }

  async function handleResetDaily() {
    if (!id) return;
    try {
      const updated = await resetQuota(id, { reset_daily: true });
      setUser(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al resetear cuota');
    }
  }

  async function handleResetMonthly() {
    if (!id) return;
    try {
      const updated = await resetQuota(id, { reset_monthly: true });
      setUser(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al resetear cuota');
    }
  }

  async function handleGenerateApiKey() {
    if (!id) return;
    try {
      const { api_key } = await generateApiKey(id);
      setUser((prev) => prev ? { ...prev, api_key } : prev);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al generar API key');
    }
  }

  function toggleSource(source: string) {
    setSelectedSources((prev) =>
      prev.includes(source) ? prev.filter((s) => s !== source) : [...prev, source],
    );
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 rounded bg-slate-800 animate-pulse" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-96 rounded-xl bg-slate-800 animate-pulse" />
          <div className="h-96 rounded-xl bg-slate-800 animate-pulse" />
        </div>
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className="rounded-xl bg-red-500/10 border border-red-500/30 px-4 py-3 text-sm text-red-400">
        {error ?? 'Usuario no encontrado'}
      </div>
    );
  }

  const histTotalPages = history ? Math.ceil(history.total / 10) : 1;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/users')}
          className="text-slate-400 hover:text-white transition-colors text-sm"
        >
          ← Usuarios
        </button>
        <div>
          <h1 className="text-2xl font-bold text-white">{user.full_name}</h1>
          <p className="text-sm text-slate-400">{user.email}</p>
        </div>
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left — User info */}
        <div className="rounded-xl bg-slate-800 border border-slate-700 p-6 space-y-5">
          <h2 className="text-base font-semibold text-white border-b border-slate-700 pb-3">
            Información del usuario
          </h2>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">Nombre completo</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:border-orange-500 focus:outline-none focus:ring-1 focus:ring-orange-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">Email</label>
            <input
              type="email"
              value={user.email}
              readOnly
              className="w-full rounded-lg bg-slate-900/50 border border-slate-700 px-3 py-2 text-sm text-slate-500 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">Rol</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as 'admin' | 'user')}
              className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:border-orange-500 focus:outline-none"
            >
              <option value="user">Usuario</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1.5">Fecha de expiración</label>
            <input
              type="date"
              value={expiresAt}
              onChange={(e) => setExpiresAt(e.target.value)}
              className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:border-orange-500 focus:outline-none focus:ring-1 focus:ring-orange-500"
            />
          </div>

          <div className="flex items-center justify-between py-1">
            <span className="text-sm text-slate-300">Cuenta activa</span>
            <Toggle checked={isActive} onChange={setIsActive} />
          </div>

          {saveMsg && (
            <p className={`text-xs ${saveMsg.startsWith('Error') ? 'text-red-400' : 'text-emerald-400'}`}>
              {saveMsg}
            </p>
          )}

          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full rounded-lg bg-orange-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-orange-600 disabled:opacity-60 transition-colors"
          >
            {saving ? 'Guardando…' : 'Guardar cambios'}
          </button>
        </div>

        {/* Right — Quota & Permissions */}
        <div className="rounded-xl bg-slate-800 border border-slate-700 p-6 space-y-5">
          <h2 className="text-base font-semibold text-white border-b border-slate-700 pb-3">
            Cuota y permisos
          </h2>

          {/* Daily quota */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-medium text-slate-400">Cuota diaria</label>
              <span className="text-xs text-slate-500">
                Usado: <span className={user.quota_daily_used >= quotaDaily ? 'text-red-400' : 'text-slate-300'}>{user.quota_daily_used}</span>
              </span>
            </div>
            <div className="flex gap-2">
              <input
                type="number"
                min={0}
                value={quotaDaily}
                onChange={(e) => setQuotaDaily(Number(e.target.value))}
                className="flex-1 rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:border-orange-500 focus:outline-none"
              />
              <button
                onClick={handleResetDaily}
                className="rounded-lg px-3 py-2 text-xs font-medium bg-slate-700 text-slate-300 hover:bg-slate-600 whitespace-nowrap transition-colors"
              >
                Resetear
              </button>
            </div>
          </div>

          {/* Monthly quota */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-medium text-slate-400">Cuota mensual</label>
              <span className="text-xs text-slate-500">
                Usado: <span className={user.quota_monthly_used >= quotaMonthly ? 'text-red-400' : 'text-slate-300'}>{user.quota_monthly_used}</span>
              </span>
            </div>
            <div className="flex gap-2">
              <input
                type="number"
                min={0}
                value={quotaMonthly}
                onChange={(e) => setQuotaMonthly(Number(e.target.value))}
                className="flex-1 rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:border-orange-500 focus:outline-none"
              />
              <button
                onClick={handleResetMonthly}
                className="rounded-lg px-3 py-2 text-xs font-medium bg-slate-700 text-slate-300 hover:bg-slate-600 whitespace-nowrap transition-colors"
              >
                Resetear
              </button>
            </div>
          </div>

          {/* Sources */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-2">
              Fuentes permitidas{' '}
              {selectedSources.length === SOURCES.length && (
                <span className="text-emerald-400">(sin restricciones)</span>
              )}
            </label>
            <div className="grid grid-cols-2 gap-2">
              {SOURCES.map((src) => (
                <label key={src} className="flex items-center gap-2 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={selectedSources.includes(src)}
                    onChange={() => toggleSource(src)}
                    className="w-4 h-4 rounded border-slate-600 bg-slate-900 accent-orange-500"
                  />
                  <span className="text-xs text-slate-300 group-hover:text-white transition-colors">
                    {src}
                    <span className="block text-slate-500 leading-tight">{SOURCE_NAMES[src]}</span>
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Download permissions */}
          <div className="space-y-3">
            <Toggle checked={canPdf} onChange={setCanPdf} label="Puede descargar PDF" />
            <Toggle checked={canJson} onChange={setCanJson} label="Puede descargar JSON" />
          </div>

          {/* API Key */}
          <div className="border-t border-slate-700 pt-4">
            <label className="block text-xs font-medium text-slate-400 mb-2">API Key</label>
            <div className="flex gap-2 items-center">
              <code className="flex-1 rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-xs text-slate-300 font-mono truncate">
                {user.api_key ? maskApiKey(user.api_key) : 'Sin API key'}
              </code>
              <button
                onClick={handleGenerateApiKey}
                className="rounded-lg px-3 py-2 text-xs font-medium bg-slate-700 text-slate-300 hover:bg-slate-600 whitespace-nowrap transition-colors"
              >
                Regenerar API Key
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Search history */}
      <div className="rounded-xl bg-slate-800 border border-slate-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700">
          <h2 className="text-base font-semibold text-white">Historial de búsquedas</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 bg-slate-900/50">
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">Cédula</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">Fuentes</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">Éxito</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">Caché</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-400 uppercase">Fecha</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50">
              {histLoading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i}>
                    {[...Array(5)].map((__, j) => (
                      <td key={j} className="px-4 py-3">
                        <div className="h-4 rounded bg-slate-700 animate-pulse w-3/4" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : !history || history.items.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-8 text-center text-sm text-slate-500">
                    Sin búsquedas registradas
                  </td>
                </tr>
              ) : (
                history.items.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-700/30 transition-colors">
                    <td className="px-4 py-3 font-mono text-xs text-white">{item.cedula}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {item.sources.map((s) => (
                          <span key={s} className="rounded px-1.5 py-0.5 text-xs bg-slate-700 text-slate-300">
                            {s}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-300 text-xs">
                      {item.success_count}/{item.total_count}
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={item.cached ? 'info' : 'neutral'}>
                        {item.cached ? 'Sí' : 'No'}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400">
                      {new Date(item.created_at).toLocaleString('es-EC')}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {histTotalPages > 1 && (
          <div className="border-t border-slate-700 px-4 py-3 flex items-center justify-between">
            <p className="text-xs text-slate-400">Página {histPage} de {histTotalPages}</p>
            <div className="flex gap-2">
              <button
                onClick={() => setHistPage((p) => Math.max(1, p - 1))}
                disabled={histPage === 1}
                className="rounded px-3 py-1 text-xs font-medium bg-slate-700 text-slate-300 hover:bg-slate-600 disabled:opacity-40 transition-colors"
              >
                ← Anterior
              </button>
              <button
                onClick={() => setHistPage((p) => Math.min(histTotalPages, p + 1))}
                disabled={histPage === histTotalPages}
                className="rounded px-3 py-1 text-xs font-medium bg-slate-700 text-slate-300 hover:bg-slate-600 disabled:opacity-40 transition-colors"
              >
                Siguiente →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
