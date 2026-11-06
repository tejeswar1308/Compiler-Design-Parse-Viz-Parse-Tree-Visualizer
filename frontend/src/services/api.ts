import axios from 'axios';
import type {
  ValidationResult,
  TransformResult,
  FirstFollowResult,
  ParsingTableResult,
  ParseResult,
  PracticeQuestion,
  PracticeCheckResult,
  ExampleGrammar,
} from '../types';

const client = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.data?.detail) {
      return Promise.reject(new Error(error.response.data.detail));
    }
    if (error.response?.data?.message) {
      return Promise.reject(new Error(error.response.data.message));
    }
    return Promise.reject(error);
  }
);

export const api = {
  validateGrammar: async (grammarText: string, startSymbol?: string): Promise<ValidationResult> => {
    const { data } = await client.post<ValidationResult>('/grammar/validate', {
      grammar: grammarText,
      start_symbol: startSymbol,
    });
    return data;
  },

  eliminateLeftRecursion: async (grammarText: string, startSymbol?: string): Promise<TransformResult> => {
    const { data } = await client.post<TransformResult>('/grammar/eliminate-left-recursion', {
      grammar: grammarText,
      start_symbol: startSymbol,
    });
    return data;
  },

  applyLeftFactoring: async (grammarText: string, startSymbol?: string): Promise<TransformResult> => {
    const { data } = await client.post<TransformResult>('/grammar/left-factoring', {
      grammar: grammarText,
      start_symbol: startSymbol,
    });
    return data;
  },

  computeFirstFollow: async (grammarText: string, startSymbol?: string): Promise<FirstFollowResult> => {
    const { data } = await client.post<FirstFollowResult>('/grammar/first-follow', {
      grammar: grammarText,
      start_symbol: startSymbol,
    });
    return data;
  },

  buildParsingTable: async (grammarText: string, startSymbol?: string): Promise<ParsingTableResult> => {
    const { data } = await client.post<ParsingTableResult>('/grammar/parsing-table', {
      grammar: grammarText,
      start_symbol: startSymbol,
    });
    return data;
  },

  parseString: async (
    grammarText: string,
    inputString: string,
    startSymbol?: string,
    useTransformed?: boolean
  ): Promise<ParseResult> => {
    const { data } = await client.post<ParseResult>('/grammar/parse', {
      grammar: grammarText,
      input: inputString,
      start_symbol: startSymbol,
      use_transformed: useTransformed ?? false,
    });
    return data;
  },

  generatePracticeQuestion: async (type?: string): Promise<PracticeQuestion> => {
    const params = type && type !== 'all' ? { type } : {};
    const { data } = await client.get<PracticeQuestion>('/practice/question', { params });
    return data;
  },

  checkPracticeAnswer: async (
    questionId: string,
    answer: string,
    questionData: PracticeQuestion
  ): Promise<PracticeCheckResult> => {
    const { data } = await client.post<PracticeCheckResult>('/practice/check', {
      question_id: questionId,
      answer,
      question_data: questionData,
    });
    return data;
  },

  getExamples: async (): Promise<ExampleGrammar[]> => {
    try {
      const { data } = await client.get<any>('/grammar/examples');
      if (Array.isArray(data)) return data;
      if (data?.examples && Array.isArray(data.examples)) return data.examples;
      return [];
    } catch {
      const { data } = await client.get<any>('/examples');
      if (Array.isArray(data)) return data;
      if (data?.examples && Array.isArray(data.examples)) return data.examples;
      return [];
    }
  },

  healthCheck: async (): Promise<{ status: string }> => {
    const { data } = await client.get<{ status: string }>('/health');
    return data;
  },
};
