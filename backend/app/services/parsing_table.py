"""
LL(1) Parsing Table Construction.
"""

from typing import Optional, Dict, List
from app.services.grammar_parser import Grammar, parse_grammar, EPSILON
from app.services.first_follow import compute_first_sets, compute_follow_sets, compute_first_of_string


def build_parsing_table(grammar: Grammar, first_sets: dict, follow_sets: dict) -> dict:
    """
    Build the LL(1) predictive parsing table.

    Returns:
        {
            "table": { NT: { terminal: production_string | None } },
            "conflicts": [ { "nonterminal": ..., "terminal": ..., "productions": [...] } ],
            "is_ll1": bool
        }
    """
    # table[A][a] = list of production strings (conflict if > 1)
    table_raw: Dict[str, Dict[str, List[str]]] = {}

    for nt in grammar.nonterminals_ordered():
        table_raw[nt] = {}

    conflicts = []

    for nt in grammar.nonterminals_ordered():
        for prod in grammar.get_productions(nt):
            prod_str = f"{nt} -> {' '.join(prod)}"
            first_alpha = compute_first_of_string(prod, first_sets, grammar)

            for terminal in first_alpha:
                if terminal == EPSILON:
                    continue
                if terminal not in table_raw[nt]:
                    table_raw[nt][terminal] = []
                table_raw[nt][terminal].append(prod_str)

            if EPSILON in first_alpha:
                for b in follow_sets.get(nt, set()):
                    if b not in table_raw[nt]:
                        table_raw[nt][b] = []
                    table_raw[nt][b].append(prod_str)

    # Collect all terminals (including $)
    all_terminals = set(grammar.terminals) | {'$'}
    # Also include any terminals that appear in the table
    for nt_row in table_raw.values():
        all_terminals |= set(nt_row.keys())
    all_terminals = sorted(all_terminals)

    # Build final table and detect conflicts
    table: Dict[str, Dict[str, Optional[str]]] = {}
    is_ll1 = True

    for nt in grammar.nonterminals_ordered():
        table[nt] = {}
        for terminal in all_terminals:
            entries = table_raw[nt].get(terminal, [])
            if len(entries) == 0:
                table[nt][terminal] = None
            elif len(entries) == 1:
                table[nt][terminal] = entries[0]
            else:
                # Conflict
                table[nt][terminal] = entries[0]  # Use first as primary
                conflicts.append({
                    "nonterminal": nt,
                    "terminal": terminal,
                    "productions": entries
                })
                is_ll1 = False

    return {
        "table": table,
        "terminals": all_terminals,
        "nonterminals": grammar.nonterminals_ordered(),
        "conflicts": conflicts,
        "is_ll1": is_ll1
    }


def build_parsing_table_from_text(grammar_text: str, start_symbol: Optional[str] = None) -> dict:
    """Parse grammar and build LL(1) table."""
    parse_result = parse_grammar(grammar_text, start_symbol)
    if not parse_result["success"]:
        return {
            "success": False,
            "error": "Grammar parsing failed: " + "; ".join(parse_result["errors"]),
            "errors": parse_result["errors"]
        }

    grammar = parse_result["grammar"]
    first_sets = compute_first_sets(grammar)
    follow_sets = compute_follow_sets(grammar, first_sets)
    result = build_parsing_table(grammar, first_sets, follow_sets)
    result["success"] = True
    return result
