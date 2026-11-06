import { AlertCircle } from 'lucide-react';

interface ErrorPanelProps {
  errors: string[];
  title?: string;
}

export function ErrorPanel({ errors, title = 'Error' }: ErrorPanelProps) {
  if (!errors || errors.length === 0) return null;

  return (
    <div className="rounded-xl border border-red-700/50 bg-red-900/20 p-4">
      <div className="flex items-start gap-3">
        <AlertCircle size={18} className="text-red-400 mt-0.5 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-red-300 mb-1">{title}</p>
          {errors.length === 1 ? (
            <p className="text-sm text-red-200/80">{errors[0]}</p>
          ) : (
            <ul className="space-y-1">
              {errors.map((err, idx) => (
                <li key={idx} className="text-sm text-red-200/80 flex items-start gap-1.5">
                  <span className="text-red-500 flex-shrink-0 mt-0.5">•</span>
                  <span>{err}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
