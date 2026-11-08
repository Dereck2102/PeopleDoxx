import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getStats, type SystemStats } from '@/lib/api';
import StatCard from '@/components/StatCard';

export default function DashboardPage() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getStats()
      .then(setStats)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : 'Error al cargar estadísticas'),
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-sm text-slate-400 mt-1">Resumen general del sistema</p>
      </div>

      {/* Disclaimer banner */}
      <div className="flex items-start gap-3 rounded-xl bg-amber-500/10 border border-amber-500/30 px-4 py-3">
        <span className="font-bold text-xs border border-amber-500/40 rounded px-1.5 py-0.5 text-amber-300">AVISO</span>
        <p className="text-sm text-amber-300">
          <span className="font-semibold">Panel de administración</span> — Acceso restringido a
          operadores autorizados. Todas las acciones quedan registradas.
        </p>
      </div>

      {/* Stats */}
      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="rounded-xl bg-slate-800 p-6 h-32 animate-pulse" />
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-xl bg-red-500/10 border border-red-500/30 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <StatCard icon="USR" value={stats.total_users} label="Usuarios totales" />
          <StatCard icon="ACT" value={stats.active_users} label="Usuarios activos" />
          <StatCard icon="HOY" value={stats.searches_today} label="Búsquedas hoy" />
          <StatCard
            icon="TOT"
            value={stats.total_searches_all_time}
            label="Búsquedas históricas"
          />
        </div>
      )}

      {/* Quick actions */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Acciones rápidas</h2>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => navigate('/users/new')}
            className="rounded-lg bg-orange-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-orange-600 transition-colors"
          >
            + Crear Usuario
          </button>
          <button
            onClick={() => navigate('/users')}
            className="rounded-lg bg-slate-700 px-5 py-2.5 text-sm font-semibold text-white hover:bg-slate-600 transition-colors"
          >
            Ver Todos los Usuarios
          </button>
        </div>
      </div>
    </div>
  );
}
