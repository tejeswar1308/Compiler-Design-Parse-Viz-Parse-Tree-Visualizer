"""
Practice Question Generator.

Generates and checks practice questions using real grammar algorithms.
"""

import uuid
import random
from typing import Optional, Dict, Any, List

from app.services.grammar_parser import parse_grammar, Grammar, EPSILON
from app.services.left_recursion import eliminate_left_recursion, _has_immediate_left_recursion
from app.services.first_follow import compute_first_sets, compute_follow_sets
from app.services.parsing_table import build_parsing_table
from app.services.left_factoring import left_factor, _longest_common_prefix


# Pool of template grammars for question generation
GRAMMAR_POOL = [
    {
        "grammar": "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id",
        "name": "Arithmetic (left-recursive)"
    },
    {
        "grammar": "E -> T E_prime\nE_prime -> + T E_prime | ε\nT -> F T_prime\nT_prime -> * F T_prime | ε\nF -> ( E ) | id",
        "name": "Arithmetic LL(1)"
    },
    {
        "grammar": "S -> a B\nB -> b | ε",
        "name": "Simple S->aB"
    },
    {
        "grammar": "A -> B C\nB -> b | ε\nC -> c | ε",
        "name": "Nullable B and C"
    },
    {
        "grammar": "S -> i E t S S_prime | a\nS_prime -> e S | ε\nE -> b",
        "name": "Dangling else (LL1)"
    },
    {
        "grammar": "A -> A a | b",
        "name": "Simple immediate left recursion"
    },
    {
        "grammar": "S -> A a | b\nA -> S b | ε",
        "name": "Indirect left recursion"
    },
    {
        "grammar": "X -> a b c | a b d | a e",
        "name": "Needs left factoring"
    },
    {
        "grammar": "P -> P + Q | Q\nQ -> Q * R | R\nR -> id | ( P )",
        "name": "P+Q*R left-recursive"
    },
    {
        "grammar": "S -> if E then S else S | if E then S | stmt\nE -> expr",
        "name": "If-then-else conflict"
    },
]

QUESTION_TYPES = [
    "has_left_recursion",
    "compute_first",
    "compute_follow",
    "is_ll1",
    "left_factor_step"
]


def _grammar_has_immediate_lr(grammar: Grammar) -> bool:
    for nt in grammar.nonterminals:
        if _has_immediate_left_recursion(grammar, nt):
            return True
    return False


def _generate_has_left_recursion(grammar_entry: dict) -> dict:
    grammar_text = grammar_entry["grammar"]
    parse_result = parse_grammar(grammar_text)
    if not parse_result["success"]:
        return None
    grammar = parse_result["grammar"]
    has_lr = _grammar_has_immediate_lr(grammar)
    correct = "Yes" if has_lr else "No"

    recursive_nts = [nt for nt in grammar.nonterminals if _has_immediate_left_recursion(grammar, nt)]
    if has_lr:
        explanation = (
            f"Yes. The grammar has immediate left recursion. "
            f"Nonterminals with left recursion: {', '.join(recursive_nts)}. "
            f"A production A -> A ... shows A derives itself at the leftmost position."
        )
    else:
        explanation = (
            "No. No nonterminal has a production of the form A -> A .... "
            "The grammar does not exhibit immediate left recursion."
        )

    return {
        "id": f"q-{uuid.uuid4()}",
        "type": "has_left_recursion",
        "question": f"Does this grammar have immediate left recursion?\n\n{grammar_text}",
        "grammar": grammar_text,
        "options": ["Yes", "No"],
        "correct_answer": correct,
        "explanation": explanation
    }


