"""Deterministic math tools for the Finance agent.

`calculator` safely evaluates an arithmetic expression (no names, no calls) so
the LLM can offload numbers instead of hallucinating them.
"""

from __future__ import annotations

import ast
import operator as op

# Whitelisted operators — anything else raises.
_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: op.neg, ast.UAdd: op.pos,
    ast.FloorDiv: op.floordiv,
}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")


def calculator(expression: str) -> str:
    """Evaluate a plain arithmetic expression, e.g. '250000 * 12 / 0.2'."""
    try:
        return str(_eval(ast.parse(expression, mode="eval").body))
    except Exception as exc:
        return f"[calculator error] {exc}"
