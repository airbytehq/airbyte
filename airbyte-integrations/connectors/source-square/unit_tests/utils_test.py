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

import math

import pytest
from source_square.utils import separate_by_count, separate_items_by_count


def test_separate_by_count():
    total_parts, last_part = separate_by_count(total_length=196582, part_count=10000)
    assert total_parts == 19
    assert last_part == 6582

    total_parts, last_part = separate_by_count(total_length=1, part_count=10)
    assert total_parts == 0
    assert last_part == 1

    total_parts, last_part = separate_by_count(total_length=10000, part_count=10000)
    assert total_parts == 1
    assert last_part == 0

    with pytest.raises(ZeroDivisionError):
        separate_by_count(total_length=0, part_count=0)

    total_parts, last_part = separate_by_count(total_length=0, part_count=10)
    assert total_parts == 0
    assert last_part == 0

    total_parts, last_part = separate_by_count(total_length=math.inf, part_count=10)
    assert math.isnan(total_parts) is True
    assert math.isnan(last_part) is True

    total_parts, last_part = separate_by_count(total_length=math.inf, part_count=math.inf)
    assert math.isnan(total_parts) is True
    assert math.isnan(last_part) is True


def test_separate_items_by_count():
    item_list = [i for i in range(10)]

    result_list = separate_items_by_count(item_list=[], part_count=10)
    assert result_list == []

    result_list = separate_items_by_count(item_list=item_list, part_count=1)
    assert result_list == [[0], [1], [2], [3], [4], [5], [6], [7], [8], [9]]

    result_list = separate_items_by_count(item_list=item_list, part_count=10)
    assert result_list == [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]

    result_list = separate_items_by_count(item_list=item_list, part_count=15)
    assert result_list == [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]

    result_list = separate_items_by_count(item_list=item_list, part_count=4)
    assert result_list == [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]

    result_list = separate_items_by_count(item_list=item_list, part_count=5)
    assert result_list == [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

    result_list = separate_items_by_count(item_list=item_list, part_count=9)
    assert result_list == [[0, 1, 2, 3, 4, 5, 6, 7, 8], [9]]

    result_list = separate_items_by_count(item_list=None, part_count=5)
    assert result_list == []