def _generate_compute_first(grammar_entry: dict) -> dict:
    grammar_text = grammar_entry["grammar"]
    parse_result = parse_grammar(grammar_text)
    if not parse_result["success"]:
        return None
    grammar = parse_result["grammar"]
    first_sets = compute_first_sets(grammar)

    nts = grammar.nonterminals_ordered()
    if not nts:
        return None

    target_nt = random.choice(nts)
    correct_first = sorted(first_sets.get(target_nt, set()))
    correct_str = "{" + ", ".join(correct_first) + "}"

    # Generate plausible wrong options
    all_terminals = sorted(grammar.terminals)
    wrong_options = []
    # Option: missing one symbol
    if len(correct_first) > 1:
        wrong1 = sorted(random.sample(correct_first, len(correct_first) - 1))
        wrong_options.append("{" + ", ".join(wrong1) + "}")
    # Option: add a random terminal
    extras = [t for t in all_terminals if t not in correct_first]
    if extras:
        wrong2 = sorted(correct_first + [random.choice(extras)])
        wrong_options.append("{" + ", ".join(wrong2) + "}")
    # Option: empty set
    if correct_first:
        wrong_options.append("{}")

    # Build unique options pool
    options_pool = list({correct_str} | set(wrong_options[:3]))
    random.shuffle(options_pool)
    if len(options_pool) < 2:
        options_pool.append("{" + ", ".join(all_terminals[:2]) + "}" if all_terminals else "{a, b}")
    options_pool = options_pool[:4]
    if correct_str not in options_pool:
        options_pool[0] = correct_str

    explanation = (
        f"FIRST({target_nt}) = {correct_str}. "
        f"This is computed by looking at what terminals can appear first "
        f"when {target_nt} is expanded. "
        f"ε (epsilon) appears if {target_nt} can derive the empty string."
    )

    return {
        "id": f"q-{uuid.uuid4()}",
        "type": "compute_first",
        "question": (
            f"What is FIRST({target_nt}) for the following grammar?\n\n{grammar_text}"
        ),
        "grammar": grammar_text,
        "target_symbol": target_nt,
        "options": options_pool,
        "correct_answer": correct_str,
        "explanation": explanation
    }


def _generate_compute_follow(grammar_entry: dict) -> dict:
    grammar_text = grammar_entry["grammar"]
    parse_result = parse_grammar(grammar_text)
    if not parse_result["success"]:
        return None
    grammar = parse_result["grammar"]
    first_sets = compute_first_sets(grammar)
    follow_sets = compute_follow_sets(grammar, first_sets)

    nts = grammar.nonterminals_ordered()
    if not nts:
        return None

    target_nt = random.choice(nts)
    correct_follow = sorted(follow_sets.get(target_nt, set()))
    correct_str = "{" + ", ".join(correct_follow) + "}"

    all_terminals = sorted(grammar.terminals | {'$'})
    wrong_options = []
    if len(correct_follow) > 1:
        wrong1 = sorted(random.sample(correct_follow, len(correct_follow) - 1))
        wrong_options.append("{" + ", ".join(wrong1) + "}")
    extras = [t for t in all_terminals if t not in correct_follow]
    if extras:
        wrong2 = sorted(correct_follow + [random.choice(extras)])
        wrong_options.append("{" + ", ".join(wrong2) + "}")
    wrong_options.append("{ $ }")

    options_pool = list({correct_str} | set(wrong_options[:3]))
    random.shuffle(options_pool)
    if len(options_pool) < 2:
        options_pool.append("{a, $}")
    options_pool = options_pool[:4]
    if correct_str not in options_pool:
        options_pool[0] = correct_str

    explanation = (
        f"FOLLOW({target_nt}) = {correct_str}. "
        f"$ ∈ FOLLOW({grammar.start_symbol}) because it is the start symbol. "
        f"We add symbols to FOLLOW({target_nt}) by examining all productions "
        f"where {target_nt} appears on the right-hand side."
    )

    return {
        "id": f"q-{uuid.uuid4()}",
        "type": "compute_follow",
        "question": (
            f"What is FOLLOW({target_nt}) for the following grammar?\n\n{grammar_text}"
        ),
        "grammar": grammar_text,
        "target_symbol": target_nt,
        "options": options_pool,
        "correct_answer": correct_str,
        "explanation": explanation
    }


