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

from typing import Union


def separate_by_count(total_length: int, part_count: int) -> (int, int):
    """
    Calculates parts needed to separate count by part_count value
    For example: separate_by_count(total_length=196582, part_count=10000) returns (19, 6582) -> 19*10000 + 6582=196582

    :param total_length:
    :param part_count:
    :return: Returns the total_parts and last part count
    """
    total_parts = total_length // part_count
    last_part = total_length - (part_count * total_parts)
    return total_parts, last_part


def separate_items_by_count(item_list: Union[list, tuple], part_count: int) -> list:
    if not item_list:
        return []

    total_parts, _ = separate_by_count(len(item_list), part_count)

    result_list = []
    for i in range(total_parts):
        result_list.append(item_list[part_count * i : part_count * (i + 1)])

    if len(item_list) % part_count != 0:
        result_list.append(item_list[total_parts * part_count :])

    return result_list
