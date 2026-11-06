import { useState } from 'react';
import { motion } from 'framer-motion';
import { Calculator, Play, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import { ErrorPanel } from './ErrorPanel';
import type { FirstFollowResult } from '../types';

interface FirstFollowPanelProps {
  grammarText: string;
  result: FirstFollowResult | null;
  loading: boolean;
  error: string | null;
  onRun: () => void;
  isGrammarValid: boolean;
}

export function FirstFollowPanel({
  grammarText,
  result,
  loading,
  error,
  onRun,
  isGrammarValid,
}: FirstFollowPanelProps) {
  const [showSteps, setShowSteps] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-5 max-w-5xl mx-auto"
    >
      {/* Title */}
      <div className="flex items-center gap-2">
        <Calculator size={20} className="text-emerald-400" />
        <h2 className="text-xl font-semibold text-white">FIRST &amp; FOLLOW Sets</h2>
      </div>

      {/* Current grammar */}
      <div className="card">
        <p className="label-text mb-2">Current Grammar</p>
        <pre className="font-mono text-sm text-cyan-200 bg-gray-950 rounded-lg p-3 border border-gray-800 whitespace-pre-wrap">
          {grammarText || 'No grammar loaded.'}
        </pre>
      </div>

      {/* Run button */}
      <div className="flex items-center gap-3">
        <button
          onClick={onRun}
          disabled={loading || !grammarText.trim()}
          className="btn-primary"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
          {loading ? 'Computing…' : 'Compute FIRST & FOLLOW'}
        </button>
        {!isGrammarValid && grammarText && (
          <p className="text-xs text-amber-400">Validate grammar first for accurate results</p>
        )}
      </div>

      {error && <ErrorPanel errors={[error]} title="Computation Error" />}

      {result && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
          {/* Summary badges */}
          {result.nullable && result.nullable.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap">
              <span className="label-text">Nullable:</span>
              {result.nullable.map((nt) => (
                <span key={nt} className="badge-violet">{nt}</span>
              ))}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {/* FIRST sets */}
            <SetTable
              title="FIRST Sets"
              sets={result.first_sets}
              nullable={result.nullable}
              accentColor="blue"
            />

            {/* FOLLOW sets */}
            <SetTable
              title="FOLLOW Sets"
              sets={result.follow_sets}
              nullable={result.nullable}
              accentColor="cyan"
            />
          </div>

          {/* Steps toggle */}
          {result.steps && result.steps.length > 0 && (
            <div className="card">
              <button
                onClick={() => setShowSteps((p) => !p)}
                className="w-full flex items-center justify-between text-sm text-gray-300 hover:text-white transition-colors"
              >
                <span className="font-medium">Computation Steps ({result.steps.length})</span>
                {showSteps ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </button>

              {showSteps && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-3 space-y-2 max-h-64 overflow-y-auto scrollbar-thin"
                >
                  {result.steps.map((step, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-sm">
                      <span className="w-5 h-5 rounded-full bg-gray-800 border border-gray-700 text-gray-400 text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
                        {idx + 1}
                      </span>
                      <div>
                        <p className="text-gray-300">{step.description}</p>
                        {step.detail && (
                          <p className="text-xs text-gray-500 mt-0.5 font-mono">{step.detail}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </motion.div>
              )}
            </div>
          )}
        </motion.div>
      )}

      {!result && !loading && !error && (
        <div className="empty-state">
          <Calculator size={40} className="text-gray-700 mb-3" />
          <p className="text-sm text-gray-500">
            Click "Compute FIRST &amp; FOLLOW" to calculate the sets.
          </p>
        </div>
      )}
    </motion.div>
  );
}

function SetTable({
  title,
  sets,
  nullable,
  accentColor,
}: {
  title: string;
  sets: Record<string, string[]>;
  nullable: string[];
  accentColor: 'blue' | 'cyan';
}) {
  const entries = Object.entries(sets);
  const accent = accentColor === 'blue' ? 'text-blue-400' : 'text-cyan-400';
  const headerBg = accentColor === 'blue' ? 'bg-blue-950/40' : 'bg-cyan-950/40';
  const headerText = accentColor === 'blue' ? 'text-blue-300' : 'text-cyan-300';
  const cellBg = accentColor === 'blue' ? 'bg-blue-900/30' : 'bg-cyan-900/30';
  const cellBorder = accentColor === 'blue' ? 'border-blue-700/30' : 'border-cyan-700/30';

  return (
    <div className="card overflow-hidden p-0">
      <div className={`px-4 py-3 ${headerBg} border-b border-gray-800`}>
        <p className={`text-sm font-semibold ${headerText}`}>{title}</p>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800">
              <th className="text-left px-4 py-2 text-gray-500 font-medium">Nonterminal</th>
              <th className="text-left px-4 py-2 text-gray-500 font-medium">Set</th>
            </tr>
          </thead>
          <tbody>
            {entries.length === 0 ? (
              <tr>
                <td colSpan={2} className="px-4 py-6 text-center text-gray-600 text-xs">
                  No data
                </td>
              </tr>
            ) : (
              entries.map(([nt, symbols]) => {
                const isNullable = nullable.includes(nt);
                return (
                  <tr key={nt} className="border-b border-gray-800/50 hover:bg-gray-800/30">
                    <td className="px-4 py-2.5">
                      <div className="flex items-center gap-2">
                        <span className={`font-mono font-semibold ${accent}`}>{nt}</span>
                        {isNullable && (
                          <span className="badge-violet text-xs">nullable</span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-2.5">
                      <div className="flex flex-wrap gap-1">
                        {symbols.length === 0 ? (
                          <span className="text-gray-600 text-xs">∅</span>
                        ) : (
                          symbols.map((sym, i) => (
                            <span
                              key={i}
                              className={`px-2 py-0.5 rounded text-xs font-mono border ${cellBg} ${cellBorder} ${accent}`}
                            >
                              {sym === 'eps' || sym === 'ε' ? 'ε' : sym}
                            </span>
                          ))
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
