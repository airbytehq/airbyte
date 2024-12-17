from __future__ import annotations

from typing import Any

import pytest
from destination_deepset import util
from pydantic import BaseModel


class Simple(BaseModel):
    name: str


class Nested(BaseModel):
    simple: Simple
    adjacent: bool


@pytest.mark.parametrize(
    ("obj", "key_path", "expected"),
    [
        ({}, "a.b", None),  # default fallback value is None
        ({"a": {"b": 5}}, "a.b", 5),
        ({"a": {"b": 5}}, "a.b.c", None),  # fallback
        # Should work for Pydantic models too
        (Simple(name="Jack"), "name", "Jack"),
        (Simple(name="Jack"), "name.last", None),  # fallback
        (Nested(simple=Simple(name="Jack"), adjacent=False), "adjacent", False),
        (Nested(simple=Simple(name="Jack"), adjacent=False), "simple.name", "Jack"),
    ],
)
def test_get(obj: Any, key_path: str, expected: Any) -> None:
    assert util.get(obj=obj, key_path=key_path) == expected


def test_get_ignores_fallback_value_if_match_found() -> None:
    fallback = "I Fall Back"
    obj = {"a": {"b": {"c": "I Don't Fall Back"}}}
    assert util.get(obj=obj, key_path="a.b.c", default=fallback) != fallback
    assert util.get(obj=obj, key_path="a.b.c", default=fallback) == "I Don't Fall Back"


def test_get_returns_fallback_value_if_no_match_found() -> None:
    fallback = "I Fall Back"
    assert util.get(obj={}, key_path="a.b.c", default=fallback) == fallback
