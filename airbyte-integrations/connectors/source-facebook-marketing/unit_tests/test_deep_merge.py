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

from copy import deepcopy

from source_facebook_marketing.common import deep_merge


def test_return_new_object():
    """Should return new object, arguments should not be modified"""
    left = {
        "key_1": {
            "one": {"a", "b"},
            "two": "left_value",
        },
        "key_2": [1, 2],
    }
    right = {"key_1": {"two": "right_value", "three": [1, 2, 3]}, "key_2": [3]}
    expected_result = {"key_1": {"one": {"a", "b"}, "two": "right_value", "three": [1, 2, 3]}, "key_2": [1, 2, 3]}

    result = deep_merge(deepcopy(left), deepcopy(right))

    assert left == left
    assert right == right
    assert result == expected_result


def test_sets():
    left = {1, 2, 3}
    right = {4, 2, 1}
    result = deep_merge(left, right)

    assert result == {1, 2, 3, 4}


def test_lists():
    left = [1, 2, 3]
    right = [4, 2, 1]
    result = deep_merge(left, right)

    assert result == [1, 2, 3, 4, 2, 1]
