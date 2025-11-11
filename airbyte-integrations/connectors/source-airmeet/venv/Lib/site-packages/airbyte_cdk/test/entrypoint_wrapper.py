# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""
The AirbyteEntrypoint is important because it is a service layer that orchestrate how we execute commands from the
[common interface](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol#common-interface) through the source Python
implementation. There is some logic about which message we send to the platform and when which is relevant for integration testing. Other
than that, there are integrations point that are annoying to integrate with using Python code:
* Sources communicate with the platform using stdout. The implication is that the source could just print every message instead of
    returning things to source.<method> or to using the message repository. WARNING: As part of integration testing, we will not support
    messages that are simply printed. The reason is that capturing stdout relies on overriding sys.stdout (see
    https://docs.python.org/3/library/contextlib.html#contextlib.redirect_stdout) which clashes with how pytest captures logs and brings
    considerations for multithreaded applications. If code you work with uses `print` statements, please migrate to
    source.message_repository to emit those messages
* The entrypoint interface relies on file being written on the file system
"""

import json
import logging
import re
import tempfile
import traceback
from collections import deque
from collections.abc import Generator, Mapping
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, List, Literal, Optional, Union, final, overload

import orjson
from pydantic import ValidationError as V2ValidationError
from serpyco_rs import SchemaValidationError

from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.exception_handler import assemble_uncaught_exception
from airbyte_cdk.logger import AirbyteLogFormatter
from airbyte_cdk.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteMessageSerializer,
    AirbyteStateMessage,
    AirbyteStateMessageSerializer,
    AirbyteStreamState,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteCatalogSerializer,
    Level,
    TraceType,
    Type,
)
from airbyte_cdk.sources import Source
from airbyte_cdk.test.models.scenario import ExpectedOutcome


class AirbyteEntrypointException(Exception):
    """Exception raised for errors in the AirbyteEntrypoint execution.

    Used to provide details of an Airbyte connector execution failure in the output
    captured in an `EntrypointOutput` object. Use `EntrypointOutput.as_exception()` to
    convert it to an exception.

    Example Usage:
        output = EntrypointOutput(...)
        if output.errors:
            raise output.as_exception()
    """

    message: str = ""

    def __post_init__(self) -> None:
        super().__init__(self.message)


class EntrypointOutput:
    """A class to encapsulate the output of an Airbyte connector's execution.

    This class can be initialized with a list of messages or a file containing messages.
    It provides methods to access different types of messages produced during the execution
    of an Airbyte connector, including both successful messages and error messages.

    When working with records and state messages, it provides both a list and an iterator
    implementation. Lists are easier to work with, but generators are better suited to handle
    large volumes of messages without overflowing the available memory.
    """

    def __init__(
        self,
        messages: list[str] | None = None,
        uncaught_exception: Optional[BaseException] = None,
        *,
        command: list[str] | None = None,
        message_file: Path | None = None,
    ) -> None:
        if messages is None and message_file is None:
            raise ValueError("Either messages or message_file must be provided")
        if messages is not None and message_file is not None:
            raise ValueError("Only one of messages or message_file can be provided")

        self._command = command
        self._messages: list[AirbyteMessage] | None = None
        self._message_file: Path | None = message_file
        if messages:
            try:
                self._messages = [self._parse_message(message) for message in messages]
            except V2ValidationError as exception:
                raise ValueError("All messages are expected to be AirbyteMessage") from exception

        if uncaught_exception:
            if self._messages is None:
                self._messages = []

            self._messages.append(
                assemble_uncaught_exception(
                    type(uncaught_exception), uncaught_exception
                ).as_airbyte_message()
            )

    @staticmethod
    def _parse_message(message: str) -> AirbyteMessage:
        try:
            return AirbyteMessageSerializer.load(orjson.loads(message))
        except (orjson.JSONDecodeError, SchemaValidationError):
            # The platform assumes that logs that are not of AirbyteMessage format are log messages
            return AirbyteMessage(
                type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=message)
            )

    @property
    def records_and_state_messages(
        self,
    ) -> list[AirbyteMessage]:
        return self.get_message_by_types(
            message_types=[Type.RECORD, Type.STATE],
            safe_iterator=False,
        )

    def records_and_state_messages_iterator(
        self,
    ) -> Generator[AirbyteMessage, None, None]:
        """Returns a generator that yields record and state messages one by one.

        Use this instead of `records_and_state_messages` when the volume of messages could be large
        enough to overload available memory.
        """
        return self.get_message_by_types(
            message_types=[Type.RECORD, Type.STATE],
            safe_iterator=True,
        )

    @property
    def records(self) -> List[AirbyteMessage]:
        return self.get_message_by_types([Type.RECORD])

    @property
    def records_iterator(self) -> Generator[AirbyteMessage, None, None]:
        """Returns a generator that yields record messages one by one.

        Use this instead of `records` when the volume of records could be large
        enough to overload available memory.
        """
        return self.get_message_by_types([Type.RECORD], safe_iterator=True)

    @property
    def state_messages(self) -> List[AirbyteMessage]:
        return self.get_message_by_types([Type.STATE])

    @property
    def spec_messages(self) -> List[AirbyteMessage]:
        return self.get_message_by_types([Type.SPEC])

    @property
    def connection_status_messages(self) -> List[AirbyteMessage]:
        return self.get_message_by_types([Type.CONNECTION_STATUS])

    @property
    def most_recent_state(self) -> AirbyteStreamState | None:
        state_message_iterator = self.get_message_by_types(
            [Type.STATE],
            safe_iterator=True,
        )
        # Use a deque with maxlen=1 to efficiently get the last state message
        double_ended_queue = deque(state_message_iterator, maxlen=1)
        try:
            final_state_message: AirbyteMessage = double_ended_queue.pop()
        except IndexError:
            raise ValueError(
                "Can't provide most recent state as there are no state messages."
            ) from None

        return final_state_message.state.stream  # type: ignore[union-attr] # state has `stream`

    @property
    def logs(self) -> List[AirbyteMessage]:
        return self.get_message_by_types([Type.LOG])

    @property
    def trace_messages(self) -> List[AirbyteMessage]:
        return self.get_message_by_types([Type.TRACE])

    @property
    def analytics_messages(self) -> List[AirbyteMessage]:
        return self._get_trace_message_by_trace_type(TraceType.ANALYTICS)

    @property
    def errors(self) -> List[AirbyteMessage]:
        return self._get_trace_message_by_trace_type(TraceType.ERROR)

    def get_formatted_error_message(self) -> str:
        """Returns a human-readable error message with the contents.

        If there are no errors, returns an empty string.
        """
        errors = self.errors
        if not errors:
            # If there are no errors, return an empty string.
            return ""

        result = "Failed to run airbyte command"
        result += ": " + " ".join(self._command) if self._command else "."
        result += "\n" + "\n".join(
            [str(error.trace.error).replace("\\n", "\n") for error in errors if error.trace],
        )
        return result

    def as_exception(self) -> AirbyteEntrypointException:
        """Convert the output to an exception."""
        return AirbyteEntrypointException(self.get_formatted_error_message())

    def raise_if_errors(
        self,
    ) -> None:
        """Raise an exception if there are errors in the output.

        Otherwise, do nothing.
        """
        if not self.errors:
            return None

        raise self.as_exception()

    @property
    def catalog(self) -> AirbyteMessage:
        catalog = self.get_message_by_types([Type.CATALOG])
        if len(catalog) != 1:
            raise ValueError(f"Expected exactly one catalog but got {len(catalog)}")
        return catalog[0]

    def get_stream_statuses(self, stream_name: str) -> List[AirbyteStreamStatus]:
        status_messages = map(
            lambda message: message.trace.stream_status.status,  # type: ignore
            filter(
                lambda message: message.trace.stream_status.stream_descriptor.name == stream_name,  # type: ignore # callable; trace has `stream_status`
                self._get_trace_message_by_trace_type(TraceType.STREAM_STATUS),
            ),
        )
        return list(status_messages)

    def get_message_iterator(self) -> Generator[AirbyteMessage, None, None]:
        """Creates a generator which yields messages one by one.

        This will iterate over all messages in the output file (if provided) or the messages
        provided during initialization. File results are provided first, followed by any
        messages that were passed in directly.
        """
        if self._message_file:
            try:
                with open(self._message_file, "r", encoding="utf-8") as file:
                    for line in file:
                        if not line.strip():
                            # Skip empty lines
                            continue

                        yield self._parse_message(line.strip())
            except FileNotFoundError:
                raise ValueError(f"Message file {self._message_file} not found")

        if self._messages is not None:
            yield from self._messages

    # Overloads to provide proper type hints for different usages of `get_message_by_types`.

    @overload
    def get_message_by_types(
        self,
        message_types: list[Type],
    ) -> list[AirbyteMessage]: ...

    @overload
    def get_message_by_types(
        self,
        message_types: list[Type],
        *,
        safe_iterator: Literal[False],
    ) -> list[AirbyteMessage]: ...

    @overload
    def get_message_by_types(
        self,
        message_types: list[Type],
        *,
        safe_iterator: Literal[True],
    ) -> Generator[AirbyteMessage, None, None]: ...

    def get_message_by_types(
        self,
        message_types: list[Type],
        *,
        safe_iterator: bool = False,
    ) -> list[AirbyteMessage] | Generator[AirbyteMessage, None, None]:
        """Get messages of specific types.

        If `safe_iterator` is True, returns a generator that yields messages one by one.
        If `safe_iterator` is False, returns a list of messages.

        Use `safe_iterator=True` when the volume of messages could overload the available
        memory.
        """
        message_generator = self.get_message_iterator()

        if safe_iterator:
            return (message for message in message_generator if message.type in message_types)

        return [message for message in message_generator if message.type in message_types]

    def _get_trace_message_by_trace_type(self, trace_type: TraceType) -> List[AirbyteMessage]:
        return [
            message
            for message in self.get_message_by_types(
                [Type.TRACE],
                safe_iterator=True,
            )
            if message.trace.type == trace_type  # type: ignore[union-attr] # trace has `type`
        ]

    def is_in_logs(self, pattern: str) -> bool:
        """Check if any log message case-insensitive matches the pattern."""
        return any(
            re.search(
                pattern,
                entry.log.message,  # type: ignore[union-attr] # log has `message`
                flags=re.IGNORECASE,
            )
            for entry in self.logs
        )

    def is_not_in_logs(self, pattern: str) -> bool:
        """Check if no log message matches the case-insensitive pattern."""
        return not self.is_in_logs(pattern)


def _run_command(
    source: Source,
    args: List[str],
    expecting_exception: bool | None = None,  # Deprecated, use `expected_outcome` instead.
    *,
    expected_outcome: ExpectedOutcome | None = None,
) -> EntrypointOutput:
    """Internal function to run a command with the AirbyteEntrypoint.

    Note: Even though this function is private, some connectors do call it directly.

    Note: The `expecting_exception` arg is now deprecated in favor of the tri-state
    `expected_outcome` arg. The old argument is supported (for now) for backwards compatibility.
    """
    expected_outcome = expected_outcome or ExpectedOutcome.from_expecting_exception_bool(
        expecting_exception,
    )
    log_capture_buffer = StringIO()
    stream_handler = logging.StreamHandler(log_capture_buffer)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(AirbyteLogFormatter())
    parent_logger = logging.getLogger("")
    parent_logger.addHandler(stream_handler)

    parsed_args = AirbyteEntrypoint.parse_args(args)

    source_entrypoint = AirbyteEntrypoint(source)
    messages: list[str] = []
    uncaught_exception = None
    try:
        for message in source_entrypoint.run(parsed_args):
            messages.append(message)
    except Exception as exception:
        if expected_outcome.expect_success():
            print("Printing unexpected error from entrypoint_wrapper")
            print("".join(traceback.format_exception(None, exception, exception.__traceback__)))

        uncaught_exception = exception

    captured_logs = log_capture_buffer.getvalue().split("\n")[:-1]

    parent_logger.removeHandler(stream_handler)
    return EntrypointOutput(
        messages=messages + captured_logs,
        uncaught_exception=uncaught_exception,
    )


def discover(
    source: Source,
    config: Mapping[str, Any],
    expecting_exception: bool | None = None,  # Deprecated, use `expected_outcome` instead.
    *,
    expected_outcome: ExpectedOutcome | None = None,
) -> EntrypointOutput:
    """
    config must be json serializable
    :param expected_outcome: By default if there is an uncaught exception, the exception will be printed out. If this is expected, please
        provide `expected_outcome=ExpectedOutcome.EXPECT_FAILURE` so that the test output logs are cleaner
    """

    with tempfile.TemporaryDirectory() as tmp_directory:
        tmp_directory_path = Path(tmp_directory)
        config_file = make_file(tmp_directory_path / "config.json", config)

        return _run_command(
            source,
            ["discover", "--config", config_file, "--debug"],
            expecting_exception=expecting_exception,  # Deprecated, but still supported.
            expected_outcome=expected_outcome,
        )


def read(
    source: Source,
    config: Mapping[str, Any],
    catalog: ConfiguredAirbyteCatalog,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: bool | None = None,  # Deprecated, use `expected_outcome` instead.
    *,
    expected_outcome: ExpectedOutcome | None = None,
    debug: bool = False,
) -> EntrypointOutput:
    """
    config and state must be json serializable

    :param expected_outcome: By default if there is an uncaught exception, the exception will be printed out. If this is expected, please
        provide `expected_outcome=ExpectedOutcome.EXPECT_FAILURE` so that the test output logs are cleaner.
    """
    with tempfile.TemporaryDirectory() as tmp_directory:
        tmp_directory_path = Path(tmp_directory)
        config_file = make_file(tmp_directory_path / "config.json", config)
        catalog_file = make_file(
            tmp_directory_path / "catalog.json",
            orjson.dumps(ConfiguredAirbyteCatalogSerializer.dump(catalog)).decode(),
        )
        args = [
            "read",
            "--config",
            config_file,
            "--catalog",
            catalog_file,
        ]
        if debug:
            args.append("--debug")
        if state is not None:
            args.extend(
                [
                    "--state",
                    make_file(
                        tmp_directory_path / "state.json",
                        f"[{','.join([orjson.dumps(AirbyteStateMessageSerializer.dump(stream_state)).decode() for stream_state in state])}]",
                    ),
                ]
            )

        return _run_command(
            source,
            args,
            expecting_exception=expecting_exception,  # Deprecated, but still supported.
            expected_outcome=expected_outcome,
        )


def make_file(
    path: Path, file_contents: Optional[Union[str, Mapping[str, Any], List[Mapping[str, Any]]]]
) -> str:
    if isinstance(file_contents, str):
        path.write_text(file_contents)
    else:
        path.write_text(json.dumps(file_contents))
    return str(path)
