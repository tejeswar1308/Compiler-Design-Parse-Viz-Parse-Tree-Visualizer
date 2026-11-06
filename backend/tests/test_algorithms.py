"""
Comprehensive pytest tests for ParseViz backend algorithms.

Tests cover:
1. Grammar parsing
2. Left recursion elimination
3. Left factoring
4. FIRST sets
5. FOLLOW sets
6. LL(1) table construction
7. Conflict detection
8. Predictive parsing (accept/reject)
9. Parse tree construction
10. Tokenizer
11. End-to-end arithmetic grammar
"""

import pytest
from app.services.grammar_parser import parse_grammar, grammar_to_dict, Grammar, EPSILON
from app.services.left_recursion import eliminate_left_recursion, _has_immediate_left_recursion
from app.services.left_factoring import left_factor, _longest_common_prefix
from app.services.first_follow import (
    compute_first_sets,
    compute_follow_sets,
    compute_first_of_string,
    compute_nullable
)
from app.services.parsing_table import build_parsing_table, build_parsing_table_from_text
from app.services.predictive_parser import predictive_parse
from app.services.parse_tree import build_parse_tree
from app.services.tokenizer import tokenize, smart_tokenize


# ===========================================================================
# Helper
# ===========================================================================

def get_grammar(text: str, start: str = None):
    """Parse grammar text and return Grammar object."""
    result = parse_grammar(text, start)
    assert result["success"], f"Grammar parsing failed: {result['errors']}"
    return result["grammar"]


# ===========================================================================
# 1. Grammar Parsing
# ===========================================================================

class TestGrammarParser:

    def test_simple_valid_grammar(self):
        text = "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id"
        result = parse_grammar(text)
        assert result["success"] is True
        g = result["grammar"]
        assert "E" in g.nonterminals
        assert "T" in g.nonterminals
        assert "F" in g.nonterminals
        assert "+" in g.terminals
        assert "*" in g.terminals
        assert "id" in g.terminals
        assert g.start_symbol == "E"

    def test_epsilon_production(self):
        text = "A -> B C\nB -> b | ε\nC -> c | ε"
        result = parse_grammar(text)
        assert result["success"] is True
        g = result["grammar"]
        # B has epsilon production
        prods_B = g.get_productions("B")
        assert [EPSILON] in prods_B

    def test_epsilon_word_form(self):
        text = "A -> a | epsilon"
        result = parse_grammar(text)
        assert result["success"] is True
        g = result["grammar"]
        prods = g.get_productions("A")
        assert [EPSILON] in prods

    def test_multichar_symbols(self):
        text = "Expr -> Term Expr_prime\nExpr_prime -> + Term Expr_prime | ε\nTerm -> id | num"
        result = parse_grammar(text)
        assert result["success"] is True
        g = result["grammar"]
        assert "Expr" in g.nonterminals
        assert "Term" in g.nonterminals
        assert "Expr_prime" in g.nonterminals
        assert "id" in g.terminals
        assert "num" in g.terminals

    def test_missing_arrow_error(self):
        text = "E E + T | T"
        result = parse_grammar(text)
        assert result["success"] is False
        assert any("Missing '->'".casefold() in e.casefold() or "Missing" in e for e in result["errors"])

    def test_empty_grammar_error(self):
        result = parse_grammar("")
        assert result["success"] is False
        assert len(result["errors"]) > 0

    def test_duplicate_production_error(self):
        text = "E -> T\nE -> T"
        result = parse_grammar(text)
        assert result["success"] is False
        assert any("Duplicate" in e or "duplicate" in e for e in result["errors"])

    def test_custom_start_symbol(self):
        text = "A -> a\nB -> b"
        result = parse_grammar(text, start_symbol="B")
        assert result["success"] is True
        assert result["grammar"].start_symbol == "B"

    def test_invalid_start_symbol(self):
        text = "A -> a\nB -> b"
        result = parse_grammar(text, start_symbol="Z")
        assert result["success"] is False

    def test_grammar_to_dict(self):
        text = "S -> a B\nB -> b | ε"
        g = get_grammar(text)
        d = grammar_to_dict(g)
        assert "nonterminals" in d
        assert "terminals" in d
        assert "productions" in d
        assert "start_symbol" in d
        assert d["start_symbol"] == "S"

    def test_comment_lines_ignored(self):
        text = "# This is a comment\nE -> a | b"
        result = parse_grammar(text)
        assert result["success"] is True

    def test_empty_lines_ignored(self):
        text = "E -> a\n\n\nF -> b"
        result = parse_grammar(text)
        assert result["success"] is True

    def test_whitespace_only_grammar(self):
        result = parse_grammar("   \n  \n ")
        assert result["success"] is False


