#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from decimal import Decimal

import pytest
from source_shopify.transform import DataTypeEnforcer


def find_by_path(path_list, value):
    key_or_index = path_list.pop(0)
    result_value = value[key_or_index]
    if len(path_list) > 0:
        result_value = find_by_path(path_list, result_value)
    return result_value


def run_check(transform_object, schema, checks):
    transformer = DataTypeEnforcer(schema)
    transform_object = transformer.transform(transform_object)
    for check in checks:
        expected_value = find_by_path(check.get("path"), transform_object)
        assert isinstance(expected_value, check["expected_type"])


@pytest.mark.parametrize(
    "transform_object, schema, checks",
    [
        (
            {"id": 1},
            {
                "type": "object",
                "properties": {
                    "total_price": {"type": ["null", "integer"]},
                },
            },
            [
                {
                    "path": [
                        "id",
                    ],
                    "expected_type": int,
                },
            ],
        ),
        (
            {
                "created_at": "2021-07-08T04:58:50-07:00",
            },
            {
                "type": "object",
                "properties": {
                    "total_price": {"type": ["null", "string"]},
                },
            },
            [
                {
                    "path": [
                        "created_at",
                    ],
                    "expected_type": str,
                },
            ],
        ),
        (
            {
                "note": None,
            },
            {
                "type": "object",
                "properties": {
                    "total_price": {"type": ["null", "string"]},
                },
            },
            [
                {
                    "path": [
                        "note",
                    ],
                    "expected_type": type(None),
                },
            ],
        ),
        (
            {
                "buyer_accepts_marketing": False,
            },
            {
                "type": "object",
                "properties": {
                    "total_price": {"type": ["null", "boolean"]},
                },
            },
            [
                {
                    "path": [
                        "buyer_accepts_marketing",
                    ],
                    "expected_type": bool,
                },
            ],
        ),
    ],
)
def test_enforcer_correct_type(transform_object, schema, checks):
    run_check(transform_object, schema, checks)


@pytest.mark.parametrize(
    "transform_object, schema, checks",
    [
        (
            {
                "total_discounts": "0.00",
            },
            {
                "type": "object",
                "properties": {
                    "total_discounts": {"type": ["null", "number"]},
                },
            },
            [
                {
                    "path": [
                        "total_discounts",
                    ],
                    "expected_type": Decimal,
                },
            ],
        ),
        (
            {
                "total_price": "39.17",
            },
            {
                "type": "object",
                "properties": {
                    "total_price": {"type": ["null", "number"]},
                },
            },
            [
                {
                    "path": [
                        "total_price",
                    ],
                    "expected_type": Decimal,
                },
            ],
        ),
    ],
)
def test_enforcer_string_to_number(transform_object, schema, checks):
    run_check(transform_object, schema, checks)


@pytest.mark.parametrize(
    "transform_object, schema, checks",
    [
        (
            {
                "customer": {"total_spent": "0.00"},
            },
            {
                "type": "object",
                "properties": {
                    "customer": {"type": "object", "properties": {"total_spent": {"type": ["null", "number"]}}},
                },
            },
            [
                {"path": ["customer", "total_spent"], "expected_type": Decimal},
            ],
        )
    ],
)
def test_enforcer_nested_object(transform_object, schema, checks):
    run_check(transform_object, schema, checks)


@pytest.mark.parametrize(
    "transform_object, schema, checks",
    [
        (
            {
                "shipping_lines": [{"price": "20.17"}],
            },
            {
                "type": "object",
                "properties": {
                    "shipping_lines": {
                        "items": {"properties": {"price": {"type": ["null", "number"]}}, "type": ["null", "object"]},
                        "type": ["null", "array"],
                    },
                },
            },
            [
                {"path": ["shipping_lines", 0, "price"], "expected_type": Decimal},
            ],
        ),
        (
            {
                "line_items": [{"gift_card": False, "grams": 112, "line_price": "19.00", "price": "19.00"}],
            },
            {
                "type": "object",
                "properties": {
                    "line_items": {
                        "items": {
                            "properties": {
                                "grams": {"type": ["null", "integer"]},
                                "line_price": {"type": ["null", "number"]},
                                "gift_card": {"type": ["null", "boolean"]},
                                "price": {"type": ["null", "number"]},
                            },
                            "type": ["null", "object"],
                        },
                        "type": ["null", "array"],
                    },
                },
            },
            [
                {"path": ["line_items", 0, "line_price"], "expected_type": Decimal},
            ],
        ),
    ],
)
def test_enforcer_nested_array(transform_object, schema, checks):
    run_check(transform_object, schema, checks)


@pytest.mark.parametrize(
    "transform_object, schema, checks",
    [
        (
            {
                "line_items": ["19.00", "0.00"],
            },
            {
                "type": "object",
                "properties": {
                    "line_items": {
                        "items": {
                            "type": ["null", "number"],
                        },
                        "type": ["null", "array"],
                    },
                },
            },
            [
                {"path": ["line_items", 0], "expected_type": Decimal},
                {"path": ["line_items", 1], "expected_type": Decimal},
            ],
        ),
    ],
)
def test_enforcer_string_to_number_in_array(transform_object, schema, checks):
    run_check(transform_object, schema, checks)
