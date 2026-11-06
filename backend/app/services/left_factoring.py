"""
Left Factoring.

For each nonterminal A with productions sharing a common prefix,
factor out the longest common prefix repeatedly until no common prefixes remain.
"""

import copy
from typing import Optional, List
from app.services.grammar_parser import Grammar, parse_grammar, EPSILON


def _longest_common_prefix(productions: List[List[str]]) -> List[str]:
    """
    Find the longest common prefix shared by at least two of the given productions.
    Returns the prefix (may be empty list if none).
    """
    if len(productions) < 2:
        return []

    # Group productions by first symbol
    groups: dict = {}
    for prod in productions:
        if prod and prod != [EPSILON]:
            first = prod[0]
            groups.setdefault(first, []).append(prod)

    # Find the group with the most members (or first group with >= 2)
    best_prefix: List[str] = []
    for first_sym, group in groups.items():
        if len(group) >= 2:
            # Compute longest common prefix of this group
            lcp = list(group[0])
            for prod in group[1:]:
                new_lcp = []
                for a, b in zip(lcp, prod):
                    if a == b:
                        new_lcp.append(a)
                    else:
                        break
                lcp = new_lcp
                if not lcp:
                    break
            if len(lcp) > len(best_prefix):
                best_prefix = lcp

    return best_prefix


def _make_new_name(base: str, existing: set) -> str:
    """Generate a collision-free nonterminal name."""
    candidate = base + "_f"
    if candidate not in existing:
        return candidate
    i = 1
    while True:
        candidate = base + f"_f{i}"
        if candidate not in existing:
            return candidate
        i += 1


def _factor_once(grammar: Grammar, nt: str, steps: list) -> bool:
    """
    Perform one round of left factoring for nonterminal `nt`.
    Returns True if any factoring was performed.
    """
    prods = grammar.get_productions(nt)
    prefix = _longest_common_prefix(prods)

    if not prefix:
        return False

    # Separate productions into those sharing the prefix and others
    prefix_len = len(prefix)
    with_prefix = []
    without_prefix = []

    for prod in prods:
        if len(prod) >= prefix_len and prod[:prefix_len] == prefix:
            with_prefix.append(prod)
        else:
            without_prefix.append(prod)

    if len(with_prefix) < 2:
        return False

    # Create new nonterminal
    all_existing = grammar.nonterminals | grammar.terminals
    new_nt = _make_new_name(nt, all_existing)

    # Remainders after removing the prefix
    remainders = []
    for prod in with_prefix:
        remainder = prod[prefix_len:]
        if not remainder:
            remainders.append([EPSILON])
        else:
            remainders.append(remainder)

    # Updated productions for nt
    new_prods_nt = without_prefix + [prefix + [new_nt]]
    grammar.productions[nt] = new_prods_nt

    # Productions for new nonterminal
    grammar.productions[new_nt] = remainders
    grammar.nonterminals.add(new_nt)
    grammar._nt_order.append(new_nt)

    prefix_str = ' '.join(prefix)
    step_desc = (
        f"Left factor '{nt}' on common prefix '{prefix_str}':\n"
        f"  {nt} -> {' | '.join(' '.join(p) for p in new_prods_nt)}\n"
        f"  {new_nt} -> {' | '.join(' '.join(p) for p in remainders)}"
    )
    steps.append({
        "step": len(steps) + 1,
        "description": step_desc,
        "grammar_state": grammar.to_text()
    })
    return True


def left_factor(grammar_text: str, start_symbol: Optional[str] = None) -> dict:
    """
    Perform left factoring on the grammar.
    Repeatedly factors until no more common prefixes exist.
    """
    parse_result = parse_grammar(grammar_text, start_symbol)
    if not parse_result["success"]:
        return {
            "success": False,
            "error": "Grammar parsing failed: " + "; ".join(parse_result["errors"]),
            "errors": parse_result["errors"]
        }

    grammar = parse_result["grammar"]
    original_text = grammar.to_text()

    # Check if any factoring is needed
    needs_factoring = False
    for nt in grammar.nonterminals_ordered():
        if _longest_common_prefix(grammar.get_productions(nt)):
            needs_factoring = True
            break

    steps = []
    g = copy.deepcopy(grammar)

    # Iterate until convergence (max iterations as safety)
    max_iterations = 100
    iteration = 0
    changed = True
    while changed and iteration < max_iterations:
        changed = False
        for nt in list(g.nonterminals_ordered()):
            if _factor_once(g, nt, steps):
                changed = True
        iteration += 1

    if not steps:
        steps.append({
            "step": 1,
            "description": "No common prefixes found. Grammar does not need left factoring.",
            "grammar_state": g.to_text()
        })

    return {
        "original_grammar": original_text,
        "needs_factoring": needs_factoring,
        "steps": steps,
        "transformed_grammar": g.to_text(),
        "success": True
    }
