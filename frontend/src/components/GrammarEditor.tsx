import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  BookOpen, CheckCircle, XCircle, Loader2, AlertCircle, Terminal,
  Hash, ArrowRight,
} from 'lucide-react';
import { ErrorPanel } from './ErrorPanel';
import type { ValidationResult } from '../types';

const SYNTAX_HINT = `Example format:
E -> E + T | T
T -> T * F | F
F -> ( E ) | id`;

interface GrammarEditorProps {
  grammarText: string;
  setGrammarText: (text: string) => void;
  startSymbol: string;
  setStartSymbol: (s: string) => void;
  validationResult: ValidationResult | null;
  loading: { validate: boolean };
  errors: { validate: string | null };
  validate: () => void;
}

export function GrammarEditor({
  grammarText,
  setGrammarText,
  startSymbol,
  setStartSymbol,
  validationResult,
  loading,
  errors,
  validate,
}: GrammarEditorProps) {
  const [showHint, setShowHint] = useState(false);

  const isValid = validationResult?.success;
  const hasErrors = validationResult && !validationResult.success;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      validate();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-5 max-w-5xl mx-auto"
    >
      {/* Title */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BookOpen size={20} className="text-blue-400" />
          <h2 className="text-xl font-semibold text-white">Grammar Workspace</h2>
        </div>
        <button
          onClick={() => setShowHint((prev) => !prev)}
          className="text-xs text-gray-500 hover:text-gray-300 transition-colors flex items-center gap-1"
        >
          <AlertCircle size={13} />
          {showHint ? 'Hide hint' : 'Show syntax hint'}
        </button>
      </div>

      {/* Syntax hint */}
      {showHint && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="card-sm border-blue-800/50 bg-blue-950/30"
        >
          <p className="text-xs font-semibold text-blue-400 mb-1 flex items-center gap-1">
            <Terminal size={12} /> Syntax Hint
          </p>
          <pre className="text-xs font-mono text-blue-200/70 whitespace-pre-wrap">{SYNTAX_HINT}</pre>
          <p className="text-xs text-gray-500 mt-2">
            Use <span className="font-mono text-cyan-400">eps</span> or{' '}
            <span className="font-mono text-cyan-400">ε</span> for epsilon productions.
            Press <span className="font-mono text-cyan-400">Ctrl+Enter</span> to validate.
          </p>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Editor */}
        <div className="lg:col-span-2 space-y-3">
          <div className="space-y-1.5">
            <label className="label-text flex items-center gap-1.5">
              <Hash size={12} />
              Grammar Rules
            </label>
            <div className="relative">
              {/* Line numbers pseudo-element area */}
              <div className="absolute left-0 top-0 bottom-0 w-10 bg-gray-900 border-r border-gray-700 rounded-l-lg flex flex-col pt-3 overflow-hidden pointer-events-none">
                {grammarText.split('\n').map((_, idx) => (
                  <span key={idx} className="text-right pr-2 text-xs text-gray-600 font-mono leading-6">
                    {idx + 1}
                  </span>
                ))}
              </div>

              <textarea
                value={grammarText}
                onChange={(e) => setGrammarText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={`E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id`}
                spellCheck={false}
                rows={Math.max(8, grammarText.split('\n').length + 1)}
                className="w-full bg-gray-900 border border-gray-700 rounded-lg text-cyan-200 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/50 placeholder-gray-600 pl-12 pr-4 pt-3 pb-3 resize-none leading-6 transition-all"
                style={{ minHeight: 200 }}
              />

              {/* Status corner badge */}
              <div className="absolute top-2 right-2">
                {loading.validate && (
                  <Loader2 size={14} className="animate-spin text-blue-400" />
                )}
                {!loading.validate && isValid && (
                  <CheckCircle size={14} className="text-green-400" />
                )}
                {!loading.validate && hasErrors && (
                  <XCircle size={14} className="text-red-400" />
                )}
              </div>
            </div>
          </div>

          {/* Start symbol override */}
          <div className="flex items-center gap-3">
            <div className="flex-1">
              <label className="label-text flex items-center gap-1.5 mb-1">
                <ArrowRight size={12} />
                Start Symbol (optional — auto-detected)
              </label>
              <input
                type="text"
                value={startSymbol}
                onChange={(e) => setStartSymbol(e.target.value)}
                placeholder="e.g. E"
                className="input-field max-w-xs"
              />
            </div>
          </div>

          {/* Validate button */}
          <button
            onClick={validate}
            disabled={loading.validate || !grammarText.trim()}
            className="btn-primary"
          >
            {loading.validate ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <CheckCircle size={16} />
            )}
            {loading.validate ? 'Validating…' : 'Validate Grammar'}
          </button>
        </div>

        {/* Info panel */}
        <div className="space-y-3">
          {/* Validation status */}
          {validationResult && (
            <motion.div
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              className={`card ${
                isValid
                  ? 'border-green-700/50 bg-green-900/10'
                  : 'border-red-700/50 bg-red-900/10'
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                {isValid ? (
                  <CheckCircle size={16} className="text-green-400" />
                ) : (
                  <XCircle size={16} className="text-red-400" />
                )}
                <span className={`text-sm font-semibold ${isValid ? 'text-green-300' : 'text-red-300'}`}>
                  {isValid ? 'Grammar is Valid' : 'Invalid Grammar'}
                </span>
              </div>

              {isValid && validationResult.grammar && (
                <div className="space-y-2">
                  <InfoRow label="Start Symbol" value={validationResult.grammar.start_symbol} />
                  <InfoRow
                    label="Nonterminals"
                    value={validationResult.grammar.nonterminals.join(', ')}
                  />
                  <InfoRow
                    label="Terminals"
                    value={validationResult.grammar.terminals.join(', ')}
                  />
                  <InfoRow
                    label="Productions"
                    value={String(Object.values(validationResult.grammar.productions).flat().length)}
                  />
                </div>
              )}
            </motion.div>
          )}

          {/* Error list */}
          {hasErrors && validationResult.errors && validationResult.errors.length > 0 && (
            <ErrorPanel errors={validationResult.errors} title="Validation Errors" />
          )}

          {errors.validate && (
            <ErrorPanel errors={[errors.validate]} title="Error" />
          )}

          {/* Tips */}
          {!validationResult && (
            <div className="card border-gray-800/50">
              <p className="text-sm font-medium text-gray-400 mb-3">Quick Tips</p>
              <ul className="space-y-2">
                {[
                  'One production rule per line',
                  'Use | to separate alternatives',
                  'Use eps or ε for empty productions',
                  'Nonterminals are uppercase, terminals lowercase',
                  'Press Ctrl+Enter to validate quickly',
                ].map((tip, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-xs text-gray-500">
                    <span className="text-blue-500 mt-0.5">•</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-gray-500 mb-0.5">{label}</p>
      <p className="text-sm font-mono text-cyan-300 break-all">{value || '—'}</p>
    </div>
  );
}
