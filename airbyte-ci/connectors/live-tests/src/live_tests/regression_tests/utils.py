# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import json
import logging
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

import pytest
from airbyte_protocol.models import AirbyteMessage, Type  # type: ignore
from deepdiff import DeepDiff  # type: ignore
from live_tests.commons.models import ExecutionResult

from . import stash_keys
from .consts import MAX_LINES_IN_REPORT

if TYPE_CHECKING:
    from _pytest.fixtures import SubRequest

MAX_DIFF_SIZE_FOR_LOGGING = 500


def get_test_logger(request: SubRequest) -> logging.Logger:
    return logging.getLogger(request.node.name)


def filter_records(messages: Iterable[AirbyteMessage]) -> Iterable[AirbyteMessage]:
    for message in messages:
        if message.type is Type.RECORD:
            yield message


def write_string_to_test_artifact(request: SubRequest, content: str, filename: str, subdir: Optional[Path] = None) -> Path:
    test_artifact_directory = request.config.stash[stash_keys.TEST_ARTIFACT_DIRECTORY]
    if subdir:
        test_artifact_directory = test_artifact_directory / subdir
    test_artifact_directory.mkdir(parents=True, exist_ok=True)
    artifact_path = test_artifact_directory / filename
    artifact_path.write_text(content)
    return artifact_path


def get_and_write_diff(
    request: SubRequest,
    control_data: Union[list, dict],
    target_data: Union[list, dict],
    filepath: str,
    ignore_order: bool,
    exclude_paths: Optional[list[str]],
) -> str:
    logger = get_test_logger(request)
    diff = DeepDiff(
        control_data,
        target_data,
        ignore_order=ignore_order,
        report_repetition=True,
        exclude_regex_paths=exclude_paths,
    )
    if diff:
        diff_json = diff.to_json()
        parsed_diff = json.loads(diff_json)
        formatted_diff_json = json.dumps(parsed_diff, indent=2)

        diff_path_tree = write_string_to_test_artifact(request, str(diff.tree), f"{filepath}_tree.txt", subdir=request.node.name)
        diff_path_text = write_string_to_test_artifact(
            request,
            formatted_diff_json,
            f"{filepath}_text.txt",
            subdir=request.node.name,
        )
        diff_path_pretty = write_string_to_test_artifact(
            request,
            str(diff.pretty()),
            f"{filepath}_pretty.txt",
            subdir=request.node.name,
        )

        logger.info(f"Diff file are stored in {diff_path_tree}, {diff_path_text}, and {diff_path_pretty}.")
        if len(diff_json.encode("utf-8")) < MAX_DIFF_SIZE_FOR_LOGGING:
            logger.error(formatted_diff_json)

        return formatted_diff_json
    return ""


def fail_test_on_failing_execution_results(record_property: Callable, execution_results: list[ExecutionResult]) -> None:
    error_messages = []
    for execution_result in execution_results:
        if not execution_result.success:
            property_suffix = f"of failing execution {execution_result.command.value} on {execution_result.connector_under_test.name}:{execution_result.connector_under_test.version} [{MAX_LINES_IN_REPORT} last lines]"
            record_property(
                f"Stdout {property_suffix}",
                tail_file(execution_result.stdout_file_path, n=MAX_LINES_IN_REPORT),
            )
            record_property(
                f"Stderr of {property_suffix}",
                tail_file(execution_result.stderr_file_path, n=MAX_LINES_IN_REPORT),
            )
            error_messages.append(
                f"Failed executing command {execution_result.command} on {execution_result.connector_under_test.name}:{execution_result.connector_under_test.version}"
            )
    if error_messages:
        pytest.fail("\n".join(error_messages))


def tail_file(file_path: Path, n: int = MAX_LINES_IN_REPORT) -> list[str]:
    with open(file_path) as f:
        # Move the cursor to the end of the file
        f.seek(0, 2)
        file_size = f.tell()
        lines: list[str] = []
        read_size = min(4096, file_size)
        cursor = file_size - read_size

        # Read chunks of the file until we've found n lines
        while len(lines) < n and cursor >= 0:
            f.seek(cursor)
            chunk = f.read(read_size)
            lines.extend(chunk.splitlines(True)[-n:])
            cursor -= read_size

        # Return the last n lines
        return lines[-n:]
