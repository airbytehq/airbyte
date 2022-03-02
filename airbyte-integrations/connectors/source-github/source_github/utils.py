#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping


def get_value_by_path(D: Mapping[str, Any], path: List[str]):
    for k in path:
        if k not in D:
            return None
        D = D[k]
    return D


def set_value_by_path(D: Mapping[str, Any], path: List[str], value):
    for k in path[:-1]:
        D = D.setdefault(k, {})
    D[path[-1]] = value


def del_value_by_path(D, path):
    for k in path[:1]:
        D = D[k]
    del D[path[-1]]
