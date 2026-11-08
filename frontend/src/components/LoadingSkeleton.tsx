export function LoadingSkeleton() {
  return (
    <div
      className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3"
      aria-busy="true"
      aria-label="Cargando resultados…"
    >
      {Array.from({ length: 6 }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}

function SkeletonCard() {
  return (
    <div
      className="flex flex-col rounded-xl border border-slate-700 bg-slate-800 shadow-lg overflow-hidden"
      aria-hidden="true"
    >
      {/* Header skeleton */}
      <div className="flex items-start justify-between gap-2 border-b border-slate-700 px-5 py-4">
        <div className="flex-1 space-y-2">
          <div className="h-4 w-24 rounded bg-slate-700 animate-pulse" />
          <div className="h-3 w-16 rounded bg-slate-700/60 animate-pulse" />
        </div>
        <div className="flex flex-col items-end gap-1.5">
          <div className="h-5 w-16 rounded-full bg-slate-700 animate-pulse" />
          <div className="h-4 w-12 rounded-full bg-slate-700/60 animate-pulse" />
        </div>
      </div>

      {/* Body skeleton */}
      <div className="flex-1 space-y-3 px-5 py-4">
        {Array.from({ length: 4 }).map((_, j) => (
          <div key={j} className="flex gap-3">
            <div className="h-3 w-24 rounded bg-slate-700/60 animate-pulse shrink-0" />
            <div className="h-3 flex-1 rounded bg-slate-700/40 animate-pulse" />
          </div>
        ))}
      </div>

      {/* Footer skeleton */}
      <div className="border-t border-slate-700/50 px-5 py-2.5">
        <div className="h-3 w-32 rounded bg-slate-700/40 animate-pulse" />
      </div>
    </div>
  );
}
