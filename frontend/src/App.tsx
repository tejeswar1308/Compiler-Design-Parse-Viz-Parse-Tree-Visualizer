import { useState, useCallback, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useGrammar } from './hooks/useGrammar';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { GrammarEditor } from './components/GrammarEditor';
import { TransformationPanel } from './components/TransformationPanel';
import { FirstFollowPanel } from './components/FirstFollowPanel';
import { ParsingTable } from './components/ParsingTable';
import { ParsingSimulator } from './components/ParsingSimulator';
import { ParseTreeView } from './components/ParseTreeView';
import { PracticePanel } from './components/PracticePanel';
import type { ActiveSection } from './types';

const pageVariants = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
};

const pageTransition = {
  type: 'tween' as const,
  duration: 0.22,
  ease: 'easeInOut',
};

export default function App() {
  const [activeSection, setActiveSection] = useState<ActiveSection>('grammar');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const grammar = useGrammar();

  // Close sidebar on mobile by default
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) setSidebarOpen(false);
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleSectionChange = useCallback((section: ActiveSection) => {
    setActiveSection(section);
    if (window.innerWidth < 768) setSidebarOpen(false);
  }, []);

  const renderSection = () => {
    switch (activeSection) {
      case 'grammar':
        return <GrammarEditor key="grammar" {...grammar} />;
      case 'left-recursion':
        return (
          <TransformationPanel
            key="left-recursion"
            type="left-recursion"
            grammarText={grammar.activeGrammar || grammar.grammarText}
            result={grammar.lrResult}
            loading={grammar.loading.eliminateLeftRecursion}
            error={grammar.errors.eliminateLeftRecursion}
            onRun={grammar.eliminateLeftRecursion}
            onUseTransformed={grammar.useTransformedGrammar}
            isGrammarValid={!!grammar.validationResult?.success}
          />
        );
      case 'left-factoring':
        return (
          <TransformationPanel
            key="left-factoring"
            type="left-factoring"
            grammarText={grammar.activeGrammar || grammar.grammarText}
            result={grammar.lfResult}
            loading={grammar.loading.applyLeftFactoring}
            error={grammar.errors.applyLeftFactoring}
            onRun={grammar.applyLeftFactoring}
            onUseTransformed={grammar.useTransformedGrammar}
            isGrammarValid={!!grammar.validationResult?.success}
          />
        );
      case 'first-follow':
        return (
          <FirstFollowPanel
            key="first-follow"
            grammarText={grammar.activeGrammar || grammar.grammarText}
            result={grammar.firstFollow}
            loading={grammar.loading.computeFirstFollow}
            error={grammar.errors.computeFirstFollow}
            onRun={grammar.computeFirstFollow}
            isGrammarValid={!!grammar.validationResult?.success}
          />
        );
      case 'parsing-table':
        return (
          <ParsingTable
            key="parsing-table"
            grammarText={grammar.activeGrammar || grammar.grammarText}
            result={grammar.parsingTable}
            loading={grammar.loading.buildTable}
            error={grammar.errors.buildTable}
            onRun={grammar.buildTable}
            isGrammarValid={!!grammar.validationResult?.success}
          />
        );
      case 'parsing-simulator':
        return (
          <ParsingSimulator
            key="parsing-simulator"
            grammarText={grammar.activeGrammar || grammar.grammarText}
            result={grammar.parseResult}
            loading={grammar.loading.parseString}
            error={grammar.errors.parseString}
            onParse={grammar.parseString}
            isGrammarValid={!!grammar.validationResult?.success}
          />
        );
      case 'parse-tree':
        return (
          <ParseTreeView
            key="parse-tree"
            parseResult={grammar.parseResult}
          />
        );
      case 'practice':
        return <PracticePanel key="practice" />;
      default:
        return <GrammarEditor key="grammar" {...grammar} />;
    }
  };

  return (
    <div className="flex h-screen bg-[#0a0f1e] text-white overflow-hidden">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/60 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`
          fixed md:relative z-30 h-full transition-transform duration-300
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        <Sidebar
          activeSection={activeSection}
          onSectionChange={handleSectionChange}
          isCollapsed={false}
        />
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header
          activeSection={activeSection}
          onMenuToggle={() => setSidebarOpen((prev) => !prev)}
          onReset={grammar.resetAll}
          onLoadExample={grammar.loadExample}
        />

        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeSection}
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={pageTransition}
              className="h-full"
            >
              {renderSection()}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
