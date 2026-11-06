export interface Grammar {
  nonterminals: string[];
  terminals: string[];
  productions: Record<string, string[][]>;
  start_symbol: string;
}

export interface ValidationResult {
  success: boolean;
  grammar?: Grammar;
  errors?: string[];
}

export interface TransformResult {
  original_grammar: string;
  has_left_recursion?: boolean;
  needs_factoring?: boolean;
  recursive_nonterminals?: string[];
  steps: TransformStep[];
  transformed_grammar: string;
  success: boolean;
  warnings: string[];
}

export interface TransformStep {
  step: number;
  description: string;
  grammar_state: string;
}

export interface FirstFollowResult {
  first_sets: Record<string, string[]>;
  follow_sets: Record<string, string[]>;
  nullable: string[];
  steps?: StepEntry[];
}

export interface StepEntry {
  description: string;
  detail?: string;
}

export interface ParsingTableResult {
  table: Record<string, Record<string, string | null>>;
  terminals: string[];
  nonterminals: string[];
  conflicts: Conflict[];
  is_ll1: boolean;
}

export interface Conflict {
  nonterminal: string;
  terminal: string;
  productions: string[];
}

export interface ParseStep {
  step: number;
  stack: string[];
  remaining_input: string[];
  action: string;
  production?: string;
}

export interface ParseResult {
  accepted: boolean;
  steps: ParseStep[];
  error_message?: string;
  error_step?: number;
  productions_used: string[];
  parse_tree?: TreeNode;
}

export interface TreeNode {
  id: string;
  label: string;
  type: 'nonterminal' | 'terminal' | 'epsilon';
  production?: string;
  children?: TreeNode[];
}

export interface PracticeQuestion {
  id: string;
  type: string;
  question: string;
  grammar: string;
  options: string[];
  correct_answer: string;
  explanation: string;
}

export interface PracticeCheckResult {
  correct: boolean;
  correct_answer: string;
  explanation: string;
  step_by_step?: string[];
}

export type ActiveSection =
  | 'grammar'
  | 'left-recursion'
  | 'left-factoring'
  | 'first-follow'
  | 'parsing-table'
  | 'parsing-simulator'
  | 'parse-tree'
  | 'practice';

export interface ExampleGrammar {
  name: string;
  grammar: string;
  description?: string;
}
