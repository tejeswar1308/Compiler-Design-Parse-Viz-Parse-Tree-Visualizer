import { motion } from 'framer-motion';
import { Table, Play, Loader2, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { ErrorPanel } from './ErrorPanel';
import type { ParsingTableResult } from '../types';

interface ParsingTableProps {
  grammarText: string;
  result: ParsingTableResult | null;
  loading: boolean;
  error: string | null;
  onRun: () => void;
  isGrammarValid: boolean;
}

export function ParsingTable({
  grammarText,
  result,
  loading,
  error,
  onRun,
  isGrammarValid,
}: ParsingTableProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-5 max-w-6xl mx-auto"
    >
      {/* Title */}
      <div className="flex items-center gap-2">
        <Table size={20} className="text-amber-400" />
        <h2 className="text-xl font-semibold text-white">LL(1) Parsing Table</h2>
      </div>

      {/* Grammar */}
      <div className="card">
        <p className="label-text mb-2">Current Grammar</p>
        <pre className="font-mono text-sm text-cyan-200 bg-gray-950 rounded-lg p-3 border border-gray-800 whitespace-pre-wrap">
          {grammarText || 'No grammar loaded.'}
        </pre>
      </div>

      {/* Action */}
      <div className="flex items-center gap-3">
        <button
          onClick={onRun}
          disabled={loading || !grammarText.trim()}
          className="btn-primary"
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
          {loading ? 'Building…' : 'Build Parsing Table'}
        </button>
        {!isGrammarValid && grammarText && (
          <p className="text-xs text-amber-400">Validate grammar first</p>
        )}
      </div>

      {error && <ErrorPanel errors={[error]} title="Table Construction Error" />}

      {result && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
          {/* LL(1) status */}
          <div className="flex items-center gap-3">
            <div
              className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-semibold ${
                result.is_ll1
                  ? 'border-green-600/50 bg-green-900/20 text-green-300'
                  : 'border-red-600/50 bg-red-900/20 text-red-300'
              }`}
            >
              {result.is_ll1 ? <CheckCircle size={16} /> : <XCircle size={16} />}
              {result.is_ll1 ? 'LL(1) Grammar' : 'Not LL(1) — Has Conflicts'}
            </div>
            <span className="text-xs text-gray-500">
              {result.nonterminals.length} nonterminals × {result.terminals.length} terminals
            </span>
          </div>

          {/* Table */}
          <div className="card p-0 overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-800 bg-amber-950/20">
              <p className="text-sm font-semibold text-amber-300">Parsing Table M[A, a]</p>
            </div>
            <div className="overflow-auto max-h-96 scrollbar-thin">
              <table className="text-xs min-w-max">
                <thead className="sticky top-0 z-10 bg-gray-900">
                  <tr>
                    <th className="px-3 py-2.5 text-left text-gray-500 font-semibold border-b border-r border-gray-700 bg-gray-900 min-w-[80px]">
                      NT \ T
                    </th>
                    {result.terminals.map((t) => (
                      <th
                        key={t}
                        className="px-3 py-2.5 text-center text-cyan-400 font-mono border-b border-gray-700 min-w-[120px]"
                      >
                        {t}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.nonterminals.map((nt) => (
                    <tr key={nt} className="border-b border-gray-800/50">
                      <td className="px-3 py-2 text-blue-400 font-mono font-semibold border-r border-gray-700 bg-gray-900/50">
                        {nt}
                      </td>
                      {result.terminals.map((t) => {
                        const cell = result.table[nt]?.[t];
                        const isConflict = result.conflicts.some(
                          (c) => c.nonterminal === nt && c.terminal === t
                        );
                        return (
                          <td key={t} className="px-3 py-2 text-center">
                            {cell ? (
                              <span
                                className={`inline-block font-mono rounded px-1.5 py-0.5 text-xs ${
                                  isConflict
                                    ? 'bg-red-900/50 text-red-300 border border-red-700/50'
                                    : 'bg-blue-900/30 text-blue-200 border border-blue-700/30'
                                }`}
                              >
                                {cell}
                              </span>
                            ) : (
                              <span className="text-gray-700">—</span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Conflicts */}
          {result.conflicts && result.conflicts.length > 0 && (
            <div className="space-y-3">
              <p className="section-title text-base text-red-400">
                <AlertCircle size={18} className="text-red-400" />
                Conflicts ({result.conflicts.length})
              </p>
              {result.conflicts.map((conflict, idx) => (
                <div key={idx} className="rounded-xl border border-red-700/40 bg-red-900/10 p-4">
                  <p className="text-sm text-red-200 font-semibold mb-1">
                    M[{conflict.nonterminal}, {conflict.terminal}]
                  </p>
                  <p className="text-xs text-gray-400 mb-2">Multiple productions compete:</p>
                  <div className="flex flex-wrap gap-2">
                    {conflict.productions.map((prod, i) => (
                      <span
                        key={i}
                        className="font-mono text-xs bg-red-950/40 border border-red-700/30 text-red-200 px-2 py-1 rounded"
                      >
                        {prod}
                      </span>
                    ))}
                  </div>
                </div>
              ))}

              <div className="rounded-xl border border-amber-700/40 bg-amber-900/10 p-4">
                <p className="text-sm font-semibold text-amber-300 mb-1">
                  Why conflicts occur
                </p>
                <p className="text-sm text-gray-400">
                  LL(1) conflicts arise when a nonterminal has ambiguous alternatives —
                  two or more productions that can start with the same terminal, or when
                  FIRST sets overlap with FOLLOW sets in nullable productions. Try eliminating
                  left recursion and applying left factoring to resolve them.
                </p>
              </div>
            </div>
          )}
        </motion.div>
      )}

      {!result && !loading && !error && (
        <div className="empty-state">
          <Table size={40} className="text-gray-700 mb-3" />
          <p className="text-sm text-gray-500">Build the parsing table to see it here.</p>
        </div>
      )}
    </motion.div>
  );
}