# ===========================================================================
# 2. Left Recursion Elimination
# ===========================================================================

class TestLeftRecursionElimination:

    def test_simple_immediate_lr(self):
        """A -> A a | b  should eliminate to  A -> b A_prime, A_prime -> a A_prime | ε"""
        text = "A -> A a | b"
        result = eliminate_left_recursion(text)
        assert result["success"] is True
        assert result["has_left_recursion"] is True
        assert "A" in result["recursive_nonterminals"]

        transformed = result["transformed_grammar"]
        assert "A_prime" in transformed or "A'" in transformed or "_prime" in transformed
        # Verify no left recursion in result
        lr_check = eliminate_left_recursion(transformed)
        assert lr_check["has_left_recursion"] is False

    def test_arithmetic_immediate_lr(self):
        """E -> E + T | T"""
        text = "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id"
        result = eliminate_left_recursion(text)
        assert result["success"] is True
        assert result["has_left_recursion"] is True
        assert "E" in result["recursive_nonterminals"]
        assert "T" in result["recursive_nonterminals"]
        transformed = result["transformed_grammar"]
        # Transformed grammar should contain prime nonterminals
        assert "_prime" in transformed

    def test_no_lr_grammar(self):
        """Grammar without LR should be unchanged."""
        text = "S -> a B\nB -> b | ε"
        result = eliminate_left_recursion(text)
        assert result["success"] is True
        assert result["has_left_recursion"] is False
        assert result["recursive_nonterminals"] == []

    def test_indirect_lr(self):
        """S -> A a | b; A -> S b | ε — indirect LR between S and A."""
        text = "S -> A a | b\nA -> S b | ε"
        result = eliminate_left_recursion(text)
        assert result["success"] is True
        # After elimination, no left recursion
        transformed = result["transformed_grammar"]
        check = eliminate_left_recursion(transformed)
        assert check["has_left_recursion"] is False

    def test_purely_left_recursive(self):
        """A -> A — grammar with only left-recursive production."""
        text = "A -> A a"
        result = eliminate_left_recursion(text)
        assert result["success"] is True
        assert result["has_left_recursion"] is True

    def test_steps_are_generated(self):
        text = "E -> E + T | T"
        result = eliminate_left_recursion(text)
        assert result["success"] is True
        assert len(result["steps"]) > 0
        for step in result["steps"]:
            assert "step" in step
            assert "description" in step
            assert "grammar_state" in step

    def test_collision_free_naming(self):
        """When A_prime already exists, use A_prime1."""
        text = "A -> A a | b\nA_prime -> x"
        result = eliminate_left_recursion(text)
        assert result["success"] is True
        transformed = result["transformed_grammar"]
        # Should not overwrite A_prime
        lines = transformed.split('\n')
        nt_names = [l.split('->')[0].strip() for l in lines if '->' in l]
        # Each NT name must be unique
        assert len(nt_names) == len(set(nt_names))


# ===========================================================================
# 3. Left Factoring
# ===========================================================================

