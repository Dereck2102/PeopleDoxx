'use client';

import { type ScraperResult } from '@/lib/api';

interface ResultCardProps {
  result: ScraperResult;
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'object') return JSON.stringify(value, null, 2);
  return String(value);
}

function formatKey(key: string): string {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function ResultCard({ result }: ResultCardProps) {
  const dataEntries = Object.entries(result.data);
  const hasData = dataEntries.length > 0;

  return (
    <article
      className="animate-fade-in flex flex-col rounded-xl border border-slate-700 bg-slate-800 shadow-lg overflow-hidden"
      aria-label={`Resultado de ${result.source_name}`}
    >
      {/* Card Header */}
      <div className="flex items-start justify-between gap-2 border-b border-slate-700 px-5 py-4">
        <div>
          <h3 className="font-bold text-white">{result.source_name}</h3>
          <p className="mt-0.5 text-xs font-mono text-slate-500 uppercase tracking-wider">
            {result.source}
          </p>
        </div>
        <div className="flex flex-col items-end gap-1.5 shrink-0">
          {/* Success / Error badge */}
          <span
            className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
              result.success
                ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                : 'bg-red-500/20 text-red-400 border border-red-500/30'
            }`}
            aria-label={result.success ? 'Exitoso' : 'Error'}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                result.success ? 'bg-green-400' : 'bg-red-400'
              }`}
              aria-hidden="true"
            />
            {result.success ? 'Exitoso' : 'Error'}
          </span>

          {/* Duration badge */}
          <span
            className="inline-flex items-center rounded-full border border-slate-600 bg-slate-700/50 px-2 py-0.5 text-xs text-slate-400"
            aria-label={`Tiempo de respuesta: ${result.duration_ms} milisegundos`}
          >
            {result.duration_ms}ms
          </span>
        </div>
      </div>

      {/* Card Body */}
      <div className="flex-1 px-5 py-4">
        {result.success ? (
          hasData ? (
            <table className="w-full text-sm" aria-label={`Datos de ${result.source_name}`}>
              <tbody>
                {dataEntries.map(([key, value]) => (
                  <tr key={key} className="border-b border-slate-700/50 last:border-0">
                    <td className="py-2 pr-3 font-medium text-slate-400 align-top w-2/5">
                      {formatKey(key)}
                    </td>
                    <td className="py-2 text-slate-200 break-all align-top">
                      {typeof value === 'object' && value !== null ? (
                        <pre className="whitespace-pre-wrap text-xs text-slate-300 font-mono bg-slate-900/50 rounded p-2 overflow-x-auto">
                          {formatValue(value)}
                        </pre>
                      ) : (
                        formatValue(value)
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-sm text-slate-400 italic">
              Sin datos adicionales disponibles.
            </p>
          )
        ) : (
          <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-4">
            <div className="mb-1 flex items-center gap-2 text-amber-400">
              <span className="font-bold text-xs border border-amber-500/40 rounded px-1.5 py-0.5">!</span>
              <span className="text-sm font-semibold">No se pudo obtener información</span>
            </div>
            <p className="text-sm text-amber-200/80">
              {result.error ?? 'Error desconocido al consultar la fuente.'}
            </p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-slate-700/50 px-5 py-2.5">
        <p className="text-xs text-slate-500">
          Consultado:{' '}
          {new Date(result.fetched_at).toLocaleString('es-EC', {
            dateStyle: 'short',
            timeStyle: 'medium',
          })}
        </p>
      </div>
    </article>
  );
}
