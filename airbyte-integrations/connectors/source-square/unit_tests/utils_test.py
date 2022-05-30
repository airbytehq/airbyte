#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
