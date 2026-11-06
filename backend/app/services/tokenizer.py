"""
Tokenizer for input strings.

Tokenizes an input string using the grammar's terminal symbols
via greedy longest-match tokenization.
Automatically appends '$' end-of-input marker.
"""

from typing import List, Set, Optional


def tokenize(input_string: str, terminals: Set[str]) -> dict:
    """
    Tokenize `input_string` using the grammar's terminal symbols.

    Uses greedy longest-match: at each position, try to match the
    longest terminal symbol first.

    Args:
        input_string: The string to tokenize.
        terminals: Set of terminal symbols from the grammar.

    Returns:
        {
            "success": bool,
            "tokens": list[str] | None,
            "error": str | None,
            "error_position": int | None
        }
    """
    if not input_string or not input_string.strip():
        return {
            "success": True,
            "tokens": ['$'],
            "error": None,
            "error_position": None
        }

    # Sort terminals by length descending for greedy longest match
    sorted_terminals = sorted(terminals, key=len, reverse=True)

    tokens: List[str] = []
    s = input_string.strip()
    pos = 0

    while pos < len(s):
        # Skip whitespace
        if s[pos].isspace():
            pos += 1
            continue

        matched = False
        for term in sorted_terminals:
            if s[pos:].startswith(term):
                # Make sure it's a full token (either end of string or followed by non-alnum
                # if the terminal is alphanumeric, to avoid partial matches)
                end = pos + len(term)
                # If terminal is alphanumeric, ensure next char is boundary
                if term.isalnum() or '_' in term:
                    if end < len(s) and (s[end].isalnum() or s[end] == '_'):
                        continue  # Not a full match (e.g. "id" matching "ide")
                tokens.append(term)
                pos = end
                matched = True
                break

        if not matched:
            # Try to extract the unrecognized token for a good error message
            end = pos
            while end < len(s) and not s[end].isspace():
                end += 1
            unrecognized = s[pos:end]
            return {
                "success": False,
                "tokens": None,
                "error": f"Unrecognized token '{unrecognized}' at position {pos}.",
                "error_position": pos
            }

    tokens.append('$')
    return {
        "success": True,
        "tokens": tokens,
        "error": None,
        "error_position": None
    }


def tokenize_with_spaces(input_string: str, terminals: Set[str]) -> dict:
    """
    Alternative tokenizer: splits by whitespace first.
    Falls back to this when the input appears space-separated.
    Each space-separated token must be a known terminal or '$'.
    """
    parts = input_string.strip().split()
    if not parts:
        return {"success": True, "tokens": ['$'], "error": None, "error_position": None}

    tokens = []
    for part in parts:
        if part == '$':
            tokens.append('$')
        elif part in terminals:
            tokens.append(part)
        else:
            return {
                "success": False,
                "tokens": None,
                "error": f"Unrecognized token '{part}'.",
                "error_position": None
            }

    if tokens[-1] != '$':
        tokens.append('$')

    return {"success": True, "tokens": tokens, "error": None, "error_position": None}


def smart_tokenize(input_string: str, terminals: Set[str]) -> dict:
    """
    Tries greedy longest-match first, falls back to space-split.
    """
    result = tokenize(input_string, terminals)
    if result["success"]:
        return result
    # If greedy failed, try space-split
    fallback = tokenize_with_spaces(input_string, terminals)
    if fallback["success"]:
        return fallback
    # Return the original greedy error
    return result