class TestLeftFactoring:

    def test_simple_left_factoring(self):
        """X -> a b c | a b d | a e  should factor out 'a'."""
        text = "X -> a b c | a b d | a e"
        result = left_factor(text)
        assert result["success"] is True
        assert result["needs_factoring"] is True
        transformed = result["transformed_grammar"]
        assert "_f" in transformed or "X_" in transformed

    def test_no_factoring_needed(self):
        """S -> a | b | c — no common prefix."""
        text = "S -> a | b | c"
        result = left_factor(text)
        assert result["success"] is True
        assert result["needs_factoring"] is False

    def test_multi_round_factoring(self):
        """Factoring may require multiple rounds."""
        text = "A -> a b c | a b d"
        result = left_factor(text)
        assert result["success"] is True
        assert result["needs_factoring"] is True
        # After factoring, no common prefixes should remain
        transformed_parse = parse_grammar(result["transformed_grammar"])
        assert transformed_parse["success"] is True
        g = transformed_parse["grammar"]
        for nt in g.nonterminals_ordered():
            lcp = _longest_common_prefix(g.get_productions(nt))
            assert lcp == [], f"{nt} still has common prefix {lcp}"

    def test_epsilon_not_confused_with_prefix(self):
        """A -> a | ε should not factor (no common prefix)."""
        text = "A -> a | ε"
        result = left_factor(text)
        assert result["success"] is True
        assert result["needs_factoring"] is False

    def test_steps_generated(self):
        text = "X -> a b c | a b d"
        result = left_factor(text)
        assert result["success"] is True
        assert len(result["steps"]) > 0

    def test_longest_common_prefix_util(self):
        prods = [["a", "b", "c"], ["a", "b", "d"], ["a", "e"]]
        lcp = _longest_common_prefix(prods)
        assert lcp == ["a"]

    def test_longest_common_prefix_multitoken(self):
        prods = [["a", "b", "c"], ["a", "b", "d"]]
        lcp = _longest_common_prefix(prods)
        assert lcp == ["a", "b"]

    def test_no_common_prefix_empty(self):
        prods = [["a"], ["b"]]
        lcp = _longest_common_prefix(prods)
        assert lcp == []


# ===========================================================================
# 4 & 5. FIRST and FOLLOW sets
# ===========================================================================

class TestFirstFollow:

    def _get_ff(self, text, start=None):
        g = get_grammar(text, start)
        first = compute_first_sets(g)
        follow = compute_follow_sets(g, first)
        return g, first, follow

    def test_first_terminal(self):
        g, first, follow = self._get_ff("S -> a | b")
        assert "a" in first["S"]
        assert "b" in first["S"]

    def test_first_nullable(self):
        g, first, follow = self._get_ff("A -> B C\nB -> b | ε\nC -> c | ε")
        assert EPSILON in first["B"]
        assert EPSILON in first["C"]
        assert EPSILON in first["A"]
        assert "b" in first["A"]
        assert "c" in first["A"]

    def test_first_arithmetic_ll1(self):
        text = (
            "E -> T E_prime\n"
            "E_prime -> + T E_prime | ε\n"
            "T -> F T_prime\n"
            "T_prime -> * F T_prime | ε\n"
            "F -> ( E ) | id"
        )
        g, first, follow = self._get_ff(text)
        assert "(" in first["E"]
        assert "id" in first["E"]
        assert "+" in first["E_prime"]
        assert EPSILON in first["E_prime"]
        assert "*" in first["T_prime"]
        assert EPSILON in first["T_prime"]

    def test_follow_start_has_dollar(self):
        g, first, follow = self._get_ff("S -> a B\nB -> b | ε")
        assert "$" in follow["S"]

    def test_follow_arithmetic_ll1(self):
        text = (
            "E -> T E_prime\n"
            "E_prime -> + T E_prime | ε\n"
            "T -> F T_prime\n"
            "T_prime -> * F T_prime | ε\n"
            "F -> ( E ) | id"
        )
        g, first, follow = self._get_ff(text)
        assert "$" in follow["E"]
        assert ")" in follow["E"]
        assert "+" in follow["E_prime"] or "$" in follow["E_prime"]
        assert "$" in follow["T"]
        assert "+" in follow["T"]
        assert ")" in follow["T"]

    def test_nullable_list(self):
        text = "A -> B C\nB -> b | ε\nC -> c | ε"
        g = get_grammar(text)
        first = compute_first_sets(g)
        nullable = compute_nullable(g, first)
        assert "B" in nullable
        assert "C" in nullable
        assert "A" in nullable

    def test_first_of_string_utility(self):
        text = "A -> B C\nB -> b | ε\nC -> c"
        g = get_grammar(text)
        first = compute_first_sets(g)
        result = compute_first_of_string(["B", "C"], first, g)
        assert "b" in result
        assert "c" in result  # since B is nullable

    def test_fixed_point_convergence(self):
        """Mutual recursion: A -> B a | c; B -> A b | d"""
        text = "A -> B a | c\nB -> A b | d"
        g = get_grammar(text)
        first = compute_first_sets(g)
        assert "c" in first["A"]
        assert "d" in first["A"]
        assert "c" in first["B"]
        assert "d" in first["B"]

    def test_follow_propagation(self):
        """S -> A B $; A -> a; B -> b | ε — FOLLOW(A) includes FIRST(B) and FOLLOW(S) if B nullable"""
        text = "S -> A B\nA -> a\nB -> b | ε"
        g, first, follow = self._get_ff(text)
        # A is followed by B; since B is nullable, FOLLOW(A) also includes FOLLOW(S)
        assert "b" in follow["A"] or "$" in follow["A"]


