# uses code from https://github.com/daveoncode/python-string-utils

import re

__all__ = ["camel_to_snake", "snake_to_camel"]

_re_camel_to_snake = re.compile(r"([a-z]|[A-Z0-9]+)(?=[A-Z])")
_re_snake_to_camel = re.compile(r"(_)([a-z\d])")


def camel_to_snake(s: str) -> str:
    """Convert from CamelCase to snake_case"""
    return _re_camel_to_snake.sub(r"\1_", s).lower()


def snake_to_camel(s: str, upper: bool = True) -> str:
    """Convert from snake_case to CamelCase

    If upper is set, then convert to upper CamelCase, otherwise the first character
    keeps its case.
    """
    s = _re_snake_to_camel.sub(lambda m: m.group(2).upper(), s)
    if upper:
        s = s[:1].upper() + s[1:]
    return s