def _generate_is_ll1(grammar_entry: dict) -> dict:
    grammar_text = grammar_entry["grammar"]
    parse_result = parse_grammar(grammar_text)
    if not parse_result["success"]:
        return None
    grammar = parse_result["grammar"]
    first_sets = compute_first_sets(grammar)
    follow_sets = compute_follow_sets(grammar, first_sets)
    table_result = build_parsing_table(grammar, first_sets, follow_sets)
    is_ll1 = table_result["is_ll1"]
    conflicts = table_result["conflicts"]

    correct = "Yes" if is_ll1 else "No"
    if is_ll1:
        explanation = (
            "Yes. The grammar is LL(1). The predictive parsing table has no conflicts: "
            "each cell M[A][a] contains at most one production."
        )
    else:
        conflict_descriptions = []
        for c in conflicts[:3]:
            conflict_descriptions.append(
                f"M[{c['nonterminal']}][{c['terminal']}] has {len(c['productions'])} productions: "
                + ", ".join(f"'{p}'" for p in c['productions'])
            )
        explanation = (
            "No. The grammar is NOT LL(1). Parsing table conflicts exist:\n"
            + "\n".join(conflict_descriptions)
        )

    return {
        "id": f"q-{uuid.uuid4()}",
        "type": "is_ll1",
        "question": f"Is the following grammar LL(1)?\n\n{grammar_text}",
        "grammar": grammar_text,
        "options": ["Yes", "No"],
        "correct_answer": correct,
        "explanation": explanation
    }


def _generate_left_factor_step(grammar_entry: dict) -> dict:
    grammar_text = grammar_entry["grammar"]
    parse_result = parse_grammar(grammar_text)
    if not parse_result["success"]:
        return None
    grammar = parse_result["grammar"]

    # Find a nonterminal that needs left factoring
    target_nt = None
    target_prefix = None
    for nt in grammar.nonterminals_ordered():
        prefix = _longest_common_prefix(grammar.get_productions(nt))
        if prefix:
            target_nt = nt
            target_prefix = prefix
            break

    if not target_nt:
        return None

    prods = grammar.get_productions(target_nt)
    prods_str = " | ".join(" ".join(p) for p in prods)
    correct = " ".join(target_prefix)

    # Wrong options
    all_syms = list(grammar.terminals | grammar.nonterminals)
    wrong1 = random.choice(all_syms) if all_syms else "x"
    wrong2 = " ".join(target_prefix + [random.choice(all_syms)]) if all_syms and target_prefix else "z"
    wrong3 = "ε"

    options_pool = list({correct, str(wrong1), wrong2, wrong3})
    random.shuffle(options_pool)
    if len(options_pool) < 2:
        options_pool.append("a b")
    options_pool = options_pool[:4]
    if correct not in options_pool:
        options_pool[0] = correct

    explanation = (
        f"The longest common prefix for {target_nt}'s productions ({prods_str}) is '{correct}'. "
        f"Left factoring introduces a new nonterminal to factor this out."
    )

    return {
        "id": f"q-{uuid.uuid4()}",
        "type": "left_factor_step",
        "question": (
            f"What is the longest common prefix in the productions of {target_nt}?\n\n"
            f"{target_nt} -> {prods_str}"
        ),
        "grammar": grammar_text,
        "target_symbol": target_nt,
        "options": options_pool,
        "correct_answer": correct,
        "explanation": explanation
    }


_GENERATORS = {
    "has_left_recursion": _generate_has_left_recursion,
    "compute_first": _generate_compute_first,
    "compute_follow": _generate_compute_follow,
    "is_ll1": _generate_is_ll1,
    "left_factor_step": _generate_left_factor_step,
}


TYPE_ALIASES = {
    "left_recursion": "has_left_recursion",
    "has_left_recursion": "has_left_recursion",
    "first_set": "compute_first",
    "compute_first": "compute_first",
    "first": "compute_first",
    "follow_set": "compute_follow",
    "compute_follow": "compute_follow",
    "follow": "compute_follow",
    "is_ll1": "is_ll1",
    "ll1": "is_ll1",
    "left_factor": "left_factor_step",
    "left_factoring": "left_factor_step",
    "left_factor_step": "left_factor_step",
}


