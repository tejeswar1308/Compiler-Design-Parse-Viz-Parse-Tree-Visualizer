"""
Left Recursion Elimination.

Supports:
1. Immediate left recursion: A -> A α | β  =>  A -> β A', A' -> α A' | ε
2. Indirect left recursion using Dragon Book Algorithm 4.1.
"""

import copy
from typing import Optional
from app.services.grammar_parser import Grammar, parse_grammar, EPSILON


def _has_immediate_left_recursion(grammar: Grammar, nt: str) -> bool:
    """Return True if nt has immediate left recursion."""
    for prod in grammar.get_productions(nt):
        if prod and prod[0] == nt:
            return True
    return False


def _has_any_left_recursion(grammar: Grammar) -> list:
    """Return list of nonterminals that have immediate left recursion."""
    result = []
    for nt in grammar.nonterminals_ordered():
        if _has_immediate_left_recursion(grammar, nt):
            result.append(nt)
    return result


def _make_new_name(base: str, existing: set) -> str:
    """
    Generate a collision-free name for a new nonterminal based on `base`.
    A' -> A_prime, then A_prime1, A_prime2, ...
    """
    candidate = base + "_prime"
    if candidate not in existing:
        return candidate
    i = 1
    while True:
        candidate = base + f"_prime{i}"
        if candidate not in existing:
            return candidate
        i += 1


def _eliminate_immediate(grammar: Grammar, nt: str, steps: list) -> Grammar:
    """
    Eliminate immediate left recursion for `nt` in `grammar`.
    Modifies grammar in-place (on a copy) and appends to steps.
    Returns modified grammar.
    """
    prods = grammar.get_productions(nt)
    recursive = []   # productions of the form nt -> nt α
    non_recursive = []

    for prod in prods:
        if prod and prod[0] == nt:
            recursive.append(prod[1:])  # the α part (may be empty)
        else:
            non_recursive.append(prod)

    if not recursive:
        return grammar

    # Create new nonterminal nt'
    all_existing = set(grammar.nonterminals) | set(grammar.terminals)
    prime_nt = _make_new_name(nt, all_existing)

    # A  -> β A' for each β in non_recursive
    # A' -> α A' for each α in recursive
    # A' -> ε

    new_prods_nt = []
    for beta in non_recursive:
        new_prods_nt.append(beta + [prime_nt])

    if not new_prods_nt:
        # A -> ε A' (edge case: A was purely left recursive)
        new_prods_nt.append([EPSILON, prime_nt])

    new_prods_prime = []
    for alpha in recursive:
        if alpha:
            new_prods_prime.append(alpha + [prime_nt])
        else:
            # A -> A (empty suffix) is weird but handle it: A' -> A'
            new_prods_prime.append([prime_nt])
    new_prods_prime.append([EPSILON])

    grammar.productions[nt] = new_prods_nt
    grammar.productions[prime_nt] = new_prods_prime
    grammar.nonterminals.add(prime_nt)
    grammar._nt_order.append(prime_nt)

    step_desc = (
        f"Eliminate immediate left recursion for '{nt}':\n"
        f"  New rule: {nt} -> {' | '.join(' '.join(p) for p in new_prods_nt)}\n"
        f"  New rule: {prime_nt} -> {' | '.join(' '.join(p) for p in new_prods_prime)}"
    )
    steps.append({
        "step": len(steps) + 1,
        "description": step_desc,
        "grammar_state": grammar.to_text()
    })
    return grammar


def _substitute(grammar: Grammar, ai: str, aj: str) -> None:
    """
    Substitute all productions of aj into productions of ai where ai -> aj γ.
    Modifies grammar in-place.
    """
    aj_prods = grammar.get_productions(aj)
    new_ai_prods = []
    for prod in grammar.get_productions(ai):
        if prod and prod[0] == aj:
            gamma = prod[1:]
            for aj_prod in aj_prods:
                if aj_prod == [EPSILON]:
                    new_ai_prods.append(list(gamma) if gamma else [EPSILON])
                else:
                    new_ai_prods.append(list(aj_prod) + list(gamma))
        else:
            new_ai_prods.append(prod)
    grammar.productions[ai] = new_ai_prods


def eliminate_left_recursion(grammar_text: str, start_symbol: Optional[str] = None) -> dict:
    """
    Full left recursion elimination (immediate + indirect).
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

    # Detect which nonterminals have immediate left recursion before transformation
    recursive_nts = _has_any_left_recursion(grammar)
    has_lr = len(recursive_nts) > 0

    # Check for indirect left recursion (simplified: check if after substitution any arise)
    # We run the algorithm and track
    steps = []
    g = copy.deepcopy(grammar)

    ordered_nts = list(g.nonterminals_ordered())  # snapshot of original NTs

    warnings = []

    # Dragon Book Algorithm 4.1
    for i, ai in enumerate(ordered_nts):
        # Step 1: For each j < i, substitute Aj productions into Ai
        for j in range(i):
            aj = ordered_nts[j]
            before = g.productions.get(ai, [])
            _substitute(g, ai, aj)
            after = g.productions.get(ai, [])
            if before != after:
                steps.append({
                    "step": len(steps) + 1,
                    "description": (
                        f"Substitute {aj} into {ai}: replace '{ai} -> {aj} ...' "
                        f"with {aj}'s productions"
                    ),
                    "grammar_state": g.to_text()
                })

        # Step 2: Eliminate immediate left recursion for Ai
        if _has_immediate_left_recursion(g, ai):
            if ai not in recursive_nts:
                recursive_nts.append(ai)
                has_lr = True
            _eliminate_immediate(g, ai, steps)

    if not steps:
        steps.append({
            "step": 1,
            "description": "No left recursion found. Grammar is unchanged.",
            "grammar_state": g.to_text()
        })

    return {
        "original_grammar": original_text,
        "has_left_recursion": has_lr,
        "recursive_nonterminals": recursive_nts,
        "steps": steps,
        "transformed_grammar": g.to_text(),
        "success": True,
        "warnings": warnings
    }
