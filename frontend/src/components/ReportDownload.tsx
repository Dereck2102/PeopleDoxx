'use client';

import { useState, useCallback } from 'react';
import { downloadReport } from '@/lib/api';

interface ReportDownloadProps {
  cedula: string;
}

function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

export function ReportDownload({ cedula }: ReportDownloadProps) {
  const [loadingPdf, setLoadingPdf] = useState(false);
  const [loadingJson, setLoadingJson] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = useCallback(
    async (format: 'pdf' | 'json') => {
      const setLoading = format === 'pdf' ? setLoadingPdf : setLoadingJson;
      setLoading(true);
      setError(null);

      try {
        const blob = await downloadReport(cedula, format);
        const ext = format === 'pdf' ? 'pdf' : 'json';
        triggerDownload(blob, `reporte_${cedula}.${ext}`);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : 'Error al descargar el reporte.';
        setError(message);
      } finally {
        setLoading(false);
      }
    },
    [cedula]
  );

  return (
    <div className="flex flex-col items-end gap-2">
      <div className="flex items-center gap-2">
        {/* PDF button */}
        <button
          onClick={() => handleDownload('pdf')}
          disabled={loadingPdf || loadingJson}
          aria-label="Descargar reporte en formato PDF"
          className="inline-flex items-center gap-2 rounded-lg border border-slate-600 bg-slate-800 px-4 py-2 text-sm font-medium text-slate-200 hover:border-slate-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loadingPdf ? (
            <>
              <Spinner />
              Descargando…
            </>
          ) : (
            <>
              <DownloadIcon />
              PDF
            </>
          )}
        </button>

        {/* JSON button */}
        <button
          onClick={() => handleDownload('json')}
          disabled={loadingPdf || loadingJson}
          aria-label="Descargar reporte en formato JSON"
          className="inline-flex items-center gap-2 rounded-lg border border-slate-600 bg-slate-800 px-4 py-2 text-sm font-medium text-slate-200 hover:border-slate-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loadingJson ? (
            <>
              <Spinner />
              Descargando…
            </>
          ) : (
            <>
              <DownloadIcon />
              JSON
            </>
          )}
        </button>
      </div>

      {error && (
        <p role="alert" className="text-xs text-red-400">
          {error}
        </p>
      )}
    </div>
  );
}

function Spinner() {
  return (
    <svg
      className="h-4 w-4 animate-spin text-orange-400"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v8H4z"
      />
    </svg>
  );
}

function DownloadIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className="h-4 w-4"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
      />
    </svg>
  );
}
