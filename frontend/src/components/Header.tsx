import { useState, useEffect } from 'react';
import { Menu, TreePine, RefreshCw, ChevronDown, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import type { ActiveSection, ExampleGrammar } from '../types';

const SECTION_LABELS: Record<ActiveSection, string> = {
  'grammar': 'Grammar Workspace',
  'left-recursion': 'Left Recursion Elimination',
  'left-factoring': 'Left Factoring',
  'first-follow': 'FIRST & FOLLOW Sets',
  'parsing-table': 'LL(1) Parsing Table',
  'parsing-simulator': 'Parsing Simulator',
  'parse-tree': 'Parse Tree Visualizer',
  'practice': 'Practice Mode',
};

interface HeaderProps {
  activeSection: ActiveSection;
  onMenuToggle: () => void;
  onReset: () => void;
  onLoadExample: (grammar: string) => void;
}

export function Header({ activeSection, onMenuToggle, onReset, onLoadExample }: HeaderProps) {
  const [examples, setExamples] = useState<ExampleGrammar[]>([]);
  const [loadingExamples, setLoadingExamples] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    const fetchExamples = async () => {
      setLoadingExamples(true);
      try {
        const data = await api.getExamples();
        setExamples(data);
      } catch {
        // Silently fail — examples are a nice-to-have
      } finally {
        setLoadingExamples(false);
      }
    };
    fetchExamples();
  }, []);

  const handleExampleSelect = (example: ExampleGrammar) => {
    onLoadExample(example.grammar);
    setShowDropdown(false);
  };

  return (
    <header className="relative bg-[#0f172a] border-b border-gray-800 flex-shrink-0">
      {/* Content */}
      <div className="flex items-center gap-3 px-4 py-3">
        {/* Hamburger (mobile) */}
        <button
          onClick={onMenuToggle}
          className="md:hidden text-gray-400 hover:text-white transition-colors p-1"
          aria-label="Toggle menu"
        >
          <Menu size={20} />
        </button>

        {/* Logo */}
        <div className="flex items-center gap-2 mr-4">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center shadow-glow-blue">
            <TreePine size={16} className="text-white" />
          </div>
          <span className="hidden sm:block text-lg font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            ParseViz
          </span>
        </div>

        {/* Current section label */}
        <div className="flex-1 min-w-0">
          <h1 className="text-sm font-semibold text-white truncate">
            {SECTION_LABELS[activeSection]}
          </h1>
          <p className="text-xs text-gray-500 hidden sm:block">
            Compiler Design — LL(1) Parser
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Sample grammars dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowDropdown((prev) => !prev)}
              disabled={loadingExamples}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm text-gray-300 transition-all duration-200 disabled:opacity-50"
            >
              {loadingExamples ? (
                <Loader2 size={14} className="animate-spin" />
              ) : null}
              <span className="hidden sm:inline">Examples</span>
              <ChevronDown size={14} className={`transition-transform ${showDropdown ? 'rotate-180' : ''}`} />
            </button>

            {showDropdown && examples.length > 0 && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowDropdown(false)}
                />
                <div className="absolute right-0 top-full mt-1 z-20 bg-gray-900 border border-gray-700 rounded-xl shadow-2xl overflow-hidden min-w-56">
                  <div className="px-3 py-2 border-b border-gray-800">
                    <p className="text-xs text-gray-500 font-medium uppercase tracking-wide">
                      Sample Grammars
                    </p>
                  </div>
                  {examples.map((ex, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleExampleSelect(ex)}
                      className="w-full text-left px-3 py-2.5 hover:bg-gray-800 transition-colors group"
                    >
                      <p className="text-sm text-white font-medium group-hover:text-blue-300 transition-colors">
                        {ex.name}
                      </p>
                      {ex.description && (
                        <p className="text-xs text-gray-500 mt-0.5 truncate">{ex.description}</p>
                      )}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>

          {/* Reset button */}
          <button
            onClick={onReset}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-red-900/40 border border-gray-700 hover:border-red-700/60 rounded-lg text-sm text-gray-300 hover:text-red-300 transition-all duration-200"
            title="Reset all"
          >
            <RefreshCw size={14} />
            <span className="hidden sm:inline">Reset</span>
          </button>
        </div>
      </div>

      {/* Accent bar */}
      <div className="h-0.5 bg-gradient-to-r from-blue-600 via-cyan-500 to-violet-600" />
    </header>
  );
}
