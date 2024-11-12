#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Callable, Dict, Iterable, Optional

import dpath
from airbyte_cdk.models import AirbyteStream


def get_first(iterable: Iterable[Any], predicate: Callable[[Any], bool] = lambda m: True) -> Optional[Any]:
    return next(filter(predicate, iterable), None)


def get_defined_id(stream: AirbyteStream, data: Dict[str, Any]) -> Optional[str]:
    if not stream.source_defined_primary_key:
        return None
    primary_key = []
    for key in stream.source_defined_primary_key:
        try:
            primary_key.append(str(dpath.get(data, key)))
        except KeyError:
            primary_key.append("__not_found__")
    return "_".join(primary_key)
