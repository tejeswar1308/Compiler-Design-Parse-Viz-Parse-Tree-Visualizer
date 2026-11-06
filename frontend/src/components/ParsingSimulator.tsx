import { useState, useEffect, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  Play as PlayIcon, SkipBack, SkipForward, ChevronLeft, ChevronRight,
  Loader2, CheckCircle, XCircle, Pause,
} from 'lucide-react';
import { ErrorPanel } from './ErrorPanel';
import type { ParseResult, ParseStep } from '../types';

interface ParsingSimulatorProps {
  grammarText: string;
  result: ParseResult | null;
  loading: boolean;
  error: string | null;
  onParse: (input: string) => void;
  isGrammarValid: boolean;
}

export function ParsingSimulator({
  grammarText,
  result,
  loading,
  error,
  onParse,
  isGrammarValid,
}: ParsingSimulatorProps) {
  const [inputString, setInputString] = useState('');
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const playInterval = useRef<ReturnType<typeof setInterval> | null>(null);
  const tableRef = useRef<HTMLDivElement>(null);

  const steps = result?.steps ?? [];
  const maxStep = steps.length > 0 ? steps.length - 1 : 0;

  useEffect(() => {
    if (result) setCurrentStep(0);
  }, [result]);

  useEffect(() => {
    if (isPlaying) {
      playInterval.current = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= maxStep) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 900);
    } else {
      if (playInterval.current) clearInterval(playInterval.current);
    }
    return () => {
      if (playInterval.current) clearInterval(playInterval.current);
    };
  }, [isPlaying, maxStep]);

  // Scroll active row into view
  useEffect(() => {
    const el = tableRef.current?.querySelector(`[data-step="${currentStep}"]`);
    el?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  }, [currentStep]);

  const handleParse = () => {
    if (!inputString.trim() && inputString !== '') {
      onParse(inputString);
    } else {
      onParse(inputString.trim());
    }
    setIsPlaying(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleParse();
  };

  const goFirst = useCallback(() => { setCurrentStep(0); setIsPlaying(false); }, []);
  const goPrev = useCallback(() => setCurrentStep((p) => Math.max(0, p - 1)), []);
  const goNext = useCallback(() => setCurrentStep((p) => Math.min(maxStep, p + 1)), [maxStep]);
  const goLast = useCallback(() => { setCurrentStep(maxStep); setIsPlaying(false); }, [maxStep]);
  const togglePlay = useCallback(() => setIsPlaying((p) => !p), []);

  const getActionColor = (action: string) => {
    if (action.toLowerCase().includes('match') || action.toLowerCase().includes('accept')) return 'text-green-400';
    if (action.toLowerCase().includes('error') || action.toLowerCase().includes('reject')) return 'text-red-400';
    if (action.toLowerCase().includes('predict') || action.toLowerCase().includes('expand') || action.toLowerCase().includes('replace')) return 'text-blue-400';
    return 'text-gray-300';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-5 max-w-5xl mx-auto"
    >
      {/* Title */}
      <div className="flex items-center gap-2">
        <PlayIcon size={20} className="text-orange-400" />
        <h2 className="text-xl font-semibold text-white">Parsing Simulator</h2>
      </div>

      {/* Grammar + Input */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="card">
          <p className="label-text mb-2">Active Grammar</p>
          <pre className="font-mono text-xs text-cyan-200 bg-gray-950 rounded p-2 border border-gray-800 whitespace-pre-wrap max-h-32 overflow-y-auto scrollbar-thin">
            {grammarText || 'No grammar loaded.'}
          </pre>
        </div>

        <div className="card space-y-3">
          <p className="label-text">Input String</p>
          <input
            type="text"
            value={inputString}
            onChange={(e) => setInputString(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g. id + id * id"
            className="input-field"
          />
          <div className="flex items-center gap-2">
            <button
              onClick={handleParse}
              disabled={loading || !grammarText.trim()}
              className="btn-primary flex-1"
            >
              {loading ? <Loader2 size={15} className="animate-spin" /> : <PlayIcon size={15} />}
              {loading ? 'Parsing…' : 'Parse'}
            </button>
            {!isGrammarValid && grammarText && (
              <span className="text-xs text-amber-400">Validate first</span>
            )}
          </div>
        </div>
      </div>

      {error && <ErrorPanel errors={[error]} title="Parsing Error" />}

      {result && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
          {/* Result badge */}
          <div className={`flex items-center gap-3 p-3 rounded-xl border ${
            result.accepted
              ? 'border-green-600/50 bg-green-900/20'
              : 'border-red-600/50 bg-red-900/20'
          }`}>
            {result.accepted ? (
              <CheckCircle size={20} className="text-green-400" />
            ) : (
              <XCircle size={20} className="text-red-400" />
            )}
            <div>
              <p className={`font-semibold ${result.accepted ? 'text-green-300' : 'text-red-300'}`}>
                {result.accepted ? 'Accepted ✓' : 'Rejected ✗'}
              </p>
              {result.error_message && (
                <p className="text-xs text-red-200/70 mt-0.5">{result.error_message}</p>
              )}
            </div>
            <div className="ml-auto text-right">
              <p className="text-xs text-gray-500">Steps: {steps.length}</p>
              {result.productions_used && result.productions_used.length > 0 && (
                <p className="text-xs text-gray-500">Productions used: {result.productions_used.length}</p>
              )}
            </div>
          </div>

          {/* Step trace table */}
          {steps.length > 0 && (
            <div className="card p-0 overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-800 bg-orange-950/20">
                <p className="text-sm font-semibold text-orange-300">
                  Parse Trace — Step {currentStep + 1} of {steps.length}
                </p>
              </div>

              {/* Table */}
              <div ref={tableRef} className="overflow-auto max-h-72 scrollbar-thin">
                <table className="w-full text-xs min-w-max">
                  <thead className="sticky top-0 bg-gray-900 z-10">
                    <tr className="border-b border-gray-700">
                      <th className="px-3 py-2 text-left text-gray-500 font-medium w-12">#</th>
                      <th className="px-3 py-2 text-left text-gray-500 font-medium min-w-[160px]">Stack (top →)</th>
                      <th className="px-3 py-2 text-left text-gray-500 font-medium min-w-[160px]">Remaining Input</th>
                      <th className="px-3 py-2 text-left text-gray-500 font-medium min-w-[200px]">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {steps.map((step: ParseStep, idx) => {
                      const isActive = idx === currentStep;
                      const isError = result.error_step !== undefined && idx === result.error_step;
                      return (
                        <tr
                          key={idx}
                          data-step={idx}
                          onClick={() => { setCurrentStep(idx); setIsPlaying(false); }}
                          className={`border-b border-gray-800/50 cursor-pointer transition-colors ${
                            isActive
                              ? 'bg-blue-900/30 border-l-2 border-l-blue-500'
                              : isError
                                ? 'bg-red-900/20'
                                : 'hover:bg-gray-800/30'
                          }`}
                        >
                          <td className="px-3 py-2 text-gray-600">{step.step}</td>
                          <td className="px-3 py-2 font-mono text-blue-300 max-w-[200px] truncate">
                            {step.stack.join(' ')}
                          </td>
                          <td className="px-3 py-2 font-mono text-cyan-300 max-w-[200px] truncate">
                            {step.remaining_input.length > 0 ? step.remaining_input.join(' ') : ''}
                          </td>
                          <td className={`px-3 py-2 ${getActionColor(step.action)}`}>
                            <span>{step.action}</span>
                            {step.production && (
                              <span className="text-gray-500 ml-1 font-mono">({step.production})</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Playback controls */}
              <div className="px-4 py-3 border-t border-gray-800 bg-gray-900 flex items-center justify-between gap-3">
                <div className="flex items-center gap-1">
                  <ControlBtn onClick={goFirst} title="First step"><SkipBack size={15} /></ControlBtn>
                  <ControlBtn onClick={goPrev} title="Previous" disabled={currentStep === 0}><ChevronLeft size={15} /></ControlBtn>
                  <button
                    onClick={togglePlay}
                    className={`w-8 h-8 rounded-lg flex items-center justify-center transition-colors ${
                      isPlaying
                        ? 'bg-orange-600 hover:bg-orange-500'
                        : 'bg-blue-600 hover:bg-blue-500'
                    } text-white`}
                    title={isPlaying ? 'Pause' : 'Play'}
                  >
                    {isPlaying ? <Pause size={14} /> : <PlayIcon size={14} />}
                  </button>
                  <ControlBtn onClick={goNext} title="Next" disabled={currentStep >= maxStep}><ChevronRight size={15} /></ControlBtn>
                  <ControlBtn onClick={goLast} title="Last step"><SkipForward size={15} /></ControlBtn>
                </div>

                <div className="flex-1 mx-4">
                  <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full transition-all duration-300"
                      style={{ width: `${steps.length > 1 ? (currentStep / (steps.length - 1)) * 100 : 100}%` }}
                    />
                  </div>
                </div>

                <span className="text-xs text-gray-500 font-mono flex-shrink-0">
                  {currentStep + 1} / {steps.length}
                </span>
              </div>
            </div>
          )}

          {/* Current step detail */}
          {steps[currentStep] && (
            <StepDetail step={steps[currentStep]} />
          )}
        </motion.div>
      )}

      {!result && !loading && !error && (
        <div className="empty-state">
          <PlayIcon size={40} className="text-gray-700 mb-3" />
          <p className="text-sm text-gray-500">Enter an input string and click Parse.</p>
        </div>
      )}
    </motion.div>
  );
}

function ControlBtn({
  onClick,
  children,
  disabled,
  title,
}: {
  onClick: () => void;
  children: React.ReactNode;
  disabled?: boolean;
  title?: string;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className="w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
    >
      {children}
    </button>
  );
}

function StepDetail({ step }: { step: ParseStep }) {
  return (
    <motion.div
      key={step.step}
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      className="card border-blue-800/40 bg-blue-950/20"
    >
      <p className="text-xs text-blue-400 font-semibold mb-2">Step {step.step} Detail</p>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
        <div>
          <p className="label-text mb-0.5">Stack</p>
          <p className="font-mono text-blue-300 break-all">{step.stack.join(' ') || '—'}</p>
        </div>
        <div>
          <p className="label-text mb-0.5">Input</p>
          <p className="font-mono text-cyan-300 break-all">{step.remaining_input.join(' ') || 'ε'}</p>
        </div>
        <div>
          <p className="label-text mb-0.5">Action</p>
          <p className="text-gray-200 break-all">{step.action}</p>
        </div>
        {step.production && (
          <div>
            <p className="label-text mb-0.5">Production</p>
            <p className="font-mono text-violet-300 break-all">{step.production}</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}
