import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { createUser, type CreateUserPayload } from '@/lib/api';
import { SOURCES, SOURCE_NAMES } from '@/lib/sources';
import Toggle from '@/components/Toggle';

export default function CreateUserPage() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'admin' | 'user'>('user');
  const [quotaDaily, setQuotaDaily] = useState(50);
  const [quotaMonthly, setQuotaMonthly] = useState(500);
  const [selectedSources, setSelectedSources] = useState<string[]>([...SOURCES]);
  const [canPdf, setCanPdf] = useState(true);
  const [canJson, setCanJson] = useState(true);
  const [expiresAt, setExpiresAt] = useState('');

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function toggleSource(source: string) {
    setSelectedSources((prev) =>
      prev.includes(source) ? prev.filter((s) => s !== source) : [...prev, source],
    );
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const payload: CreateUserPayload = {
        full_name: fullName,
        email,
        password,
        role,
        quota_daily: quotaDaily,
        quota_monthly: quotaMonthly,
        allowed_sources: selectedSources.length === SOURCES.length ? null : selectedSources,
        can_download_pdf: canPdf,
        can_download_json: canJson,
        expires_at: expiresAt ? expiresAt : null,
      };
      const user = await createUser(payload);
      navigate(`/users/${user.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al crear usuario');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/users')}
          className="text-slate-400 hover:text-white transition-colors text-sm"
        >
          ← Usuarios
        </button>
        <h1 className="text-2xl font-bold text-white">Crear Usuario</h1>
      </div>

      <form onSubmit={handleSubmit} className="rounded-xl bg-slate-800 border border-slate-700 p-6 space-y-6">
        {/* Basic info */}
        <div>
          <h2 className="text-sm font-semibold text-white border-b border-slate-700 pb-3 mb-5">
            Información básica
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">Nombre completo</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                placeholder="Juan Pérez"
                className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-orange-500 focus:outline-none focus:ring-1 focus:ring-orange-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">Correo electrónico</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="usuario@example.com"
                className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-orange-500 focus:outline-none focus:ring-1 focus:ring-orange-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">Contraseña</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                placeholder="Mínimo 8 caracteres"
                className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-orange-500 focus:outline-none focus:ring-1 focus:ring-orange-500"
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
              <label className="block text-xs font-medium text-slate-400 mb-1.5">Fecha de expiración (opcional)</label>
              <input
                type="date"
                value={expiresAt}
                onChange={(e) => setExpiresAt(e.target.value)}
                className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:border-orange-500 focus:outline-none focus:ring-1 focus:ring-orange-500"
              />
            </div>
          </div>
        </div>

        {/* Quotas */}
        <div>
          <h2 className="text-sm font-semibold text-white border-b border-slate-700 pb-3 mb-5">
            Cuotas
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">Cuota diaria</label>
              <input
                type="number"
                min={0}
                value={quotaDaily}
                onChange={(e) => setQuotaDaily(Number(e.target.value))}
                className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:border-orange-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1.5">Cuota mensual</label>
              <input
                type="number"
                min={0}
                value={quotaMonthly}
                onChange={(e) => setQuotaMonthly(Number(e.target.value))}
                className="w-full rounded-lg bg-slate-900 border border-slate-700 px-3 py-2 text-sm text-white focus:border-orange-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Permissions */}
        <div>
          <h2 className="text-sm font-semibold text-white border-b border-slate-700 pb-3 mb-5">
            Permisos
          </h2>

          <div className="space-y-5">
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

            {/* Downloads */}
            <div className="space-y-3">
              <Toggle checked={canPdf} onChange={setCanPdf} label="Puede descargar PDF" />
              <Toggle checked={canJson} onChange={setCanJson} label="Puede descargar JSON" />
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/30 px-3 py-2.5 text-sm text-red-400">
            {error}
          </div>
        )}

        {/* Submit */}
        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={submitting}
            className="flex-1 rounded-lg bg-orange-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-orange-600 disabled:opacity-60 transition-colors"
          >
            {submitting ? 'Creando usuario…' : 'Crear usuario'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/users')}
            className="rounded-lg bg-slate-700 px-4 py-2.5 text-sm font-medium text-slate-300 hover:bg-slate-600 transition-colors"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}