# ===========================================================================
# 6 & 7. LL(1) Parsing Table + Conflict Detection
# ===========================================================================

class TestParsingTable:

    def test_arithmetic_ll1_no_conflicts(self):
        text = (
            "E -> T E_prime\n"
            "E_prime -> + T E_prime | ε\n"
            "T -> F T_prime\n"
            "T_prime -> * F T_prime | ε\n"
            "F -> ( E ) | id"
        )
        result = build_parsing_table_from_text(text)
        assert result["success"] is True
        assert result["is_ll1"] is True
        assert result["conflicts"] == []

    def test_conflict_grammar_not_ll1(self):
        """S -> i E t S | i E t S e S | a — has conflict."""
        text = "S -> i E t S e S | i E t S | a\nE -> b"
        result = build_parsing_table_from_text(text)
        assert result["success"] is True
        assert result["is_ll1"] is False
        assert len(result["conflicts"]) > 0

    def test_table_has_correct_entries(self):
        text = "S -> a B\nB -> b | ε"
        result = build_parsing_table_from_text(text)
        assert result["success"] is True
        table = result["table"]
        # M[S][a] should be "S -> a B"
        assert table["S"]["a"] == "S -> a B"
        # M[B][b] should be "B -> b"
        assert table["B"]["b"] == "B -> b"

    def test_table_nonterminals_and_terminals(self):
        text = (
            "E -> T E_prime\n"
            "E_prime -> + T E_prime | ε\n"
            "T -> F T_prime\n"
            "T_prime -> * F T_prime | ε\n"
            "F -> ( E ) | id"
        )
        result = build_parsing_table_from_text(text)
        assert "E" in result["nonterminals"]
        assert "E_prime" in result["nonterminals"]
        assert "id" in result["terminals"]
        assert "$" in result["terminals"]

    def test_epsilon_follow_entry(self):
        """E_prime -> ε should fill M[E_prime][a] for each a in FOLLOW(E_prime)."""
        text = (
            "E -> T E_prime\n"
            "E_prime -> + T E_prime | ε\n"
            "T -> F T_prime\n"
            "T_prime -> * F T_prime | ε\n"
            "F -> ( E ) | id"
        )
        result = build_parsing_table_from_text(text)
        table = result["table"]
        # E_prime -> ε should appear in M[E_prime][$] and M[E_prime][)]
        assert table["E_prime"]["$"] is not None
        assert table["E_prime"][")"] is not None


# ===========================================================================
# 8 & 9. Predictive Parsing (Accept / Reject)
# ===========================================================================

