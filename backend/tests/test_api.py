"""
Integration tests for ParseViz FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

ARITHMETIC_GRAMMAR = "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id"
LL1_ARITHMETIC = (
    "E -> T E'\n"
    "E' -> + T E' | ε\n"
    "T -> F T'\n"
    "T' -> * F T' | ε\n"
    "F -> ( E ) | id"
)
FACTORING_GRAMMAR = "S -> i E t S | i E t S e S | a\nE -> b"
CONFLICT_GRAMMAR = "S -> A a | b\nA -> b | ε"


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_examples_endpoint():
    # Both endpoints should work
    res1 = client.get("/api/examples")
    assert res1.status_code == 200
    assert "examples" in res1.json()
    assert len(res1.json()["examples"]) >= 5

    res2 = client.get("/api/grammar/examples")
    assert res2.status_code == 200
    assert isinstance(res2.json(), list)
    assert len(res2.json()) >= 5


def test_validate_valid_grammar():
    response = client.post("/api/grammar/validate", json={"grammar_text": ARITHMETIC_GRAMMAR})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["success"] is True
    assert data["grammar"]["start_symbol"] == "E"
    assert "E" in data["grammar"]["nonterminals"]
    assert "+" in data["grammar"]["terminals"]


def test_validate_invalid_grammar():
    response = client.post("/api/grammar/validate", json={"grammar_text": "Invalid Production Without Arrow"})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert len(data["errors"]) > 0


def test_left_recursion_elimination():
    response = client.post("/api/grammar/transform/left-recursion", json={"grammar_text": ARITHMETIC_GRAMMAR})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["has_left_recursion"] is True
    assert "E" in data["recursive_nonterminals"]
    assert "T" in data["recursive_nonterminals"]
    assert len(data["steps"]) > 0
    assert "E'" in data["transformed_grammar"] or "E_prime" in data["transformed_grammar"]


def test_left_factoring():
    response = client.post("/api/grammar/transform/left-factoring", json={"grammar_text": FACTORING_GRAMMAR})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["needs_factoring"] is True
    assert len(data["steps"]) > 0


def test_first_follow_computation():
    response = client.post("/api/grammar/first-follow", json={"grammar_text": LL1_ARITHMETIC})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "(" in data["first_sets"]["E"]
    assert "id" in data["first_sets"]["E"]
    assert "$" in data["follow_sets"]["E"]
    assert ")" in data["follow_sets"]["E"]


def test_parsing_table_construction():
    response = client.post("/api/grammar/parsing-table", json={"grammar_text": LL1_ARITHMETIC})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["is_ll1"] is True
    assert len(data["conflicts"]) == 0
    assert "E" in data["table"]
    assert "id" in data["terminals"]


def test_parsing_table_with_conflicts():
    response = client.post("/api/grammar/parsing-table", json={"grammar_text": CONFLICT_GRAMMAR})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["is_ll1"] is False
    assert len(data["conflicts"]) > 0


def test_parse_accepted_string_with_tree():
    response = client.post(
        "/api/grammar/parse",
        json={
            "grammar_text": LL1_ARITHMETIC,
            "input_string": "id + id * id",
            "use_transformed": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] is True
    assert len(data["steps"]) > 0
    assert data["parse_tree"] is not None
    assert data["parse_tree"]["label"] == "E"
    assert len(data["productions_used"]) > 0


def test_parse_rejected_string():
    response = client.post(
        "/api/grammar/parse",
        json={
            "grammar_text": LL1_ARITHMETIC,
            "input_string": "id + +",
            "use_transformed": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] is False
    assert data["parse_tree"] is None
    assert data["error_message"] is not None


def test_practice_question_generate_and_check():
    # 1. Generate question
    gen_res = client.get("/api/practice/question?type=is_ll1")
    assert gen_res.status_code == 200
    q = gen_res.json()
    assert "id" in q
    assert "question" in q
    assert "options" in q
    assert "correct_answer" in q

    # 2. Check correct answer
    check_res = client.post(
        "/api/practice/check",
        json={
            "question_id": q["id"],
            "answer": q["correct_answer"],
            "question_data": q,
        },
    )
    assert check_res.status_code == 200
    check_data = check_res.json()
    assert check_data["correct"] is True
    assert isinstance(check_data["step_by_step"], list)
    assert len(check_data["step_by_step"]) > 0
    # verify step_by_step items are strings
    assert all(isinstance(s, str) for s in check_data["step_by_step"])


def test_full_sample_demonstration_scenario():
    """
    Simulates the exact 10-step hackathon demo flow:
    1. Enter original grammar
    2. Detect left recursion in E and T
    3. Eliminate left recursion
    4. Compute FIRST and FOLLOW
    5. Construct LL(1) table
    6. Parse id + id * id
    7. Generate parse tree
    """
    # Step 1: Validate original grammar
    val_res = client.post("/api/grammar/validate", json={"grammar_text": ARITHMETIC_GRAMMAR})
    assert val_res.json()["valid"] is True

    # Step 2 & 3: Eliminate left recursion
    lr_res = client.post("/api/grammar/transform/left-recursion", json={"grammar_text": ARITHMETIC_GRAMMAR})
    lr_data = lr_res.json()
    assert lr_data["has_left_recursion"] is True
    assert "E" in lr_data["recursive_nonterminals"]
    assert "T" in lr_data["recursive_nonterminals"]
    transformed = lr_data["transformed_grammar"]

    # Step 4: FIRST & FOLLOW
    ff_res = client.post("/api/grammar/first-follow", json={"grammar_text": transformed})
    ff_data = ff_res.json()
    assert ff_data["success"] is True

    # Step 5: LL(1) table
    tbl_res = client.post("/api/grammar/parsing-table", json={"grammar_text": transformed})
    tbl_data = tbl_res.json()
    assert tbl_data["is_ll1"] is True

    # Step 6 & 7: Parse id + id * id and build parse tree
    parse_res = client.post(
        "/api/grammar/parse",
        json={
            "grammar_text": transformed,
            "input_string": "id + id * id",
            "use_transformed": False,
        },
    )
    p_data = parse_res.json()
    assert p_data["accepted"] is True
    assert p_data["parse_tree"] is not None
    assert p_data["parse_tree"]["label"] == "E"
    assert len(p_data["steps"]) > 0
