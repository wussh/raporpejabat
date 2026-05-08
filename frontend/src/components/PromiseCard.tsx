import { CheckCircle2, CircleDashed, XCircle, AlertCircle } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface PromiseProps {
  id: string;
  promise: string;
  category: string;
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED' | 'STALLED' | 'CONTRADICTED';
  analysis?: string;
}

const statusConfig = {
  NOT_STARTED: { icon: CircleDashed, color: 'text-slate-400', label: 'Belum Dimulai', bg: 'bg-slate-50' },
  IN_PROGRESS: { icon: AlertCircle, color: 'text-blue-500', label: 'Progres', bg: 'bg-blue-50' },
  COMPLETED: { icon: CheckCircle2, color: 'text-green-500', label: 'Terwujud', bg: 'bg-green-50' },
  STALLED: { icon: AlertCircle, color: 'text-orange-500', label: 'Mangkrak', bg: 'bg-orange-50' },
  CONTRADICTED: { icon: XCircle, color: 'text-red-500', label: 'Bertentangan', bg: 'bg-red-50' },
};

export default function PromiseCard({ promise, category, status, analysis }: PromiseProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <div className={cn("p-4 rounded-lg border border-slate-200 shadow-sm transition-all hover:shadow-md", config.bg)}>
      <div className="flex justify-between items-start mb-2">
        <span className="text-xs font-bold px-2 py-1 rounded bg-white border border-slate-200 uppercase text-slate-500">
          {category}
        </span>
        <div className={cn("flex items-center gap-1 text-xs font-semibold", config.color)}>
          <Icon size={14} />
          {config.label}
        </div>
      </div>
      <p className="text-sm font-medium text-slate-800 mb-2">{promise}</p>
      {analysis && (
        <p className="text-xs text-slate-500 italic border-t border-slate-100 pt-2 mt-2">
          {analysis}
        </p>
      )}
    </div>
  );
}
