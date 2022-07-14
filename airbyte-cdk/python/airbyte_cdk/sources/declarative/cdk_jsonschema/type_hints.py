#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import ast
import sys

try:
    from typing import ForwardRef  # type: ignore
except ImportError:
    # Python 3.6
    from typing import _ForwardRef as ForwardRef  # type: ignore

from typing import _eval_type  # type: ignore
from typing import Any, Dict, List, Set, Tuple, Type, Union


def get_elts(op: ast.BinOp):
    for arg in (op.left, op.right):
        if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.BitOr):
            for n in get_elts(arg):
                yield n
        else:
            yield arg


class RewriteUnionTypes(ast.NodeTransformer):
    def __init__(self):
        self.rewritten = False

    def visit_BinOp(self, node: ast.BinOp) -> Union[ast.BinOp, ast.Subscript]:
        if isinstance(node.op, ast.BitOr):
            self.rewritten = True
            return ast.Subscript(
                value=ast.Name(id="_Union", ctx=ast.Load(), lineno=1, col_offset=1),
                slice=ast.Index(
                    value=ast.Tuple(elts=list(get_elts(node)), ctx=ast.Load(), lineno=1, col_offset=1),
                    ctx=ast.Load(),
                    lineno=1,
                    col_offset=1,
                ),
                lineno=1,
                col_offset=1,
                ctx=ast.Load(),
            )
        else:
            return node


class RewriteBuiltinGenerics(ast.NodeTransformer):
    def __init__(self):
        self.rewritten = False
        # Collections are prefixed with _ to prevent any potential name clashes
        self.replacements = {
            "list": "_List",
            "set": "_Set",
            "frozenset": "_Frozenset",
            "dict": "_Dict",
            "type": "_Type",
            "tuple": "_Tuple",
        }

    def visit_Name(self, node: ast.Name) -> ast.Name:
        if node.id in self.replacements:
            self.rewritten = True
            return ast.Name(id=self.replacements[node.id], ctx=node.ctx, lineno=1, col_offset=1)
        else:
            return node


def get_class_type_hints(klass: Type, localns=None) -> Dict[str, Any]:
    """Return type hints for a class. Adapted from `typing.get_type_hints`, adds support for PEP 585 & PEP 604"""
    hints = {}
    print(f"get_class_type_hints for {klass}")
    for base in reversed(klass.__mro__):
        base_globals = sys.modules[base.__module__].__dict__
        base_globals["_Union"] = Union
        if sys.version_info < (3, 9):
            base_globals["_List"] = List
            base_globals["_Set"] = Set
            base_globals["_Type"] = Type
            base_globals["_Tuple"] = Tuple
            base_globals["_Dict"] = Dict
        ann = base.__dict__.get("__annotations__", {})
        for name, value in ann.items():
            if value is None:
                value = type(None)
            if isinstance(value, str):
                t = ast.parse(value, "<unknown>", "eval")
                union_transformer = RewriteUnionTypes()
                t = union_transformer.visit(t)
                builtin_generics_transformer = RewriteBuiltinGenerics()
                if sys.version_info < (3, 9):
                    t = builtin_generics_transformer.visit(t)
                if builtin_generics_transformer.rewritten or union_transformer.rewritten:
                    # Note: ForwardRef raises a TypeError when given anything that isn't a string, so we need
                    # to compile & eval the ast here
                    code = compile(t, "<unknown>", "eval")
                    hints[name] = eval(code, base_globals, localns)
                    continue
                else:
                    value = ForwardRef(value, is_argument=False)
            value = _eval_type(value, base_globals, localns)
            hints[name] = value
    return hints
