import { type ScraperResult } from '@/lib/api';
import { ResultCard } from '@/components/ResultCard';
import { LoadingSkeleton } from '@/components/LoadingSkeleton';

interface ResultsDashboardProps {
  results: ScraperResult[];
  isLoading: boolean;
}

export function ResultsDashboard({ results, isLoading }: ResultsDashboardProps) {
  if (isLoading) {
    return <LoadingSkeleton />;
  }

  const successCount = results.filter((r) => r.success).length;
  const totalCount = results.length;

  const badgeColor =
    successCount === totalCount
      ? 'bg-green-500/20 text-green-400 border-green-500/30'
      : successCount === 0
      ? 'bg-red-500/20 text-red-400 border-red-500/30'
      : 'bg-amber-500/20 text-amber-400 border-amber-500/30';

  return (
    <section aria-label="Resultados de la búsqueda">
      {/* Summary bar */}
      <div className="mb-6 flex flex-col gap-3 rounded-xl border border-slate-700 bg-slate-800 p-4 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-slate-300">
          Resumen del reporte
        </p>
        <span
          className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm font-semibold ${badgeColor}`}
          aria-label={`${successCount} de ${totalCount} fuentes respondieron exitosamente`}
        >
          <span
            className={`h-2 w-2 rounded-full ${
              successCount === totalCount
                ? 'bg-green-400'
                : successCount === 0
                ? 'bg-red-400'
                : 'bg-amber-400'
            }`}
            aria-hidden="true"
          />
          {successCount}/{totalCount} fuentes respondieron exitosamente
        </span>
      </div>

      {/* Grid */}
      {results.length === 0 ? (
        <p className="py-12 text-center text-slate-400">No hay resultados disponibles.</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {results.map((result, index) => (
            <ResultCard key={`${result.source}-${index}`} result={result} />
          ))}
        </div>
      )}
    </section>
  );
}
