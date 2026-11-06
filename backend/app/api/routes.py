"""
FastAPI route definitions for ParseViz API.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any

from app.models.grammar import (
    GrammarInput,
    ParseRequest,
    PracticeCheckRequest,
    TransformRequest,
)
from app.services.grammar_parser import parse_grammar, grammar_to_dict
from app.services.left_recursion import eliminate_left_recursion
from app.services.left_factoring import left_factor
from app.services.first_follow import compute_first_follow, compute_first_sets, compute_follow_sets
from app.services.parsing_table import build_parsing_table, build_parsing_table_from_text
from app.services.predictive_parser import predictive_parse
from app.services.parse_tree import build_parse_tree
from app.services.tokenizer import smart_tokenize
from app.services.practice_generator import generate_question, check_answer

router = APIRouter()

SAMPLE_EXAMPLES = [
    {
        "name": "Arithmetic Expressions (Left-Recursive)",
        "grammar": "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id",
        "grammar_text": "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id",
        "description": "Standard arithmetic expression grammar requiring left recursion elimination."
    },
    {
        "name": "Grammar Requiring Left Factoring",
        "grammar": "S -> i E t S | i E t S e S | a\nE -> b",
        "grammar_text": "S -> i E t S | i E t S e S | a\nE -> b",
        "description": "Dangling-else grammar with common prefixes requiring left factoring."
    },
    {
        "name": "Simple LL(1) Grammar",
        "grammar": "S -> a B\nB -> b | ε",
        "grammar_text": "S -> a B\nB -> b | ε",
        "description": "A clean, conflict-free LL(1) grammar."
    },
    {
        "name": "Epsilon-Production Grammar",
        "grammar": "A -> B C\nB -> b | ε\nC -> c | ε",
        "grammar_text": "A -> B C\nB -> b | ε\nC -> c | ε",
        "description": "Grammar with multiple nullable nonterminals demonstrating epsilon propagation."
    },
    {
        "name": "Grammar with LL(1) Conflicts",
        "grammar": "S -> A a | b\nA -> b | ε",
        "grammar_text": "S -> A a | b\nA -> b | ε",
        "description": "Grammar producing FIRST/FIRST conflict at M[S, 'b']."
    },
    {
        "name": "Transformed Arithmetic LL(1)",
        "grammar": (
            "E -> T E'\n"
            "E' -> + T E' | ε\n"
            "T -> F T'\n"
            "T' -> * F T' | ε\n"
            "F -> ( E ) | id"
        ),
        "grammar_text": (
            "E -> T E'\n"
            "E' -> + T E' | ε\n"
            "T -> F T'\n"
            "T' -> * F T' | ε\n"
            "F -> ( E ) | id"
        ),
        "description": "Arithmetic grammar after left recursion elimination, directly parseable in LL(1)."
    }
]


# ---------------------------------------------------------------------------
# Health & Examples
# ---------------------------------------------------------------------------

@router.get("/health")
def health():
    return {"status": "ok", "service": "ParseViz API", "version": "1.0.0"}


@router.get("/examples")
def get_examples():
    return {"examples": SAMPLE_EXAMPLES}


@router.get("/grammar/examples")
def get_grammar_examples():
    return SAMPLE_EXAMPLES


# ---------------------------------------------------------------------------
# Grammar Validation
# ---------------------------------------------------------------------------

@router.post("/grammar/validate")
def validate_grammar(body: GrammarInput):
    result = parse_grammar(body.grammar_text, body.start_symbol)
    if result["success"]:
        grammar = result["grammar"]
        return {
            "valid": True,
            "success": True,
            "grammar": grammar_to_dict(grammar),
            "errors": []
        }
    else:
        return {
            "valid": False,
            "success": False,
            "grammar": None,
            "errors": result["errors"]
        }


# ---------------------------------------------------------------------------
# Transformations (Supports both naming conventions)
# ---------------------------------------------------------------------------

@router.post("/grammar/transform/left-recursion")
@router.post("/grammar/eliminate-left-recursion")
def transform_left_recursion(body: TransformRequest):
    result = eliminate_left_recursion(body.grammar_text, body.start_symbol)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Transformation failed"))
    return result


@router.post("/grammar/transform/left-factoring")
@router.post("/grammar/left-factoring")
def transform_left_factoring(body: TransformRequest):
    result = left_factor(body.grammar_text, body.start_symbol)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Transformation failed"))
    return result


# ---------------------------------------------------------------------------
# FIRST / FOLLOW
# ---------------------------------------------------------------------------

@router.post("/grammar/first-follow")
def first_follow(body: GrammarInput):
    result = compute_first_follow(body.grammar_text, body.start_symbol)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Computation failed"))
    return result


# ---------------------------------------------------------------------------
# Parsing Table
# ---------------------------------------------------------------------------

@router.post("/grammar/parsing-table")
def parsing_table(body: GrammarInput):
    result = build_parsing_table_from_text(body.grammar_text, body.start_symbol)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Table construction failed"))
    return result


# ---------------------------------------------------------------------------
# Full Parse (tokenize + parse + tree)
# ---------------------------------------------------------------------------

@router.post("/grammar/parse")
def parse_input(body: ParseRequest):
    """
    Full pipeline:
    1. (Optionally) Transform the grammar
    2. Compute FIRST/FOLLOW
    3. Build LL(1) table
    4. Tokenize input
    5. Run LL(1) parser
    6. Build parse tree
    """
    grammar_text = body.grammar_text
    start_symbol = body.start_symbol

    # Step 1: optionally apply transformations
    transformed_grammar_text = grammar_text
    transformation_log = []

    if body.use_transformed:
        lr_result = eliminate_left_recursion(grammar_text, start_symbol)
        if lr_result.get("success") and lr_result.get("has_left_recursion"):
            transformed_grammar_text = lr_result["transformed_grammar"]
            transformation_log.append("Applied left recursion elimination")

        lf_result = left_factor(transformed_grammar_text, start_symbol)
        if lf_result.get("success") and lf_result.get("needs_factoring"):
            transformed_grammar_text = lf_result["transformed_grammar"]
            transformation_log.append("Applied left factoring")

    # Step 2: Parse grammar
    parse_result = parse_grammar(transformed_grammar_text, start_symbol)
    if not parse_result["success"]:
        raise HTTPException(
            status_code=400,
            detail={"error": "Grammar parsing failed", "errors": parse_result["errors"]}
        )

    grammar = parse_result["grammar"]
    used_start = grammar.start_symbol

    # Step 3: FIRST / FOLLOW
    first_sets = compute_first_sets(grammar)
    follow_sets = compute_follow_sets(grammar, first_sets)

    # Step 4: Build LL(1) table
    table_result = build_parsing_table(grammar, first_sets, follow_sets)

    if not table_result["is_ll1"]:
        conflicts = table_result["conflicts"]
    else:
        conflicts = []

    # Step 5: Tokenize
    tok_result = smart_tokenize(body.input_string, grammar.terminals)
    if not tok_result["success"]:
        raise HTTPException(
            status_code=400,
            detail={"error": "Tokenization failed", "message": tok_result["error"]}
        )

    tokens = tok_result["tokens"]

    # Step 6: Parse
    parse_sim = predictive_parse(grammar, table_result["table"], tokens, used_start)

    # Step 7: Build parse tree (only if accepted)
    tree = None
    if parse_sim["accepted"]:
        tree_result = build_parse_tree(grammar, parse_sim["productions_used"], used_start)
        if tree_result["success"]:
            tree = tree_result["tree"]

    return {
        "accepted": parse_sim["accepted"],
        "tokens": tokens,
        "steps": parse_sim["steps"],
        "parsing_steps": parse_sim["steps"],
        "productions_used": parse_sim["productions_used"],
        "parse_tree": tree,
        "error_message": parse_sim["error_message"],
        "error_step": parse_sim["error_step"],
        "is_ll1": table_result["is_ll1"],
        "conflicts": conflicts,
        "transformation_log": transformation_log,
        "grammar_used": grammar_to_dict(grammar),
        "parsing_table": table_result["table"]
    }


# ---------------------------------------------------------------------------
# Practice Mode
# ---------------------------------------------------------------------------

@router.get("/practice/question")
def practice_question_get(type: Optional[str] = Query(default=None)):
    question = generate_question(type)
    if "error" in question:
        raise HTTPException(status_code=400, detail=question["error"])
    return question


@router.post("/practice/generate")
def practice_generate(body: dict = {}):
    question_type = body.get("question_type") or body.get("type") if body else None
    question = generate_question(question_type)
    if "error" in question:
        raise HTTPException(status_code=400, detail=question["error"])
    return question


@router.post("/practice/check")
def practice_check(body: PracticeCheckRequest):
    result = check_answer(body.question_data, body.answer)
    return result
