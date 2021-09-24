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


import pytest
from source_marketo.utils import clean_string, format_value

test_data = [
    (1, {"type": "integer"}, int),
    ("string", {"type": "string"}, str),
    (True, {"type": ["boolean", "null"]}, bool),
    (1, {"type": ["number", "null"]}, float),
]


@pytest.mark.parametrize("value,schema,expected_output_type", test_data)
def test_fromat_value(value, schema, expected_output_type):
    test = format_value(value, schema)

    assert isinstance(test, expected_output_type)


test_data = [
    ("updatedAt", "updated_at"),
    ("UpdatedAt", "updated_at"),
    ("base URL", "base_url"),
    ("UPdatedAt", "u_pdated_at"),
    ("updated_at", "updated_at"),
    (" updated_at ", "updated_at"),
    ("updatedat", "updatedat"),
    ("", ""),
]


@pytest.mark.parametrize("value,expected", test_data)
def test_clean_string(value, expected):
    test = clean_string(value)

    assert test == expected