class TestPredictiveParser:

    def _setup(self, grammar_text: str, start: str = None):
        from app.services.grammar_parser import parse_grammar
        from app.services.first_follow import compute_first_sets, compute_follow_sets
        from app.services.parsing_table import build_parsing_table
        g = get_grammar(grammar_text, start)
        first = compute_first_sets(g)
        follow = compute_follow_sets(g, first)
        table_result = build_parsing_table(g, first, follow)
        return g, table_result["table"]

    def test_accept_simple(self):
        grammar_text = "S -> a B\nB -> b | ε"
        g, table = self._setup(grammar_text)
        result = predictive_parse(g, table, ["a", "b", "$"], "S")
        assert result["accepted"] is True
        assert result["error_message"] is None

    def test_accept_epsilon_only(self):
        grammar_text = "S -> a B\nB -> b | ε"
        g, table = self._setup(grammar_text)
        # "a" followed by nothing (B -> ε)
        result = predictive_parse(g, table, ["a", "$"], "S")
        assert result["accepted"] is True

    def test_reject_invalid_token(self):
        grammar_text = "S -> a B\nB -> b | ε"
        g, table = self._setup(grammar_text)
        result = predictive_parse(g, table, ["c", "$"], "S")
        assert result["accepted"] is False
        assert result["error_message"] is not None

    def test_accept_arithmetic(self):
        grammar_text = (
            "E -> T E_prime\n"
            "E_prime -> + T E_prime | ε\n"
            "T -> F T_prime\n"
            "T_prime -> * F T_prime | ε\n"
            "F -> ( E ) | id"
        )
        g, table = self._setup(grammar_text)
        # Parse "id + id * id"
        tokens = ["id", "+", "id", "*", "id", "$"]
        result = predictive_parse(g, table, tokens, "E")
        assert result["accepted"] is True
        assert len(result["productions_used"]) > 0

    def test_reject_arithmetic_incomplete(self):
        grammar_text = (
            "E -> T E_prime\n"
            "E_prime -> + T E_prime | ε\n"
            "T -> F T_prime\n"
            "T_prime -> * F T_prime | ε\n"
            "F -> ( E ) | id"
        )
        g, table = self._setup(grammar_text)
        # "id +" is incomplete
        tokens = ["id", "+", "$"]
        result = predictive_parse(g, table, tokens, "E")
        assert result["accepted"] is False

    def test_steps_have_required_fields(self):
        grammar_text = "S -> a B\nB -> b | ε"
        g, table = self._setup(grammar_text)
        result = predictive_parse(g, table, ["a", "b", "$"], "S")
        for step in result["steps"]:
            assert "step" in step
            assert "stack" in step
            assert "remaining_input" in step
            assert "action" in step

    def test_dollar_auto_appended(self):
        """Parser should handle tokens without '$' at end."""
        grammar_text = "S -> a B\nB -> b | ε"
        g, table = self._setup(grammar_text)
        result = predictive_parse(g, table, ["a", "b"], "S")
        assert result["accepted"] is True

    def test_productions_used_matches_derivation(self):
        grammar_text = (
            "E -> T E_prime\n"
            "E_prime -> + T E_prime | ε\n"
            "T -> F T_prime\n"
            "T_prime -> * F T_prime | ε\n"
            "F -> ( E ) | id"
        )
        g, table = self._setup(grammar_text)
        tokens = ["id", "$"]
        result = predictive_parse(g, table, tokens, "E")
        assert result["accepted"] is True
        # Should have used E -> T E_prime, T -> F T_prime, F -> id, etc.
        prods = result["productions_used"]
        assert any("E -> T E_prime" in p for p in prods)
        assert any("F -> id" in p or "id" in p for p in prods)


# ===========================================================================
# 10. Parse Tree
# ===========================================================================

class TestParseTree:

    def _parse_and_tree(self, grammar_text: str, tokens: list, start: str = None):
        from app.services.grammar_parser import parse_grammar
        from app.services.first_follow import compute_first_sets, compute_follow_sets
        from app.services.parsing_table import build_parsing_table
        from app.services.predictive_parser import predictive_parse
        from app.services.parse_tree import build_parse_tree

        g = get_grammar(grammar_text, start)
        first = compute_first_sets(g)
        follow = compute_follow_sets(g, first)
        table_result = build_parsing_table(g, first, follow)
        sim = predictive_parse(g, table_result["table"], tokens, g.start_symbol)
        assert sim["accepted"], f"Parsing failed: {sim['error_message']}"
        tree_result = build_parse_tree(g, sim["productions_used"], g.start_symbol)
        return g, sim, tree_result

    def test_simple_tree_structure(self):
        grammar_text = "S -> a B\nB -> b | ε"
        _, _, tree_result = self._parse_and_tree(grammar_text, ["a", "b", "$"])
        assert tree_result["success"] is True
        tree = tree_result["tree"]
        assert tree["label"] == "S"
        assert tree["type"] == "nonterminal"
        assert len(tree["children"]) > 0

    def test_tree_has_ids(self):
        grammar_text = "S -> a B\nB -> b | ε"
        _, _, tree_result = self._parse_and_tree(grammar_text, ["a", "b", "$"])
        tree = tree_result["tree"]
        assert "id" in tree
        assert tree["id"].startswith("node-")

    def test_terminal_nodes(self):
        grammar_text = "S -> a B\nB -> b | ε"
        _, _, tree_result = self._parse_and_tree(grammar_text, ["a", "b", "$"])
        tree = tree_result["tree"]
        # Find terminal nodes recursively
        def find_terminals(node):
            found = []
            if node["type"] == "terminal":
                found.append(node["label"])
            for child in node.get("children", []):
                found.extend(find_terminals(child))
            return found
        terminals = find_terminals(tree)
        assert "a" in terminals
        assert "b" in terminals

    def test_epsilon_nodes(self):
        grammar_text = "S -> a B\nB -> b | ε"
        _, _, tree_result = self._parse_and_tree(grammar_text, ["a", "$"])
        tree = tree_result["tree"]
        def find_epsilons(node):
            found = []
            if node["type"] == "epsilon":
                found.append(node)
            for child in node.get("children", []):
                found.extend(find_epsilons(child))
            return found
        epsilons = find_epsilons(tree)
        assert len(epsilons) > 0

    def test_arithmetic_tree(self):
        grammar_text = (
            "E -> T E_prime\n"
            "E_prime -> + T E_prime | ε\n"
            "T -> F T_prime\n"
            "T_prime -> * F T_prime | ε\n"
            "F -> ( E ) | id"
        )
        _, _, tree_result = self._parse_and_tree(
            grammar_text, ["id", "+", "id", "$"]
        )
        assert tree_result["success"] is True
        tree = tree_result["tree"]
        assert tree["label"] == "E"

    def test_empty_productions_used(self):
        from app.services.parse_tree import build_parse_tree
        g = get_grammar("S -> a")
        result = build_parse_tree(g, [], "S")
        assert result["success"] is True
        assert result["tree"] is not None


