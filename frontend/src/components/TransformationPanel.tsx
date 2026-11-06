import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft, GitBranch, Play, CheckCircle, XCircle, AlertTriangle,
  ChevronDown, Loader2, ArrowRight, GitMerge,
} from 'lucide-react';
import { ErrorPanel } from './ErrorPanel';
import type { TransformResult } from '../types';

interface TransformationPanelProps {
  type: 'left-recursion' | 'left-factoring';
  grammarText: string;
  result: TransformResult | null;
  loading: boolean;
  error: string | null;
  onRun: () => void;
  onUseTransformed: (grammar: string) => void;
  isGrammarValid: boolean;
}

export function TransformationPanel({
  type,
  grammarText,
  result,
  loading,
  error,
  onRun,
  onUseTransformed,
  isGrammarValid,
}: TransformationPanelProps) {
  const [openSteps, setOpenSteps] = useState<Set<number>>(new Set());

  const isLR = type === 'left-recursion';
  const Icon = isLR ? ArrowLeft : GitBranch;
  const title = isLR ? 'Left Recursion Elimination' : 'Left Factoring';

  const toggleStep = (step: number) => {
    setOpenSteps((prev) => {
      const next = new Set(prev);
      if (next.has(step)) next.delete(step);
      else next.add(step);
      return next;
    });
  };

  const hasIssue = result ? (isLR ? result.has_left_recursion : result.needs_factoring) : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-5 max-w-5xl mx-auto"
    >
      {/* Title */}
      <div className="flex items-center gap-2">
        <Icon size={20} className={isLR ? 'text-cyan-400' : 'text-violet-400'} />
        <h2 className="text-xl font-semibold text-white">{title}</h2>
      </div>

      {/* Grammar preview */}
      <div className="card">
        <p className="label-text mb-2 flex items-center gap-1.5">
          <GitMerge size={13} />
          Current Grammar
        </p>
        <pre className="font-mono text-sm text-cyan-200 whitespace-pre-wrap bg-gray-950 rounded-lg p-3 border border-gray-800">
          {grammarText || 'No grammar entered yet — go to Grammar Workspace first.'}
        </pre>
      </div>

      {/* Action */}
      <div className="flex items-center gap-3 flex-wrap">
        <button
          onClick={onRun}
          disabled={loading || !grammarText.trim()}
          className="btn-primary"
        >
          {loading ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Play size={16} />
          )}
          {loading ? 'Processing…' : `Run ${title}`}
        </button>

        {!isGrammarValid && grammarText && (
          <p className="text-xs text-amber-400 flex items-center gap-1">
            <AlertTriangle size={13} />
            Validate grammar first for best results
          </p>
        )}
      </div>

      {/* Error */}
      {error && <ErrorPanel errors={[error]} title={`${title} Error`} />}

      {/* Results */}
      {result && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="space-y-5"
        >
          {/* Status badge */}
          <div className="flex items-center gap-3 flex-wrap">
            {hasIssue !== null && (
              <div
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border text-sm font-medium ${
                  hasIssue
                    ? 'border-amber-600/50 bg-amber-900/20 text-amber-300'
                    : 'border-green-600/50 bg-green-900/20 text-green-300'
                }`}
              >
                {hasIssue ? (
                  <AlertTriangle size={15} />
                ) : (
                  <CheckCircle size={15} />
                )}
                {isLR
                  ? hasIssue
                    ? 'Has Left Recursion'
                    : 'No Left Recursion'
                  : hasIssue
                    ? 'Needs Left Factoring'
                    : 'Already Factored'}
              </div>
            )}
            {result.recursive_nonterminals && result.recursive_nonterminals.length > 0 && (
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-xs text-gray-500">Recursive:</span>
                {result.recursive_nonterminals.map((nt) => (
                  <span key={nt} className="badge-amber">{nt}</span>
                ))}
              </div>
            )}
          </div>

          {/* Warnings */}
          {result.warnings && result.warnings.length > 0 && (
            <div className="rounded-xl border border-amber-700/40 bg-amber-900/10 p-4">
              <p className="text-sm font-semibold text-amber-300 flex items-center gap-2 mb-2">
                <AlertTriangle size={15} /> Warnings
              </p>
              <ul className="space-y-1">
                {result.warnings.map((w, i) => (
                  <li key={i} className="text-sm text-amber-200/70 flex items-start gap-2">
                    <span className="text-amber-500 mt-0.5">•</span>
                    <span>{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Steps accordion */}
          {result.steps && result.steps.length > 0 && (
            <div className="space-y-2">
              <p className="section-title text-base">
                Step-by-Step Transformation
              </p>
              {result.steps.map((step) => {
                const isOpen = openSteps.has(step.step);
                return (
                  <div
                    key={step.step}
                    className="rounded-xl border border-gray-800 bg-gray-900 overflow-hidden"
                  >
                    <button
                      onClick={() => toggleStep(step.step)}
                      className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-800/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className="w-6 h-6 rounded-full bg-blue-900/60 border border-blue-600/50 text-blue-300 text-xs font-bold flex items-center justify-center flex-shrink-0">
                          {step.step}
                        </span>
                        <span className="text-sm text-gray-200">{step.description}</span>
                      </div>
                      <ChevronDown
                        size={16}
                        className={`text-gray-500 transition-transform flex-shrink-0 ${isOpen ? 'rotate-180' : ''}`}
                      />
                    </button>
                    <AnimatePresence>
                      {isOpen && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.2 }}
                          className="overflow-hidden"
                        >
                          <div className="px-4 pb-4 pt-1 border-t border-gray-800">
                            <pre className="font-mono text-sm text-cyan-200 bg-gray-950 rounded-lg p-3 border border-gray-800 whitespace-pre-wrap">
                              {step.grammar_state}
                            </pre>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                );
              })}
            </div>
          )}

          {/* Side-by-side comparison */}
          <div className="space-y-2">
            <p className="section-title text-base">Result Comparison</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <GrammarBox title="Original Grammar" grammar={result.original_grammar} color="gray" />
              <GrammarBox
                title="Transformed Grammar"
                grammar={result.transformed_grammar}
                color="blue"
                status={result.success ? 'success' : 'error'}
              />
            </div>
          </div>

          {/* Use transformed button */}
          {result.success && result.transformed_grammar && (
            <div className="flex items-center gap-3">
              <button
                onClick={() => onUseTransformed(result.transformed_grammar)}
                className="btn-success"
              >
                <ArrowRight size={16} />
                Use Transformed Grammar
              </button>
              <p className="text-xs text-gray-500">
                This will update the active grammar for FIRST/FOLLOW, parsing table, and simulator.
              </p>
            </div>
          )}
        </motion.div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div className="empty-state">
          <Icon size={40} className="text-gray-700 mb-3" />
          <p className="text-gray-500 text-sm">
            Click the button above to run {title.toLowerCase()}.
          </p>
        </div>
      )}
    </motion.div>
  );
}

function GrammarBox({
  title,
  grammar,
  color,
  status,
}: {
  title: string;
  grammar: string;
  color: 'gray' | 'blue';
  status?: 'success' | 'error';
}) {
  return (
    <div
      className={`rounded-xl border p-4 ${
        color === 'blue'
          ? status === 'success'
            ? 'border-blue-700/50 bg-blue-950/20'
            : 'border-red-700/50 bg-red-950/20'
          : 'border-gray-700 bg-gray-900'
      }`}
    >
      <div className="flex items-center gap-2 mb-2">
        {status === 'success' && <CheckCircle size={14} className="text-green-400" />}
        {status === 'error' && <XCircle size={14} className="text-red-400" />}
        <p className="text-xs font-semibold text-gray-400">{title}</p>
      </div>
      <pre className="font-mono text-sm text-cyan-200 whitespace-pre-wrap bg-gray-950 rounded-lg p-3 border border-gray-800">
        {grammar || '—'}
      </pre>
    </div>
  );
}
