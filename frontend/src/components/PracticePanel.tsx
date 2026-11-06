import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  GraduationCap, Play, Loader2, CheckCircle, XCircle,
  ChevronDown, RefreshCw, BarChart2,
} from 'lucide-react';
import { api } from '../services/api';
import type { PracticeQuestion, PracticeCheckResult } from '../types';

const QUESTION_TYPES = [
  { value: 'all', label: 'All Types' },
  { value: 'left_recursion', label: 'Has Left Recursion?' },
  { value: 'first_set', label: 'FIRST Set' },
  { value: 'follow_set', label: 'FOLLOW Set' },
  { value: 'is_ll1', label: 'Is LL(1)?' },
];

interface Score {
  total: number;
  correct: number;
}

export function PracticePanel() {
  const [questionType, setQuestionType] = useState('all');
  const [question, setQuestion] = useState<PracticeQuestion | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [result, setResult] = useState<PracticeCheckResult | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [score, setScore] = useState<Score>({ total: 0, correct: 0 });
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateQuestion = async () => {
    setLoading(true);
    setError(null);
    setSelected(null);
    setResult(null);
    setShowExplanation(false);
    try {
      const q = await api.generatePracticeQuestion(questionType === 'all' ? undefined : questionType);
      setQuestion(q);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate question');
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!question || !selected) return;
    setChecking(true);
    try {
      const res = await api.checkPracticeAnswer(question.id, selected, question);
      setResult(res);
      setScore((prev) => ({
        total: prev.total + 1,
        correct: prev.correct + (res.correct ? 1 : 0),
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to check answer');
    } finally {
      setChecking(false);
    }
  };

  const accuracy = score.total > 0 ? Math.round((score.correct / score.total) * 100) : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-5 max-w-3xl mx-auto"
    >
      {/* Title + Score */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <GraduationCap size={20} className="text-indigo-400" />
          <h2 className="text-xl font-semibold text-white">Practice Mode</h2>
        </div>

        {/* Score card */}
        <div className="flex items-center gap-3 px-4 py-2 bg-gray-900 border border-gray-800 rounded-xl">
          <BarChart2 size={16} className="text-indigo-400" />
          <div className="flex items-center gap-3 text-sm">
            <ScoreStat label="Questions" value={score.total} />
            <span className="text-gray-700">|</span>
            <ScoreStat label="Correct" value={score.correct} color="text-green-400" />
            <span className="text-gray-700">|</span>
            <ScoreStat
              label="Accuracy"
              value={`${accuracy}%`}
              color={accuracy >= 70 ? 'text-green-400' : accuracy >= 50 ? 'text-amber-400' : 'text-red-400'}
            />
          </div>
          <button
            onClick={() => setScore({ total: 0, correct: 0 })}
            className="text-gray-600 hover:text-gray-400 transition-colors"
            title="Reset score"
          >
            <RefreshCw size={13} />
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-end gap-3 flex-wrap">
        <div className="space-y-1">
          <label className="label-text text-xs">Question Type</label>
          <select
            value={questionType}
            onChange={(e) => setQuestionType(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg text-white text-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {QUESTION_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>

        <button onClick={generateQuestion} disabled={loading} className="btn-primary">
          {loading ? <Loader2 size={15} className="animate-spin" /> : <Play size={15} />}
          {loading ? 'Generating…' : 'Generate Question'}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-red-700/50 bg-red-900/20 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* Question card */}
      <AnimatePresence mode="wait">
        {question && !loading && (
          <motion.div
            key={question.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="space-y-4"
          >
            {/* Question */}
            <div className="card space-y-3">
              <div className="flex items-center gap-2">
                <span className="badge-indigo text-xs" style={{ backgroundColor: 'rgba(99,102,241,0.2)', color: '#a5b4fc', border: '1px solid rgba(99,102,241,0.4)' }}>
                  {question.type.replace(/_/g, ' ')}
                </span>
              </div>

              <p className="text-white font-medium">{question.question}</p>

              {question.grammar && (
                <div className="bg-gray-950 border border-gray-800 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-1 uppercase tracking-wide">Grammar</p>
                  <pre className="font-mono text-sm text-cyan-200 whitespace-pre-wrap">
                    {question.grammar}
                  </pre>
                </div>
              )}
            </div>

            {/* Options */}
            <div className="space-y-2">
              {question.options.map((option, idx) => {
                const isSelected = selected === option;
                const isCorrect = result?.correct_answer === option;
                const isWrong = result && isSelected && !result.correct;

                return (
                  <motion.button
                    key={idx}
                    whileHover={!result ? { scale: 1.01 } : {}}
                    onClick={() => !result && setSelected(option)}
                    disabled={!!result}
                    className={`w-full text-left px-4 py-3 rounded-xl border text-sm font-medium transition-all duration-200 ${
                      result
                        ? isCorrect
                          ? 'border-green-500/60 bg-green-900/20 text-green-200'
                          : isWrong
                            ? 'border-red-500/60 bg-red-900/20 text-red-200'
                            : 'border-gray-700 bg-gray-900 text-gray-500 opacity-50'
                        : isSelected
                          ? 'border-indigo-500/70 bg-indigo-900/30 text-white'
                          : 'border-gray-700 bg-gray-900 text-gray-300 hover:border-gray-600 hover:bg-gray-800'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <span>{option}</span>
                      {result && isCorrect && <CheckCircle size={16} className="text-green-400 flex-shrink-0" />}
                      {result && isWrong && <XCircle size={16} className="text-red-400 flex-shrink-0" />}
                    </div>
                  </motion.button>
                );
              })}
            </div>

            {/* Submit */}
            {!result && (
              <button
                onClick={submitAnswer}
                disabled={!selected || checking}
                className="btn-primary w-full justify-center"
              >
                {checking ? <Loader2 size={15} className="animate-spin" /> : null}
                {checking ? 'Checking…' : 'Submit Answer'}
              </button>
            )}

            {/* Result */}
            {result && (
              <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="space-y-3">
                <div
                  className={`flex items-center gap-3 p-3 rounded-xl border ${
                    result.correct
                      ? 'border-green-600/50 bg-green-900/20'
                      : 'border-red-600/50 bg-red-900/20'
                  }`}
                >
                  {result.correct ? (
                    <CheckCircle size={20} className="text-green-400" />
                  ) : (
                    <XCircle size={20} className="text-red-400" />
                  )}
                  <div>
                    <p className={`font-semibold ${result.correct ? 'text-green-300' : 'text-red-300'}`}>
                      {result.correct ? 'Correct!' : 'Incorrect'}
                    </p>
                    {!result.correct && (
                      <p className="text-sm text-gray-400 mt-0.5">
                        Correct answer: <span className="font-mono text-green-300">{result.correct_answer}</span>
                      </p>
                    )}
                  </div>
                </div>

                {/* Explanation */}
                <div className="card">
                  <button
                    onClick={() => setShowExplanation((p) => !p)}
                    className="w-full flex items-center justify-between text-sm text-gray-300 hover:text-white transition-colors"
                  >
                    <span className="font-medium">Explanation</span>
                    <ChevronDown size={16} className={`transition-transform ${showExplanation ? 'rotate-180' : ''}`} />
                  </button>

                  {showExplanation && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="mt-3 space-y-2"
                    >
                      <p className="text-sm text-gray-300">{result.explanation}</p>
                      {result.step_by_step && result.step_by_step.length > 0 && (
                        <div className="space-y-1 mt-2">
                          {result.step_by_step.map((s, i) => (
                            <div key={i} className="flex items-start gap-2 text-sm">
                              <span className="w-4 h-4 rounded-full bg-indigo-900 border border-indigo-600 text-indigo-300 text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
                                {i + 1}
                              </span>
                              <span className="text-gray-400">{s}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </motion.div>
                  )}
                </div>

                {/* Next question button */}
                <button onClick={generateQuestion} disabled={loading} className="btn-primary w-full justify-center">
                  {loading ? <Loader2 size={15} className="animate-spin" /> : <Play size={15} />}
                  Next Question
                </button>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {!question && !loading && !error && (
        <div className="empty-state">
          <GraduationCap size={48} className="text-gray-700 mb-3" />
          <p className="text-gray-400 font-medium">Ready to practice?</p>
          <p className="text-gray-600 text-sm mt-1">
            Select a question type and click Generate Question to begin.
          </p>
        </div>
      )}
    </motion.div>
  );
}

function ScoreStat({
  label,
  value,
  color = 'text-white',
}: {
  label: string;
  value: string | number;
  color?: string;
}) {
  return (
    <div className="text-center">
      <p className={`font-semibold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  );
}
