#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import os
from typing import Union

logger = logging.getLogger("airbyte")


def iterate_one_by_one(*iterables):
    iterables = list(iterables)
    while iterables:
        iterable = iterables.pop(0)
        try:
            yield next(iterable)
        except StopIteration:
            pass
        else:
            iterables.append(iterable)


def get_typed_env(name: str, default: Union[str, int]) -> Union[str, int]:
    convert = type(default)
    assert convert in [str, int]
    value = os.environ.get(name, default)
    try:
        return convert(value)
    except ValueError:
        logger.warning(f"Cannot convert environment variable {name}={value!r} to type {convert}")
        return default
