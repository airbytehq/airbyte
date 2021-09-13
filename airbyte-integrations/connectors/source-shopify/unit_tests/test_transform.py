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
from source_shopify.transform import Transformer


def find_by_path(path_list, value):
    key_or_index = path_list.pop(0)
    result_value = value[key_or_index]
    if len(path_list) > 0:
        result_value = find_by_path(path_list, result_value)
    return result_value


@pytest.mark.parametrize(
    "transform_object, schema, checks",
    [
        (
            {
                "id": 1,
                "email": "airbyte-integration-test@airbyte.io",
                "buyer_accepts_marketing": False,
                "created_at": "2021-07-08T04:58:50-07:00",
                "note": None,
                "total_weight": 112,
                "shipping_lines": [{"price": "20.17"}],
                "line_items": [{"gift_card": False, "grams": 112, "line_price": "19.00", "price": "19.00"}],
                "total_discounts": "0.00",
                "total_line_items_price": "19.00",
                "total_price": "39.17",
                "total_tax": "0.00",
                "subtotal_price": "19.00",
                "customer": {"total_spent": "0.00"},
            },
            {
                "buyer_accepts_marketing": {"type": ["null", "boolean"]},
                "total_weight": {"type": ["null", "integer"]},
                "created_at": {"type": ["null", "string"], "format": "date-time"},
                "total_line_items_price": {"type": ["null", "number"]},
                "id": {"type": ["null", "integer"]},
                "total_tax": {"type": ["null", "number"]},
                "subtotal_price": {"type": ["null", "number"]},
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
                "total_discounts": {"type": ["null", "number"]},
                "note": {"type": ["null", "string"]},
                "shipping_lines": {
                    "items": {"properties": {"price": {"type": ["null", "number"]}}, "type": ["null", "object"]},
                    "type": ["null", "array"],
                },
                "customer": {"type": "object", "properties": {"total_spent": {"type": ["null", "number"]}}},
                "total_price": {"type": ["null", "number"]},
            },
            [
                {
                    "path": [
                        "id",
                    ],
                    "expected_type": int,
                },
                {
                    "path": [
                        "buyer_accepts_marketing",
                    ],
                    "expected_type": bool,
                },
                {
                    "path": [
                        "note",
                    ],
                    "expected_type": type(None),
                },
                {
                    "path": [
                        "created_at",
                    ],
                    "expected_type": str,
                },
                {
                    "path": [
                        "total_discounts",
                    ],
                    "expected_type": Decimal,
                },
                {
                    "path": [
                        "total_price",
                    ],
                    "expected_type": Decimal,
                },
                {"path": ["customer", "total_spent"], "expected_type": Decimal},
                {"path": ["line_items", 0, "line_price"], "expected_type": Decimal},
                {"path": ["shipping_lines", 0, "price"], "expected_type": Decimal},
            ],
        )
    ],
)
def test_transform(transform_object, schema, checks):
    transformer = Transformer(schema)
    transformer._transform_object(transform_object, schema)
    for check in checks:
        expected_value = find_by_path(check.get("path"), transform_object)
        assert isinstance(expected_value, check["expected_type"])
