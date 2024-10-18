# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Message generator for Airbyte messages."""

from __future__ import annotations

import datetime
import json
import sys
from collections.abc import Iterator
from dataclasses import asdict
from typing import IO, TYPE_CHECKING, cast

import pendulum
import pydantic
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    StreamDescriptor,
    TraceType,
    Type,
)
from airbyte_cdk.sql.constants import AB_EXTRACTED_AT_COLUMN
from typing_extensions import final

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Iterable, Iterator
    from pathlib import Path

    from airbyte_cdk.sql.results import ReadResult


def _new_stream_success_message(stream_name: str) -> AirbyteMessage:
    """Return a new stream success message."""
    return AirbyteMessage(
        type=Type.TRACE,
        trace=AirbyteTraceMessage(
            type=TraceType.STREAM_STATUS,
            stream=stream_name,
            emitted_at=pendulum.now().float_timestamp,
            stream_status=AirbyteStreamStatusTraceMessage(
                stream_descriptor=StreamDescriptor(
                    name=stream_name,
                ),
                status=AirbyteStreamStatus.COMPLETE,
            ),
        ),
    )


class AirbyteMessageIterator:
    """Abstract base class for Airbyte message iterables.

    This class behaves like Iterator[AirbyteMessage] but it can also be used
    as IO[str]. In the latter case, it will return the JSON string representation of
    the all messages in the iterator.
    """

    def __init__(
        self,
        iterable: Iterable[AirbyteMessage],
    ) -> None:
        self._iterator: Iterator[AirbyteMessage] = iter(iterable)

    @final
    def __iter__(self) -> Iterator[AirbyteMessage]:
        """The class itself is not a iterator but this method makes it iterable."""
        return iter(self._iterator)

    @final
    def __next__(self) -> AirbyteMessage:
        """Delegate to the internal iterator."""
        return next(self._iterator)

    @final
    def read(self) -> str:
        """Read the next message from the iterator."""
        return json.dumps(asdict(next(self)))

    @classmethod
    def from_read_result(cls, read_result: ReadResult) -> AirbyteMessageIterator:
        """Create a iterator from a `ReadResult` object."""
        state_provider = read_result.cache.get_state_provider(
            source_name=read_result.source_name,
            refresh=True,
        )

        def generator() -> Generator[AirbyteMessage, None, None]:
            for stream_name, dataset in read_result.items():
                for record in dataset:
                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(
                            stream=stream_name,
                            data=record,
                            emitted_at=int(cast(datetime.datetime, record.get(AB_EXTRACTED_AT_COLUMN)).timestamp()),
                            # `meta` and `namespace` are not handled:
                            meta=None,
                            namespace=None,
                        ),
                    )

                # Send the latest state message from the source.
                if stream_name in state_provider.known_stream_names:
                    yield AirbyteMessage(
                        type=Type.STATE,
                        state=state_provider.get_stream_state(stream_name),
                    )

                yield _new_stream_success_message(stream_name)

        return cls(generator())

    @classmethod
    def from_str_buffer(cls, buffer: IO[str]) -> AirbyteMessageIterator:
        """Create a iterator that reads messages from a buffer."""

        def generator() -> Generator[AirbyteMessage, None, None]:
            """Yields AirbyteMessage objects read from STDIN."""
            while True:
                next_line: str | None = next(buffer, None)  # Read the next line from STDIN
                if next_line is None:
                    # End of file (EOF) indicates no more input from STDIN
                    break
                try:
                    # Let Pydantic handle the JSON decoding from the raw string
                    yield AirbyteMessage(**json.loads(next_line))
                except pydantic.ValidationError:
                    # Handle JSON decoding errors (optional)
                    raise ValueError("Invalid JSON format")  # noqa: B904, TRY003

        return cls(generator())

    @classmethod
    def from_str_iterable(cls, buffer: Iterable[str]) -> AirbyteMessageIterator:
        """Yields AirbyteMessage objects read from STDIN."""

        def generator() -> Generator[AirbyteMessage, None, None]:
            for line in buffer:
                try:
                    # Let Pydantic handle the JSON decoding from the raw string
                    yield AirbyteMessage(**json.loads(line))
                except pydantic.ValidationError:
                    # Handle JSON decoding errors (optional)
                    raise ValueError(f"Invalid JSON format in input string: {line}")  # noqa: B904, TRY003

        return cls(generator())

    @classmethod
    def from_stdin(cls) -> AirbyteMessageIterator:
        """Create an iterator that reads messages from STDIN."""
        return cls.from_str_buffer(sys.stdin)

    @classmethod
    def from_files(cls, file_iterator: Iterator[Path], file_opener: Callable[[Path], IO[str]]) -> AirbyteMessageIterator:
        """Create an iterator that reads messages from a file iterator."""

        def generator() -> Generator[AirbyteMessage, None, None]:
            current_file_buffer: IO[str] | None = None
            current_file: Path | None = None
            while True:
                if current_file_buffer is None:
                    try:
                        current_file = next(file_iterator)
                        current_file_buffer = file_opener(current_file)
                    except StopIteration:
                        # No more files to read; Exit the loop
                        break

                next_line: str = current_file_buffer.readline()
                if next_line == "":  # noqa: PLC1901  # EOF produces an empty string
                    # Close the current file and open the next one
                    current_file_buffer.close()
                    current_file_buffer = None  # Ensure the buffer is reset
                    continue  # Skip further processing and move to the next file

                try:
                    # Let Pydantic handle the JSON decoding from the raw string
                    yield AirbyteMessage(**json.loads(next_line))
                except pydantic.ValidationError:
                    # Handle JSON decoding errors
                    current_file_buffer.close()
                    current_file_buffer = None
                    raise ValueError("Invalid JSON format")  # noqa: B904, TRY003

        return cls(generator())
