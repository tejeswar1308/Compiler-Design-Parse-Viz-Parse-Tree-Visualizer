"""
Parse Tree Builder.

Reconstructs the parse tree from the sequence of productions used
during LL(1) predictive parsing (leftmost derivation replay).
"""

from typing import List, Optional, Dict, Any
import uuid
from app.services.grammar_parser import Grammar, EPSILON


def _new_id() -> str:
    return "node-" + str(uuid.uuid4())[:8]


class ParseTreeNode:
    """A node in the parse tree."""

    def __init__(self, label: str, node_type: str, production: Optional[str] = None):
        self.id = _new_id()
        self.label = label
        self.node_type = node_type  # "nonterminal", "terminal", "epsilon"
        self.production = production
        self.children: List["ParseTreeNode"] = []

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "label": self.label,
            "type": self.node_type,
        }
        if self.production:
            result["production"] = self.production
        if self.children:
            result["children"] = [c.to_dict() for c in self.children]
        else:
            result["children"] = []
        return result


def build_parse_tree(
    grammar: Grammar,
    productions_used: List[str],
    start_symbol: str
) -> dict:
    """
    Build a parse tree from the leftmost derivation (productions used).

    The algorithm replays the LL(1) parsing:
    - Start with the root = start_symbol
    - Maintain a list of frontier nodes (leaves that are nonterminals)
    - For each production used, expand the leftmost nonterminal frontier node

    Returns:
        {
            "success": bool,
            "tree": dict | None,
            "error": str | None
        }
    """
    if not productions_used:
        # Empty production sequence = just the start symbol (if it directly produces ε)
        root = ParseTreeNode(start_symbol, "nonterminal")
        return {"success": True, "tree": root.to_dict(), "error": None}

    root = ParseTreeNode(start_symbol, "nonterminal")
    # Frontier: list of nonterminal leaf nodes (in left-to-right order)
    frontier: List[ParseTreeNode] = [root]

    prod_index = 0

    while prod_index < len(productions_used) and frontier:
        # Take the leftmost nonterminal from frontier
        node = frontier.pop(0)

        if node.node_type != "nonterminal":
            continue

        production_str = productions_used[prod_index]
        prod_index += 1

        # Parse the production string "A -> B C D"
        try:
            arrow_pos = production_str.index('->')
            lhs = production_str[:arrow_pos].strip()
            rhs_str = production_str[arrow_pos + 2:].strip()
        except ValueError:
            return {
                "success": False,
                "tree": None,
                "error": f"Malformed production string: '{production_str}'"
            }

        if lhs != node.label:
            # Mismatch — could indicate parse sequence error
            return {
                "success": False,
                "tree": None,
                "error": (
                    f"Production mismatch: expected expansion of '{node.label}' "
                    f"but got production '{production_str}'."
                )
            }

        node.production = production_str

        # Parse RHS symbols
        if not rhs_str or rhs_str == EPSILON:
            rhs_symbols = [EPSILON]
        else:
            rhs_symbols = rhs_str.split()

        # Build children
        new_nonterminal_children = []
        for sym in rhs_symbols:
            if sym == EPSILON:
                child = ParseTreeNode(EPSILON, "epsilon")
            elif grammar.is_nonterminal(sym):
                child = ParseTreeNode(sym, "nonterminal")
                new_nonterminal_children.append(child)
            else:
                child = ParseTreeNode(sym, "terminal")
            node.children.append(child)

        # Add new nonterminal children to the front of frontier (leftmost first)
        frontier = new_nonterminal_children + frontier

    return {"success": True, "tree": root.to_dict(), "error": None}
