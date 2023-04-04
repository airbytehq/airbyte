#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import itertools
from typing import Any, Iterator, Optional, Tuple


def peek(iterator: Iterator[Any]) -> Tuple[Optional[Any], Iterator[Any]]:
    try:
        first = next(iterator)
    except StopIteration:
        return None, iterator
    # return the stream as it was before calling next
    return first, itertools.chain([first], iterator)