# ===========================================================================
# 11. Tokenizer
# ===========================================================================

class TestTokenizer:

    def test_simple_tokenize(self):
        terminals = {"id", "+", "*", "(", ")"}
        result = tokenize("id + id", terminals)
        assert result["success"] is True
        assert result["tokens"] == ["id", "+", "id", "$"]

    def test_auto_append_dollar(self):
        terminals = {"a", "b"}
        result = tokenize("a b", terminals)
        assert result["success"] is True
        assert result["tokens"][-1] == "$"

    def test_unrecognized_token_error(self):
        terminals = {"a", "b"}
        result = tokenize("a @ b", terminals)
        assert result["success"] is False
        assert result["error"] is not None

    def test_empty_string(self):
        terminals = {"a"}
        result = tokenize("", terminals)
        assert result["success"] is True
        assert result["tokens"] == ["$"]

    def test_multichar_terminal(self):
        terminals = {"id", "num", "+", "*"}
        result = tokenize("num + id", terminals)
        assert result["success"] is True
        assert "num" in result["tokens"]
        assert "id" in result["tokens"]

    def test_smart_tokenize_fallback(self):
        terminals = {"id", "+", "*", "(", ")"}
        result = smart_tokenize("id + id * id", terminals)
        assert result["success"] is True
        assert result["tokens"] == ["id", "+", "id", "*", "id", "$"]

    def test_longest_match_priority(self):
        """'++' should match '++' before '+'."""
        terminals = {"+", "++", "id"}
        result = tokenize("id ++ id", terminals)
        assert result["success"] is True
        assert "++" in result["tokens"]
        assert "+" not in result["tokens"]


# ===========================================================================
# 12. End-to-End: Arithmetic Grammar
# ===========================================================================

