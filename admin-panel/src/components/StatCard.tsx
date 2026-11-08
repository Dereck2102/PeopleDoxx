interface StatCardProps {
  icon?: string;
  value: number | string;
  label: string;
  trend?: string;
}

export default function StatCard({ icon, value, label, trend }: StatCardProps) {
  return (
    <div className="rounded-xl bg-slate-800 p-6 shadow-lg flex flex-col gap-2">
      <div className="flex items-center justify-between">
        {icon && (
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 bg-slate-700/50 px-2 py-0.5 rounded">
            {icon}
          </span>
        )}
        {trend && (
          <span className="text-xs font-medium text-emerald-400 bg-emerald-400/10 rounded-full px-2 py-0.5">
            {trend}
          </span>
        )}
      </div>
      <p className="text-3xl font-bold text-white mt-1">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </p>
      <p className="text-sm text-slate-400">{label}</p>
    </div>
  );
}
