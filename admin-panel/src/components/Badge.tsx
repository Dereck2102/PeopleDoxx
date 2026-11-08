type BadgeVariant = 'success' | 'error' | 'warning' | 'info' | 'neutral';

interface BadgeProps {
  variant: BadgeVariant;
  children: React.ReactNode;
}

const variantClasses: Record<BadgeVariant, string> = {
  success: 'bg-emerald-500/15 text-emerald-400 ring-1 ring-emerald-500/30',
  error: 'bg-red-500/15 text-red-400 ring-1 ring-red-500/30',
  warning: 'bg-amber-500/15 text-amber-400 ring-1 ring-amber-500/30',
  info: 'bg-blue-500/15 text-blue-400 ring-1 ring-blue-500/30',
  neutral: 'bg-slate-700 text-slate-300 ring-1 ring-slate-600',
};

export default function Badge({ variant, children }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${variantClasses[variant]}`}
    >
      {children}
    </span>
  );
}
