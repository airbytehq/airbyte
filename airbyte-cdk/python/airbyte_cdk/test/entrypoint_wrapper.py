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
from io import StringIO
from pathlib import Path
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.exception_handler import assemble_uncaught_exception
from airbyte_cdk.logger import AirbyteLogFormatter
from airbyte_cdk.sources import Source
from airbyte_protocol.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    Level,
    TraceType,
    Type,
)
from pydantic import ValidationError as V2ValidationError


class EntrypointOutput:
    def __init__(self, messages: List[str], uncaught_exception: Optional[BaseException] = None):
        try:
            self._messages = [self._parse_message(message) for message in messages]
        except V2ValidationError as exception:
            raise ValueError("All messages are expected to be AirbyteMessage") from exception

        if uncaught_exception:
            self._messages.append(assemble_uncaught_exception(type(uncaught_exception), uncaught_exception).as_airbyte_message())

    @staticmethod
    def _parse_message(message: str) -> AirbyteMessage:
        try:
            return AirbyteMessage.parse_obj(json.loads(message))
        except (json.JSONDecodeError, V2ValidationError):
            # The platform assumes that logs that are not of AirbyteMessage format are log messages
            return AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=message))

    @property
    def records_and_state_messages(self) -> List[AirbyteMessage]:
        return self._get_message_by_types([Type.RECORD, Type.STATE])

    @property
    def records(self) -> List[AirbyteMessage]:
        return self._get_message_by_types([Type.RECORD])

    @property
    def state_messages(self) -> List[AirbyteMessage]:
        return self._get_message_by_types([Type.STATE])

    @property
    def most_recent_state(self) -> Any:
        state_messages = self._get_message_by_types([Type.STATE])
        if not state_messages:
            raise ValueError("Can't provide most recent state as there are no state messages")
        return state_messages[-1].state.stream

    @property
    def logs(self) -> List[AirbyteMessage]:
        return self._get_message_by_types([Type.LOG])

    @property
    def trace_messages(self) -> List[AirbyteMessage]:
        return self._get_message_by_types([Type.TRACE])

    @property
    def analytics_messages(self) -> List[AirbyteMessage]:
        return self._get_trace_message_by_trace_type(TraceType.ANALYTICS)

    @property
    def errors(self) -> List[AirbyteMessage]:
        return self._get_trace_message_by_trace_type(TraceType.ERROR)

    @property
    def catalog(self) -> AirbyteMessage:
        catalog = self._get_message_by_types([Type.CATALOG])
        if len(catalog) != 1:
            raise ValueError(f"Expected exactly one catalog but got {len(catalog)}")
        return catalog[0]

    def get_stream_statuses(self, stream_name: str) -> List[AirbyteStreamStatus]:
        status_messages = map(
            lambda message: message.trace.stream_status.status,
            filter(
                lambda message: message.trace.stream_status.stream_descriptor.name == stream_name,
                self._get_trace_message_by_trace_type(TraceType.STREAM_STATUS),
            ),
        )
        return list(status_messages)

    def _get_message_by_types(self, message_types: List[Type]) -> List[AirbyteMessage]:
        return [message for message in self._messages if message.type in message_types]

    def _get_trace_message_by_trace_type(self, trace_type: TraceType) -> List[AirbyteMessage]:
        return [message for message in self._get_message_by_types([Type.TRACE]) if message.trace.type == trace_type]

    def is_in_logs(self, pattern: str) -> bool:
        """Check if any log message case-insensitive matches the pattern."""
        return any(re.search(pattern, entry.log.message, flags=re.IGNORECASE) for entry in self.logs)

    def is_not_in_logs(self, pattern: str) -> bool:
        """Check if no log message matches the case-insensitive pattern."""
        return not self.is_in_logs(pattern)


def _run_command(source: Source, args: List[str], expecting_exception: bool = False) -> EntrypointOutput:
    log_capture_buffer = StringIO()
    stream_handler = logging.StreamHandler(log_capture_buffer)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(AirbyteLogFormatter())
    parent_logger = logging.getLogger("")
    parent_logger.addHandler(stream_handler)

    parsed_args = AirbyteEntrypoint.parse_args(args)

    source_entrypoint = AirbyteEntrypoint(source)
    messages = []
    uncaught_exception = None
    try:
        for message in source_entrypoint.run(parsed_args):
            messages.append(message)
    except Exception as exception:
        if not expecting_exception:
            print("Printing unexpected error from entrypoint_wrapper")
            print("".join(traceback.format_exception(None, exception, exception.__traceback__)))
        uncaught_exception = exception

    captured_logs = log_capture_buffer.getvalue().split("\n")[:-1]

    parent_logger.removeHandler(stream_handler)

    return EntrypointOutput(messages + captured_logs, uncaught_exception)


def discover(
    source: Source,
    config: Mapping[str, Any],
    expecting_exception: bool = False,
) -> EntrypointOutput:
    """
    config must be json serializable
    :param expecting_exception: By default if there is an uncaught exception, the exception will be printed out. If this is expected, please
        provide expecting_exception=True so that the test output logs are cleaner
    """

    with tempfile.TemporaryDirectory() as tmp_directory:
        tmp_directory_path = Path(tmp_directory)
        config_file = make_file(tmp_directory_path / "config.json", config)

        return _run_command(source, ["discover", "--config", config_file, "--debug"], expecting_exception)


def read(
    source: Source,
    config: Mapping[str, Any],
    catalog: ConfiguredAirbyteCatalog,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    """
    config and state must be json serializable

    :param expecting_exception: By default if there is an uncaught exception, the exception will be printed out. If this is expected, please
        provide expecting_exception=True so that the test output logs are cleaner
    """
    with tempfile.TemporaryDirectory() as tmp_directory:
        tmp_directory_path = Path(tmp_directory)
        config_file = make_file(tmp_directory_path / "config.json", config)
        catalog_file = make_file(tmp_directory_path / "catalog.json", catalog.model_dump_json())
        args = [
            "read",
            "--config",
            config_file,
            "--catalog",
            catalog_file,
        ]
        if state is not None:
            args.extend(
                [
                    "--state",
                    make_file(
                        tmp_directory_path / "state.json", f"[{','.join([stream_state.model_dump_json() for stream_state in state])}]"
                    ),
                ]
            )

        return _run_command(source, args, expecting_exception)


def make_file(path: Path, file_contents: Optional[Union[str, Mapping[str, Any], List[Mapping[str, Any]]]]) -> str:
    if isinstance(file_contents, str):
        path.write_text(file_contents)
    else:
        path.write_text(json.dumps(file_contents))
    return str(path)
