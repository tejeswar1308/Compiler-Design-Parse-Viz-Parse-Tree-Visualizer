import { useState, useCallback } from 'react';
import { api } from '../services/api';
import type {
  ValidationResult,
  TransformResult,
  FirstFollowResult,
  ParsingTableResult,
  ParseResult,
} from '../types';

interface LoadingState {
  validate: boolean;
  eliminateLeftRecursion: boolean;
  applyLeftFactoring: boolean;
  computeFirstFollow: boolean;
  buildTable: boolean;
  parseString: boolean;
}

interface ErrorState {
  validate: string | null;
  eliminateLeftRecursion: string | null;
  applyLeftFactoring: string | null;
  computeFirstFollow: string | null;
  buildTable: string | null;
  parseString: string | null;
}

export function useGrammar() {
  const [grammarText, setGrammarText] = useState<string>('');
  const [startSymbol, setStartSymbol] = useState<string>('');
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);

  // Transformed grammars
  const [lrResult, setLrResult] = useState<TransformResult | null>(null);
  const [lfResult, setLfResult] = useState<TransformResult | null>(null);

  // Active grammar used for analysis (original or transformed)
  const [activeGrammar, setActiveGrammar] = useState<string>('');

  // Analysis results
  const [firstFollow, setFirstFollow] = useState<FirstFollowResult | null>(null);
  const [parsingTable, setParsingTable] = useState<ParsingTableResult | null>(null);
  const [parseResult, setParseResult] = useState<ParseResult | null>(null);

  const [loading, setLoading] = useState<LoadingState>({
    validate: false,
    eliminateLeftRecursion: false,
    applyLeftFactoring: false,
    computeFirstFollow: false,
    buildTable: false,
    parseString: false,
  });

  const [errors, setErrors] = useState<ErrorState>({
    validate: null,
    eliminateLeftRecursion: null,
    applyLeftFactoring: null,
    computeFirstFollow: null,
    buildTable: null,
    parseString: null,
  });

  const setLoadingKey = (key: keyof LoadingState, value: boolean) =>
    setLoading((prev) => ({ ...prev, [key]: value }));

  const setErrorKey = (key: keyof ErrorState, value: string | null) =>
    setErrors((prev) => ({ ...prev, [key]: value }));

  const validate = useCallback(async () => {
    if (!grammarText.trim()) return;
    setLoadingKey('validate', true);
    setErrorKey('validate', null);
    try {
      const result = await api.validateGrammar(grammarText, startSymbol || undefined);
      setValidationResult(result);
      if (result.success) {
        setActiveGrammar(grammarText);
        // Reset downstream results when grammar changes
        setFirstFollow(null);
        setParsingTable(null);
        setParseResult(null);
        setLrResult(null);
        setLfResult(null);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Validation failed';
      setErrorKey('validate', message);
      setValidationResult({ success: false, errors: [message] });
    } finally {
      setLoadingKey('validate', false);
    }
  }, [grammarText, startSymbol]);

  const eliminateLeftRecursion = useCallback(async () => {
    const grammar = activeGrammar || grammarText;
    if (!grammar.trim()) return;
    setLoadingKey('eliminateLeftRecursion', true);
    setErrorKey('eliminateLeftRecursion', null);
    try {
      const result = await api.eliminateLeftRecursion(grammar, startSymbol || undefined);
      setLrResult(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Left recursion elimination failed';
      setErrorKey('eliminateLeftRecursion', message);
    } finally {
      setLoadingKey('eliminateLeftRecursion', false);
    }
  }, [activeGrammar, grammarText, startSymbol]);

  const applyLeftFactoring = useCallback(async () => {
    const grammar = activeGrammar || grammarText;
    if (!grammar.trim()) return;
    setLoadingKey('applyLeftFactoring', true);
    setErrorKey('applyLeftFactoring', null);
    try {
      const result = await api.applyLeftFactoring(grammar, startSymbol || undefined);
      setLfResult(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Left factoring failed';
      setErrorKey('applyLeftFactoring', message);
    } finally {
      setLoadingKey('applyLeftFactoring', false);
    }
  }, [activeGrammar, grammarText, startSymbol]);

  const computeFirstFollow = useCallback(async () => {
    const grammar = activeGrammar || grammarText;
    if (!grammar.trim()) return;
    setLoadingKey('computeFirstFollow', true);
    setErrorKey('computeFirstFollow', null);
    try {
      const result = await api.computeFirstFollow(grammar, startSymbol || undefined);
      setFirstFollow(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'FIRST/FOLLOW computation failed';
      setErrorKey('computeFirstFollow', message);
    } finally {
      setLoadingKey('computeFirstFollow', false);
    }
  }, [activeGrammar, grammarText, startSymbol]);

  const buildTable = useCallback(async () => {
    const grammar = activeGrammar || grammarText;
    if (!grammar.trim()) return;
    setLoadingKey('buildTable', true);
    setErrorKey('buildTable', null);
    try {
      const result = await api.buildParsingTable(grammar, startSymbol || undefined);
      setParsingTable(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Parsing table construction failed';
      setErrorKey('buildTable', message);
    } finally {
      setLoadingKey('buildTable', false);
    }
  }, [activeGrammar, grammarText, startSymbol]);

  const parseString = useCallback(async (inputString: string) => {
    const grammar = activeGrammar || grammarText;
    if (!grammar.trim()) return;
    setLoadingKey('parseString', true);
    setErrorKey('parseString', null);
    try {
      const result = await api.parseString(grammar, inputString, startSymbol || undefined);
      setParseResult(result);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Parsing failed';
      setErrorKey('parseString', message);
    } finally {
      setLoadingKey('parseString', false);
    }
  }, [activeGrammar, grammarText, startSymbol]);

  const useTransformedGrammar = useCallback((transformedText: string) => {
    setActiveGrammar(transformedText);
    // Reset downstream results
    setFirstFollow(null);
    setParsingTable(null);
    setParseResult(null);
  }, []);

  const resetAll = useCallback(() => {
    setGrammarText('');
    setStartSymbol('');
    setValidationResult(null);
    setLrResult(null);
    setLfResult(null);
    setActiveGrammar('');
    setFirstFollow(null);
    setParsingTable(null);
    setParseResult(null);
    setErrors({
      validate: null,
      eliminateLeftRecursion: null,
      applyLeftFactoring: null,
      computeFirstFollow: null,
      buildTable: null,
      parseString: null,
    });
  }, []);

  const loadExample = useCallback((grammar: string) => {
    setGrammarText(grammar);
    setActiveGrammar('');
    setValidationResult(null);
    setLrResult(null);
    setLfResult(null);
    setFirstFollow(null);
    setParsingTable(null);
    setParseResult(null);
  }, []);

  return {
    // State
    grammarText,
    setGrammarText,
    startSymbol,
    setStartSymbol,
    validationResult,
    lrResult,
    lfResult,
    activeGrammar,
    firstFollow,
    parsingTable,
    parseResult,
    loading,
    errors,

    // Actions
    validate,
    eliminateLeftRecursion,
    applyLeftFactoring,
    computeFirstFollow,
    buildTable,
    parseString,
    useTransformedGrammar,
    resetAll,
    loadExample,
  };
}
