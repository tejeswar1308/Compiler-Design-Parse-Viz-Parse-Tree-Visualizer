"""
FIRST and FOLLOW set computation using fixed-point iteration.
"""

from typing import Optional, Set, Dict, List
from app.services.grammar_parser import Grammar, parse_grammar, EPSILON


def compute_first_of_string(
    string: List[str],
    first_sets: Dict[str, Set[str]],
    grammar: Grammar
) -> Set[str]:
    r"""
    Compute FIRST of a sequence of symbols.
    FIRST(X1 X2 ... Xk):
      - Start with FIRST(X1) \ {ε}
      - If ε ∈ FIRST(X1), add FIRST(X2) \ {ε}, etc.
      - If ε ∈ FIRST(all Xi), add ε
    """
    result: Set[str] = set()
    if not string or string == [EPSILON]:
        result.add(EPSILON)
        return result

    all_nullable = True
    for sym in string:
        if sym == EPSILON:
            # ε in the string contributes ε but doesn't block
            continue
        sym_first = first_sets.get(sym, set())
        if not sym_first:
            # Terminal with no computed FIRST (raw terminal)
            result.add(sym)
            all_nullable = False
            break
        result |= (sym_first - {EPSILON})
        if EPSILON not in sym_first:
            all_nullable = False
            break

    if all_nullable:
        result.add(EPSILON)

    return result


def compute_first_sets(grammar: Grammar) -> Dict[str, Set[str]]:
    """
    Compute FIRST sets for all symbols using fixed-point iteration.
    """
    first: Dict[str, Set[str]] = {}

    # Initialize
    for sym in grammar.terminals:
        first[sym] = {sym}
    first[EPSILON] = {EPSILON}

    for nt in grammar.nonterminals:
        first[nt] = set()

    # Fixed-point iteration
    changed = True
    while changed:
        changed = False
        for nt in grammar.nonterminals_ordered():
            for prod in grammar.get_productions(nt):
                added = compute_first_of_string(prod, first, grammar)
                before_size = len(first[nt])
                first[nt] |= added
                if len(first[nt]) > before_size:
                    changed = True

    return first


def compute_follow_sets(grammar: Grammar, first_sets: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    """
    Compute FOLLOW sets for all nonterminals using fixed-point iteration.
    """
    follow: Dict[str, Set[str]] = {}
    for nt in grammar.nonterminals:
        follow[nt] = set()

    # FOLLOW(start) contains $
    follow[grammar.start_symbol].add('$')

    # Fixed-point iteration
    changed = True
    while changed:
        changed = False
        for nt in grammar.nonterminals_ordered():
            for prod in grammar.get_productions(nt):
                # For each symbol in the production
                for i, sym in enumerate(prod):
                    if not grammar.is_nonterminal(sym):
                        continue
                    # Beta is what comes after sym in this production
                    beta = prod[i + 1:]
                    # Compute FIRST(beta)
                    first_beta = compute_first_of_string(beta, first_sets, grammar) if beta else {EPSILON}

                    before_size = len(follow[sym])
                    follow[sym] |= (first_beta - {EPSILON})

                    # If ε ∈ FIRST(beta), add FOLLOW(nt) to FOLLOW(sym)
                    if EPSILON in first_beta:
                        follow[sym] |= follow[nt]

                    if len(follow[sym]) > before_size:
                        changed = True

    return follow


def compute_nullable(grammar: Grammar, first_sets: Dict[str, Set[str]]) -> List[str]:
    """Return list of nullable nonterminals (ε in FIRST(A))."""
    return [nt for nt in grammar.nonterminals_ordered() if EPSILON in first_sets.get(nt, set())]


def compute_first_follow(grammar_text: str, start_symbol: Optional[str] = None) -> dict:
    """
    Compute FIRST and FOLLOW sets for a grammar.
    Returns serializable dict.
    """
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
    nullable = compute_nullable(grammar, first_sets)

    # Build step-by-step trace
    steps = _build_steps(grammar, first_sets, follow_sets)

    # Serialize: only output FIRST sets for nonterminals + terminals (not internal ε key)
    serialized_first = {}
    for nt in grammar.nonterminals_ordered():
        serialized_first[nt] = sorted(first_sets.get(nt, set()))

    serialized_follow = {}
    for nt in grammar.nonterminals_ordered():
        serialized_follow[nt] = sorted(follow_sets.get(nt, set()))

    return {
        "success": True,
        "first_sets": serialized_first,
        "follow_sets": serialized_follow,
        "nullable": nullable,
        "steps": steps
    }


def _build_steps(grammar: Grammar, first_sets: dict, follow_sets: dict) -> list:
    """Build human-readable computation steps."""
    steps = []

    # FIRST computation steps
    steps.append({
        "phase": "FIRST",
        "description": "Initialize FIRST sets",
        "detail": (
            "Terminals: FIRST(a) = {a} for each terminal a. "
            "Nonterminals: FIRST(A) = {} initially."
        )
    })

    for nt in grammar.nonterminals_ordered():
        for prod in grammar.get_productions(nt):
            prod_str = ' '.join(prod)
            first_prod = compute_first_of_string(prod, first_sets, grammar)
            steps.append({
                "phase": "FIRST",
                "description": f"Process production: {nt} -> {prod_str}",
                "detail": (
                    f"FIRST({prod_str}) = {{{', '.join(sorted(first_prod))}}} "
                    f"is added to FIRST({nt})"
                )
            })

    for nt in grammar.nonterminals_ordered():
        steps.append({
            "phase": "FIRST_RESULT",
            "description": f"FIRST({nt}) = {{{', '.join(sorted(first_sets.get(nt, set())))}}}",
            "detail": ""
        })

    # FOLLOW steps
    steps.append({
        "phase": "FOLLOW",
        "description": f"Initialize FOLLOW: $ ∈ FOLLOW({grammar.start_symbol})",
        "detail": "The end-of-input marker $ is placed in the FOLLOW set of the start symbol."
    })

    for nt in grammar.nonterminals_ordered():
        for prod in grammar.get_productions(nt):
            for i, sym in enumerate(prod):
                if not grammar.is_nonterminal(sym):
                    continue
                beta = prod[i + 1:]
                beta_str = ' '.join(beta) if beta else 'ε'
                steps.append({
                    "phase": "FOLLOW",
                    "description": f"Production {nt} -> {' '.join(prod)}: compute FOLLOW({sym})",
                    "detail": (
                        f"β = '{beta_str}'. "
                        f"Add FIRST(β)\\{{ε}} to FOLLOW({sym}). "
                        f"If ε ∈ FIRST(β), add FOLLOW({nt}) to FOLLOW({sym})."
                    )
                })

    for nt in grammar.nonterminals_ordered():
        steps.append({
            "phase": "FOLLOW_RESULT",
            "description": f"FOLLOW({nt}) = {{{', '.join(sorted(follow_sets.get(nt, set())))}}}",
            "detail": ""
        })

    return steps