class TestEndToEndArithmetic:
    """
    Full pipeline test for the standard arithmetic grammar.
    """

    GRAMMAR_LR = "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id"
    GRAMMAR_LL1 = (
        "E -> T E_prime\n"
        "E_prime -> + T E_prime | ε\n"
        "T -> F T_prime\n"
        "T_prime -> * F T_prime | ε\n"
        "F -> ( E ) | id"
    )

    def test_lr_grammar_detects_recursion(self):
        result = eliminate_left_recursion(self.GRAMMAR_LR)
        assert result["has_left_recursion"] is True
        assert "E" in result["recursive_nonterminals"]
        assert "T" in result["recursive_nonterminals"]

    def test_ll1_grammar_no_conflicts(self):
        result = build_parsing_table_from_text(self.GRAMMAR_LL1)
        assert result["is_ll1"] is True
        assert result["conflicts"] == []

    def test_ll1_parse_id_plus_id(self):
        from app.services.grammar_parser import parse_grammar
        from app.services.first_follow import compute_first_sets, compute_follow_sets
        from app.services.parsing_table import build_parsing_table
        from app.services.predictive_parser import predictive_parse

        g = get_grammar(self.GRAMMAR_LL1)
        first = compute_first_sets(g)
        follow = compute_follow_sets(g, first)
        table_result = build_parsing_table(g, first, follow)
        tokens = ["id", "+", "id", "$"]
        result = predictive_parse(g, table_result["table"], tokens, "E")
        assert result["accepted"] is True

    def test_ll1_parse_complex_expression(self):
        from app.services.grammar_parser import parse_grammar
        from app.services.first_follow import compute_first_sets, compute_follow_sets
        from app.services.parsing_table import build_parsing_table
        from app.services.predictive_parser import predictive_parse

        g = get_grammar(self.GRAMMAR_LL1)
        first = compute_first_sets(g)
        follow = compute_follow_sets(g, first)
        table_result = build_parsing_table(g, first, follow)
        # ( id + id ) * id
        tokens = ["(", "id", "+", "id", ")", "*", "id", "$"]
        result = predictive_parse(g, table_result["table"], tokens, "E")
        assert result["accepted"] is True

    def test_ll1_reject_invalid(self):
        from app.services.grammar_parser import parse_grammar
        from app.services.first_follow import compute_first_sets, compute_follow_sets
        from app.services.parsing_table import build_parsing_table
        from app.services.predictive_parser import predictive_parse

        g = get_grammar(self.GRAMMAR_LL1)
        first = compute_first_sets(g)
        follow = compute_follow_sets(g, first)
        table_result = build_parsing_table(g, first, follow)
        # "+ id" is invalid (starts with +)
        tokens = ["+", "id", "$"]
        result = predictive_parse(g, table_result["table"], tokens, "E")
        assert result["accepted"] is False

    def test_parse_tree_from_ll1(self):
        from app.services.grammar_parser import parse_grammar
        from app.services.first_follow import compute_first_sets, compute_follow_sets
        from app.services.parsing_table import build_parsing_table
        from app.services.predictive_parser import predictive_parse
        from app.services.parse_tree import build_parse_tree

        g = get_grammar(self.GRAMMAR_LL1)
        first = compute_first_sets(g)
        follow = compute_follow_sets(g, first)
        table_result = build_parsing_table(g, first, follow)
        tokens = ["id", "+", "id", "$"]
        sim = predictive_parse(g, table_result["table"], tokens, "E")
        assert sim["accepted"] is True
        tree_result = build_parse_tree(g, sim["productions_used"], "E")
        assert tree_result["success"] is True
        tree = tree_result["tree"]
        assert tree["label"] == "E"
        assert tree["type"] == "nonterminal"
        assert len(tree["children"]) > 0

    def test_tokenizer_with_arithmetic(self):
        terminals = {"id", "+", "*", "(", ")"}
        result = smart_tokenize("id + id * id", terminals)
        assert result["success"] is True
        assert result["tokens"] == ["id", "+", "id", "*", "id", "$"]


# ===========================================================================
# 13. Simple LL(1) Grammar: S -> a B; B -> b | ε
# ===========================================================================

