#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import itertools
import traceback
from typing import Any, Iterable, Iterator, Tuple, Union

from airbyte_cdk.models import AirbyteRecordMessage, AirbyteStream


def format_exception(exception: Exception) -> str:
    return str(exception) + "\n" + "".join(traceback.TracebackException.from_exception(exception).format())


def create_chunks(iterable: Iterable[Any], batch_size: int) -> Iterator[Tuple[Any, ...]]:
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))


def create_stream_identifier(stream: Union[AirbyteStream, AirbyteRecordMessage]) -> str:
    if isinstance(stream, AirbyteStream):
        return str(stream.name if stream.namespace is None else f"{stream.namespace}_{stream.name}")
    else:
        return str(stream.stream if stream.namespace is None else f"{stream.namespace}_{stream.stream}")
