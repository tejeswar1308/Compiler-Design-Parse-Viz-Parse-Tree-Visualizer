"""
Grammar parser: parses CFG text into an internal Grammar object.

Grammar text format:
  - One production per line: A -> B C | D E
  - Symbols separated by whitespace
  - ε or epsilon represents the empty string
  - First production's LHS is the start symbol (unless overridden)
"""

from typing import Optional

EPSILON = 'ε'


class Grammar:
    """Internal representation of a context-free grammar."""

    def __init__(self):
        self.nonterminals: set = set()
        self.terminals: set = set()
        self.productions: dict = {}   # NT -> list of list of symbols
        self.start_symbol: str = ''
        self._nt_order: list = []     # order nonterminals were defined

    def is_nonterminal(self, sym: str) -> bool:
        return sym in self.nonterminals

    def is_terminal(self, sym: str) -> bool:
        return sym in self.terminals

    def get_productions(self, nt: str) -> list:
        return self.productions.get(nt, [])

    def all_symbols(self) -> set:
        return self.nonterminals | self.terminals

    def nonterminals_ordered(self) -> list:
        return list(self._nt_order)

    def to_text(self) -> str:
        """Serialize grammar back to text form."""
        lines = []
        for nt in self._nt_order:
            prods = self.productions.get(nt, [])
            rhs_parts = []
            for prod in prods:
                rhs_parts.append(' '.join(prod) if prod else EPSILON)
            lines.append(f"{nt} -> {' | '.join(rhs_parts)}")
        return '\n'.join(lines)


def _normalize_epsilon(sym: str) -> str:
    """Normalize epsilon representations."""
    if sym in ('epsilon', 'ε', 'eps', 'EPSILON'):
        return EPSILON
    return sym


def parse_grammar(grammar_text: str, start_symbol: Optional[str] = None) -> dict:
    """
    Parse a grammar text string into a Grammar object.

    Returns:
        {
            "success": bool,
            "grammar": Grammar | None,
            "errors": list[str]
        }
    """
    errors = []
    grammar = Grammar()
    seen_productions: dict = {}  # (nt, tuple(prod)) -> line number

    if not grammar_text or not grammar_text.strip():
        return {"success": False, "grammar": None, "errors": ["Grammar text is empty."]}

    lines = grammar_text.strip().split('\n')
    raw_productions: list = []  # list of (line_no, nt, list of alternatives)

    for line_no, line in enumerate(lines, start=1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Split on '->'
        if '->' not in line:
            errors.append(f"Line {line_no}: Missing '->' in production: '{line}'")
            continue

        arrow_pos = line.index('->')
        lhs = line[:arrow_pos].strip()
        rhs_str = line[arrow_pos + 2:].strip()

        if not lhs:
            errors.append(f"Line {line_no}: Left-hand side is empty.")
            continue

        # LHS must be a single token (no spaces)
        lhs_tokens = lhs.split()
        if len(lhs_tokens) != 1:
            errors.append(f"Line {line_no}: Left-hand side must be a single symbol, got: '{lhs}'")
            continue

        lhs = lhs_tokens[0]

        if not rhs_str:
            errors.append(f"Line {line_no}: Right-hand side is empty for '{lhs}'.")
            continue

        # Split alternatives by '|'
        alternatives_raw = rhs_str.split('|')
        alternatives = []
        for alt_raw in alternatives_raw:
            tokens = alt_raw.strip().split()
            if not tokens:
                # Empty alternative = epsilon
                alt = [EPSILON]
            else:
                alt = [_normalize_epsilon(t) for t in tokens]
            alternatives.append(alt)

        raw_productions.append((line_no, lhs, alternatives))

        # Register nonterminal
        if lhs not in grammar.nonterminals:
            grammar.nonterminals.add(lhs)
            grammar._nt_order.append(lhs)
            grammar.productions[lhs] = []

    if errors and not raw_productions:
        return {"success": False, "grammar": None, "errors": errors}

    if not raw_productions:
        return {"success": False, "grammar": None, "errors": ["No valid productions found."]}

    # First pass: register all LHS as nonterminals
    # (already done above)

    # Second pass: collect all symbols, detect undefined references
    all_defined_nts = set(grammar.nonterminals)

    # Collect all RHS symbols first to determine what's terminal vs nonterminal
    all_rhs_symbols: set = set()
    for _, lhs, alts in raw_productions:
        for alt in alts:
            for sym in alt:
                if sym != EPSILON:
                    all_rhs_symbols.add(sym)

    # Terminals = RHS symbols that are NOT nonterminals
    grammar.terminals = all_rhs_symbols - grammar.nonterminals

    # Third pass: populate productions and check for duplicates
    for line_no, lhs, alternatives in raw_productions:
        for alt in alternatives:
            prod_key = (lhs, tuple(alt))
            if prod_key in seen_productions:
                errors.append(
                    f"Line {line_no}: Duplicate production '{lhs} -> "
                    f"{' '.join(alt)}' (first seen at line {seen_productions[prod_key]})."
                )
            else:
                seen_productions[prod_key] = line_no
                if lhs not in grammar.productions:
                    grammar.productions[lhs] = []
                grammar.productions[lhs].append(alt)

    # Determine start symbol
    if start_symbol:
        if start_symbol not in grammar.nonterminals:
            errors.append(f"Specified start symbol '{start_symbol}' is not a nonterminal in the grammar.")
        else:
            grammar.start_symbol = start_symbol
    else:
        grammar.start_symbol = grammar._nt_order[0] if grammar._nt_order else ''

    if not grammar.start_symbol:
        errors.append("Could not determine start symbol.")

    # Validate: warn about nonterminals used on RHS that are never defined on LHS
    for sym in all_rhs_symbols:
        if sym in grammar.nonterminals and sym not in grammar.productions:
            errors.append(f"Nonterminal '{sym}' is used but never defined.")

    success = len([e for e in errors if not e.startswith('Warning')]) == 0
    # Filter to hard errors only for success flag
    hard_errors = [e for e in errors]
    # Duplicate productions are errors but grammar may still be usable
    # We report success only if there are zero errors
    return {
        "success": len(hard_errors) == 0,
        "grammar": grammar if raw_productions else None,
        "errors": hard_errors
    }


def grammar_to_dict(grammar: Grammar) -> dict:
    """Convert Grammar object to serializable dict."""
    return {
        "nonterminals": list(grammar._nt_order),
        "terminals": sorted(grammar.terminals),
        "productions": {
            nt: [list(p) for p in prods]
            for nt, prods in grammar.productions.items()
        },
        "start_symbol": grammar.start_symbol,
    }