class TestSimpleLL1Grammar:

    GRAMMAR = "S -> a B\nB -> b | ε"

    def test_first_sets(self):
        g = get_grammar(self.GRAMMAR)
        first = compute_first_sets(g)
        assert "a" in first["S"]
        assert "b" in first["B"]
        assert EPSILON in first["B"]

    def test_follow_sets(self):
        g = get_grammar(self.GRAMMAR)
        first = compute_first_sets(g)
        follow = compute_follow_sets(g, first)
        assert "$" in follow["S"]
        # FOLLOW(B) includes FOLLOW(S) since B is at end of S -> a B
        assert "$" in follow["B"]

    def test_parsing_table(self):
        result = build_parsing_table_from_text(self.GRAMMAR)
        assert result["is_ll1"] is True
        table = result["table"]
        assert table["S"]["a"] == "S -> a B"

    def test_parse_a_b(self):
        from app.services.grammar_parser import parse_grammar
        from app.services.first_follow import compute_first_sets, compute_follow_sets
        from app.services.parsing_table import build_parsing_table
        from app.services.predictive_parser import predictive_parse
        g = get_grammar(self.GRAMMAR)
        first = compute_first_sets(g)
        follow = compute_follow_sets(g, first)
        table = build_parsing_table(g, first, follow)["table"]
        result = predictive_parse(g, table, ["a", "b", "$"], "S")
        assert result["accepted"] is True

    def test_parse_a_only(self):
        from app.services.grammar_parser import parse_grammar
        from app.services.first_follow import compute_first_sets, compute_follow_sets
        from app.services.parsing_table import build_parsing_table
        from app.services.predictive_parser import predictive_parse
        g = get_grammar(self.GRAMMAR)
        first = compute_first_sets(g)
        follow = compute_follow_sets(g, first)
        table = build_parsing_table(g, first, follow)["table"]
        result = predictive_parse(g, table, ["a", "$"], "S")
        assert result["accepted"] is True

    def test_reject_b_only(self):
        from app.services.grammar_parser import parse_grammar
        from app.services.first_follow import compute_first_sets, compute_follow_sets
        from app.services.parsing_table import build_parsing_table
        from app.services.predictive_parser import predictive_parse
        g = get_grammar(self.GRAMMAR)
        first = compute_first_sets(g)
        follow = compute_follow_sets(g, first)
        table = build_parsing_table(g, first, follow)["table"]
        result = predictive_parse(g, table, ["b", "$"], "S")
        assert result["accepted"] is False


# ===========================================================================
# 14. Epsilon Grammar: A -> B C; B -> b | ε; C -> c | ε
# ===========================================================================

class TestEpsilonGrammar:

    GRAMMAR = "A -> B C\nB -> b | ε\nC -> c | ε"

    def test_a_is_nullable(self):
        g = get_grammar(self.GRAMMAR)
        first = compute_first_sets(g)
        assert EPSILON in first["A"]

    def test_first_a_includes_b_and_c(self):
        g = get_grammar(self.GRAMMAR)
        first = compute_first_sets(g)
        assert "b" in first["A"]
        assert "c" in first["A"]

    def test_table_construction(self):
        result = build_parsing_table_from_text(self.GRAMMAR)
        assert result["success"] is True
        # Should be LL(1) (no conflicts)
        assert result["is_ll1"] is True

    def test_parse_bc(self):
        from app.services.grammar_parser import parse_grammar
        from app.services.first_follow import compute_first_sets, compute_follow_sets
        from app.services.parsing_table import build_parsing_table
        from app.services.predictive_parser import predictive_parse
        g = get_grammar(self.GRAMMAR)
        first = compute_first_sets(g)
        follow = compute_follow_sets(g, first)
        table = build_parsing_table(g, first, follow)["table"]
        result = predictive_parse(g, table, ["b", "c", "$"], "A")
        assert result["accepted"] is True

    def test_parse_empty(self):
        from app.services.grammar_parser import parse_grammar
        from app.services.first_follow import compute_first_sets, compute_follow_sets
        from app.services.parsing_table import build_parsing_table
        from app.services.predictive_parser import predictive_parse
        g = get_grammar(self.GRAMMAR)
        first = compute_first_sets(g)
        follow = compute_follow_sets(g, first)
        table = build_parsing_table(g, first, follow)["table"]
        result = predictive_parse(g, table, ["$"], "A")
        assert result["accepted"] is True


# ===========================================================================
# 15. Conflict Grammar: S -> i E t S | i E t S e S | a
# ===========================================================================

class TestConflictGrammar:

    GRAMMAR = "S -> i E t S e S | i E t S | a\nE -> b"

    def test_is_not_ll1(self):
        result = build_parsing_table_from_text(self.GRAMMAR)
        assert result["success"] is True
        assert result["is_ll1"] is False

    def test_conflicts_detected(self):
        result = build_parsing_table_from_text(self.GRAMMAR)
        assert len(result["conflicts"]) > 0
        # Conflict should involve S and terminal 'e' or 'i'
        conflict_nts = {c["nonterminal"] for c in result["conflicts"]}
        assert "S" in conflict_nts

    def test_conflict_structure(self):
        result = build_parsing_table_from_text(self.GRAMMAR)
        for conflict in result["conflicts"]:
            assert "nonterminal" in conflict
            assert "terminal" in conflict
            assert "productions" in conflict
            assert len(conflict["productions"]) >= 2
