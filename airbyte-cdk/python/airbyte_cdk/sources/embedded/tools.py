import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional, Union

from airbyte_cdk.models import AirbyteMessage, Type, ConfiguredAirbyteStream
from pydantic.main import BaseModel


def get_first(iterable: Iterable[Any], predicate: Callable[[Any], bool] = lambda m: True) -> Optional[Any]:
    return next(filter(predicate, iterable), None)

def get_defined_id(stream: ConfiguredAirbyteStream, data: Dict[str, Any]) -> Optional[str]:
    import dpath

    if not stream.primary_key:
        return None
    primary_key = []
    for key in stream.primary_key:
        try:
            primary_key.append(str(dpath.util.get(data, key)))
        except KeyError:
            primary_key.append("__not_found__")
    return "_".join(primary_key)
