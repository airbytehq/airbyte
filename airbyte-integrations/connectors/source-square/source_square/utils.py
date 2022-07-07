#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
