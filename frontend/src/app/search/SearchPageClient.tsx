'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { searchByCedula, type SearchResponse } from '@/lib/api';
import { validateCedula } from '@/lib/cedula';
import { ResultsDashboard } from '@/components/ResultsDashboard';
import { ReportDownload } from '@/components/ReportDownload';
import { LoadingSkeleton } from '@/components/LoadingSkeleton';

type PageState = 'loading' | 'success' | 'error';

export default function SearchPageClient() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const cedula = searchParams.get('cedula') ?? '';

  const [state, setState] = useState<PageState>('loading');
  const [data, setData] = useState<SearchResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState<string>('');

  useEffect(() => {
    if (!cedula) {
      router.replace('/');
      return;
    }

    const validation = validateCedula(cedula);
    if (!validation.valid) {
      setState('error');
      setErrorMsg(validation.error ?? 'Cédula inválida.');
      return;
    }

    setState('loading');
    setData(null);
    setErrorMsg('');

    searchByCedula(cedula)
      .then((response) => {
        setData(response);
        setState('success');
      })
      .catch((err: unknown) => {
        const message =
          err instanceof Error ? err.message : 'Error al conectar con el servidor.';
        setErrorMsg(message);
        setState('error');
      });
  }, [cedula, router]);

  return (
    <div className="min-h-[calc(100vh-64px)] px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm text-slate-500 uppercase tracking-widest font-medium">
              Reporte de identidad pública
            </p>
            <h1 className="mt-1 text-3xl font-extrabold text-white">
              Cédula:{' '}
              <span className="text-orange-500 font-mono tracking-widest">{cedula}</span>
            </h1>
          </div>

          {state === 'success' && data && (
            <ReportDownload cedula={cedula} />
          )}
        </div>

        {/* Back button */}
        <button
          onClick={() => router.push('/')}
          className="mb-6 inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white"
          aria-label="Volver a la búsqueda"
        >
          <span aria-hidden="true">←</span> Nueva búsqueda
        </button>

        {/* States */}
        {state === 'loading' && <LoadingSkeleton />}

        {state === 'error' && (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-8 text-center">
            <div className="mb-3 inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-500/20 text-red-400 font-bold text-lg">!</div>
            <h2 className="mb-2 text-lg font-semibold text-red-400">Error en la consulta</h2>
            <p className="text-slate-400">{errorMsg}</p>
            <button
              onClick={() => router.push('/')}
              className="mt-6 rounded-lg bg-orange-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-orange-600"
            >
              Intentar de nuevo
            </button>
          </div>
        )}

        {state === 'success' && data && (
          <>
            {/* Meta info */}
            <div className="mb-6 flex flex-wrap gap-4 text-sm text-slate-400">
              <span>
                Generado:{' '}
                <span className="text-slate-200">
                  {new Date(data.generated_at).toLocaleString('es-EC', {
                    dateStyle: 'medium',
                    timeStyle: 'short',
                  })}
                </span>
              </span>
              <span>
                Fuentes:{' '}
                <span className="text-slate-200">
                  {data.successful_sources}/{data.total_sources}
                </span>
              </span>
            </div>

            <ResultsDashboard results={data.results} isLoading={false} />
          </>
        )}
      </div>
    </div>
  );
}
