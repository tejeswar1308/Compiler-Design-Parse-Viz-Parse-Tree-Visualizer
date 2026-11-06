"""
Predictive (LL(1)) Parser Simulation.

Simulates the stack-based LL(1) parsing algorithm step by step.
"""

from typing import List, Optional, Dict
from app.services.grammar_parser import Grammar, EPSILON


def predictive_parse(
    grammar: Grammar,
    parsing_table: Dict[str, Dict[str, Optional[str]]],
    tokens: List[str],
    start_symbol: str
) -> dict:
    """
    Simulate LL(1) predictive parsing.

    Args:
        grammar: The Grammar object.
        parsing_table: The LL(1) parsing table.
        tokens: List of input tokens (must end with '$').
        start_symbol: The start symbol.

    Returns:
        {
            "accepted": bool,
            "steps": [ { step, stack, remaining_input, action, production } ],
            "error_message": str | None,
            "error_step": int | None,
            "productions_used": [ "A -> B C", ... ]
        }
    """
    if not tokens or tokens[-1] != '$':
        tokens = list(tokens) + ['$']

    stack: List[str] = ['$', start_symbol]
    input_ptr = 0
    steps = []
    productions_used: List[str] = []
    step_num = 0
    error_message = None
    error_step = None
    accepted = False

    max_steps = 1000  # Safety limit

    while stack and step_num < max_steps:
        step_num += 1
        top = stack[-1]
        current = tokens[input_ptr] if input_ptr < len(tokens) else '$'

        remaining = list(tokens[input_ptr:])
        stack_snapshot = list(stack)

        # Accept condition
        if top == '$' and current == '$':
            steps.append({
                "step": step_num,
                "stack": stack_snapshot,
                "remaining_input": remaining,
                "action": "Accept",
                "production": None
            })
            accepted = True
            break

        # Top of stack is $, but current isn't $
        if top == '$':
            error_message = f"Unexpected token '{current}' after end of input."
            error_step = step_num
            steps.append({
                "step": step_num,
                "stack": stack_snapshot,
                "remaining_input": remaining,
                "action": f"Error: {error_message}",
                "production": None
            })
            break

        # Top is a terminal
        if grammar.is_terminal(top):
            if top == current:
                stack.pop()
                input_ptr += 1
                action = f"Match '{top}'"
                steps.append({
                    "step": step_num,
                    "stack": stack_snapshot,
                    "remaining_input": remaining,
                    "action": action,
                    "production": None
                })
            else:
                error_message = f"Expected '{top}' but found '{current}'."
                error_step = step_num
                steps.append({
                    "step": step_num,
                    "stack": stack_snapshot,
                    "remaining_input": remaining,
                    "action": f"Error: {error_message}",
                    "production": None
                })
                break

        # Top is a nonterminal
        elif grammar.is_nonterminal(top):
            entry = parsing_table.get(top, {}).get(current)
            if entry is None:
                error_message = (
                    f"No production for '{top}' with lookahead '{current}'. "
                    f"Parsing table entry M[{top}][{current}] is empty."
                )
                error_step = step_num
                steps.append({
                    "step": step_num,
                    "stack": stack_snapshot,
                    "remaining_input": remaining,
                    "action": f"Error: {error_message}",
                    "production": None
                })
                break

            # entry is like "E -> T E'"
            stack.pop()
            # Parse the production
            arrow_pos = entry.index('->')
            rhs_str = entry[arrow_pos + 2:].strip()
            rhs_symbols = rhs_str.split() if rhs_str and rhs_str != EPSILON else []

            # Filter out epsilon symbols (don't push ε onto stack)
            rhs_to_push = [s for s in rhs_symbols if s != EPSILON]

            # Push in reverse order (so first symbol is on top)
            for sym in reversed(rhs_to_push):
                stack.append(sym)

            action = f"Expand {entry}"
            productions_used.append(entry)
            steps.append({
                "step": step_num,
                "stack": stack_snapshot,
                "remaining_input": remaining,
                "action": action,
                "production": entry
            })

        else:
            # Symbol not in grammar at all
            error_message = f"Unknown symbol '{top}' on stack."
            error_step = step_num
            steps.append({
                "step": step_num,
                "stack": stack_snapshot,
                "remaining_input": remaining,
                "action": f"Error: {error_message}",
                "production": None
            })
            break

    if step_num >= max_steps and not accepted:
        error_message = "Parsing exceeded maximum steps limit. Possible infinite loop."
        error_step = step_num

    return {
        "accepted": accepted,
        "steps": steps,
        "error_message": error_message,
        "error_step": error_step,
        "productions_used": productions_used
    }