def generate_question(question_type: Optional[str] = None) -> dict:
    """
    Generate a practice question of the given type (or random type).
    Tries multiple grammar entries until one succeeds.
    """
    if question_type:
        mapped_type = TYPE_ALIASES.get(question_type.lower())
        if not mapped_type or mapped_type not in _GENERATORS:
            return {
                "error": f"Unknown question type '{question_type}'. "
                         f"Valid types: {', '.join(QUESTION_TYPES)}"
            }
        q_type = mapped_type
    else:
        q_type = random.choice(QUESTION_TYPES)

    generator = _GENERATORS[q_type]

    # Shuffle grammar pool and try until we get a valid question
    pool = list(GRAMMAR_POOL)
    random.shuffle(pool)

    for entry in pool:
        question = generator(entry)
        if question:
            return question

    return {"error": f"Could not generate question of type '{q_type}'."}


def check_answer(question_data: dict, user_answer: str) -> dict:
    """
    Check a user's answer against the correct answer for a question.

    Returns:
        {
            "correct": bool,
            "correct_answer": str,
            "explanation": str,
            "step_by_step": list
        }
    """
    correct_answer = question_data.get("correct_answer", "")
    explanation = question_data.get("explanation", "")
    q_type = question_data.get("type", "")
    grammar_text = question_data.get("grammar", "")

    is_correct = user_answer.strip() == correct_answer.strip()

    step_by_step = _build_step_by_step(q_type, grammar_text, question_data)

    return {
        "correct": is_correct,
        "correct_answer": correct_answer,
        "explanation": explanation,
        "step_by_step": step_by_step
    }


def _build_step_by_step(q_type: str, grammar_text: str, question_data: dict) -> List[str]:
    """Build step-by-step solution for a question as readable strings."""
    steps: List[str] = []
    parse_result = parse_grammar(grammar_text)
    if not parse_result["success"]:
        return ["Could not parse grammar for step-by-step solution."]

    grammar = parse_result["grammar"]

    if q_type == "has_left_recursion":
        steps.append("Check each nonterminal for productions of the form A -> A ...")
        for nt in grammar.nonterminals_ordered():
            has_lr = _has_immediate_left_recursion(grammar, nt)
            prods = [" ".join(p) for p in grammar.get_productions(nt)]
            steps.append(
                f"Checking {nt}: productions = {prods}. Immediate LR: {has_lr}"
            )

    elif q_type in ("compute_first", "compute_follow"):
        first_sets = compute_first_sets(grammar)
        steps.append("Compute FIRST sets using fixed-point iteration until convergence:")
        for nt in grammar.nonterminals_ordered():
            steps.append(f"FIRST({nt}) = {{{', '.join(sorted(first_sets.get(nt, set())))}}}")
        if q_type == "compute_follow":
            follow_sets = compute_follow_sets(grammar, first_sets)
            steps.append("Compute FOLLOW sets by propagating symbols from production RHS:")
            for nt in grammar.nonterminals_ordered():
                steps.append(f"FOLLOW({nt}) = {{{', '.join(sorted(follow_sets.get(nt, set())))}}}")

    elif q_type == "is_ll1":
        first_sets = compute_first_sets(grammar)
        follow_sets = compute_follow_sets(grammar, first_sets)
        table_result = build_parsing_table(grammar, first_sets, follow_sets)
        steps.append("Construct the LL(1) parsing table using FIRST and FOLLOW sets.")
        if table_result["is_ll1"]:
            steps.append("No cells contain multiple productions. Therefore, the grammar is LL(1).")
        else:
            steps.append(f"Found conflicts in the parsing table:")
            for c in table_result["conflicts"][:3]:
                steps.append(
                    f"Conflict at M[{c['nonterminal']}][{c['terminal']}]: {c['productions']}"
                )
            steps.append("Because conflicts exist, the grammar is NOT LL(1).")

    elif q_type == "left_factor_step":
        target_nt = question_data.get("target_symbol", "")
        if target_nt:
            prods = grammar.get_productions(target_nt)
            steps.append(f"List productions of {target_nt}: {[' '.join(p) for p in prods]}")
            prefix = _longest_common_prefix(prods)
            steps.append(f"Longest common prefix among alternatives: '{' '.join(prefix)}'")
            steps.append(f"Left factoring replaces {target_nt} with factored prefix and new primed nonterminal.")

    return steps
