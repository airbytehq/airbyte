# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import json
from collections.abc import Callable, Generator, Iterable
from typing import TYPE_CHECKING, Any, Optional

import pytest
from airbyte_protocol.models import AirbyteMessage  # type: ignore
from deepdiff import DeepDiff  # type: ignore
from live_tests.commons.models import ExecutionResult
from live_tests.utils import fail_test_on_failing_execution_results, get_and_write_diff, get_test_logger, write_string_to_test_artifact

if TYPE_CHECKING:
    from _pytest.fixtures import SubRequest

pytestmark = [
    pytest.mark.anyio,
]


EXCLUDE_PATHS = ["emitted_at"]


class TestDataIntegrity:
    """This class contains tests that check if the data integrity is preserved between the control and target versions.
    The tests have some overlap but they are meant to be gradually stricter in terms of integrity checks.

    1. test_record_count: On each stream, check if the target version produces at least the same number of records as the control version.
    2. test_all_pks_are_produced_in_target_version: On each stream, check if all primary key values produced by the control version are present in the target version.
    3. test_all_records_are_the_same: On each stream, check if all records produced by the control version are the same as in the target version. This will write a diff of the records to the test artifacts.

    All these test have a full refresh and incremental variant.
    """

    async def _check_all_pks_are_produced_in_target_version(
        self,
        request: SubRequest,
        record_property: Callable,
        configured_streams: Iterable[str],
        primary_keys_per_stream: dict[str, Optional[list[str]]],
        read_with_state_control_execution_result: ExecutionResult,
        read_with_state_target_execution_result: ExecutionResult,
    ) -> None:
        """This test gathers all primary key values from the control version and checks if they are present in the target version for each stream.
        If there are missing primary keys, the test fails and the missing records are stored in the test artifacts.
        Args:
            request (SubRequest): The test request.
            record_property (Callable): A callable for stashing information on the report.
            streams: (Iterable[str]): The list of streams configured for the connection.
            primary_keys_per_stream (Dict[str, Optional[List[str]]]): The primary keys for each stream.
            read_with_state_control_execution_result (ExecutionResult): The control version execution result.
            read_with_state_target_execution_result (ExecutionResult): The target version execution result.
        """
        if not primary_keys_per_stream:
            pytest.skip("No primary keys provided on any stream. Skipping the test.")

        logger = get_test_logger(request)
        streams_with_missing_records = set()
        for stream_name in configured_streams:
            _primary_key = primary_keys_per_stream[stream_name]
            if not _primary_key:
                # TODO: report skipped PK test per individual stream
                logger.warning(f"No primary keys provided on stream {stream_name}.")
                continue

            primary_key = _primary_key[0] if isinstance(_primary_key, list) else _primary_key

            control_pks = set()
            target_pks = set()
            logger.info(f"Retrieving primary keys for stream {stream_name} on control version.")
            for control_record in read_with_state_control_execution_result.get_records_per_stream(stream_name):
                control_pks.add(control_record.record.data[primary_key])

            logger.info(f"Retrieving primary keys for stream {stream_name} on target version.")
            for target_record in read_with_state_target_execution_result.get_records_per_stream(stream_name):
                target_pks.add(target_record.record.data[primary_key])

            if missing_pks := control_pks - target_pks:
                logger.warning(f"Found {len(missing_pks)} primary keys for stream {stream_name}. Retrieving missing records.")
                streams_with_missing_records.add(stream_name)
                missing_records = [
                    r
                    for r in read_with_state_control_execution_result.get_records_per_stream(stream_name)
                    if r.record.data[primary_key] in missing_pks
                ]
                record_property(
                    f"Missing records on stream {stream_name}",
                    json.dumps(missing_records),
                )
                artifact_path = write_string_to_test_artifact(
                    request,
                    json.dumps(missing_records),
                    f"missing_records_{stream_name}.json",
                    subdir=request.node.name,
                )
                logger.info(f"Missing records for stream {stream_name} are stored in {artifact_path}.")
        if streams_with_missing_records:
            pytest.fail(f"Missing records for streams: {', '.join(streams_with_missing_records)}.")

    async def _check_record_counts(
        self,
        record_property: Callable,
        configured_streams: Iterable[str],
        read_control_execution_result: ExecutionResult,
        read_target_execution_result: ExecutionResult,
    ) -> None:
        record_count_difference_per_stream: dict[str, dict[str, int]] = {}
        for stream_name in configured_streams:
            control_records_count = sum(1 for _ in read_control_execution_result.get_records_per_stream(stream_name))
            target_records_count = sum(1 for _ in read_target_execution_result.get_records_per_stream(stream_name))

            difference = {
                "delta": target_records_count - control_records_count,
                "control": control_records_count,
                "target": target_records_count,
            }

            if difference["delta"] != 0:
                record_count_difference_per_stream[stream_name] = difference
        error_messages = []
        for stream, difference in record_count_difference_per_stream.items():
            if difference["delta"] > 0:
                error_messages.append(
                    f"Stream {stream} has {difference['delta']} more records in the target version ({difference['target']} vs. {difference['control']})."
                )
            if difference["delta"] < 0:
                error_messages.append(
                    f"Stream {stream} has {-difference['delta']} fewer records in the target version({difference['target']} vs. {difference['control']})."
                )
        if error_messages:
            record_property("Record count differences", "\n".join(error_messages))
            pytest.fail("Record counts are different.")

    async def _check_all_records_are_the_same(
        self,
        request: SubRequest,
        record_property: Callable,
        configured_streams: Iterable[str],
        primary_keys_per_stream: dict[str, Optional[list[str]]],
        read_control_execution_result: ExecutionResult,
        read_target_execution_result: ExecutionResult,
    ) -> None:
        """This test checks if all records in the control version are present in the target version for each stream.
        If there are mismatches, the test fails and the missing records are stored in the test artifacts.
        It will catch differences in record schemas, missing records, and extra records.

        Args:
            request (SubRequest): The test request.
            read_control_execution_result (ExecutionResult): The control version execution result.
            read_target_execution_result (ExecutionResult): The target version execution result.
        """
        streams_with_diff = set()
        for stream in configured_streams:
            control_records = list(read_control_execution_result.get_records_per_stream(stream))
            target_records = list(read_target_execution_result.get_records_per_stream(stream))

            if control_records and not target_records:
                pytest.fail(f"Stream {stream} is missing in the target version.")

            if primary_key := primary_keys_per_stream.get(stream):
                diffs = self._get_diff_on_stream_with_pk(
                    request,
                    record_property,
                    stream,
                    control_records,
                    target_records,
                    primary_key,
                )
            else:
                diffs = self._get_diff_on_stream_without_pk(
                    request,
                    record_property,
                    stream,
                    control_records,
                    target_records,
                )

            if diffs:
                streams_with_diff.add(stream)

        if streams_with_diff:
            messages = [
                f"Records for stream {stream} are different. Please check the diff in the test artifacts for debugging."
                for stream in sorted(streams_with_diff)
            ]
            pytest.fail("/n".join(messages))

    def _check_record_schema_match(
        self,
        request: SubRequest,
        record_property: Callable,
        control_execution_result: ExecutionResult,
        target_execution_result: ExecutionResult,
    ) -> None:
        """This test checks if the schema of the records in the control and target versions match.
        It compares the meta schema inferred for each streams on the control and target versions.
        It also fetches an example record for each stream from the DuckDB instance and compares the schema of the records.

        Args:
            record_property (Callable): The record property to store the mismatching fields.
            control_execution_result (ExecutionResult): The control version execution result.
            target_execution_result (ExecutionResult): The target version execution result.
        """
        logger = get_test_logger(request)

        assert control_execution_result.stream_schemas is not None, "Control schemas were not inferred."
        assert target_execution_result.stream_schemas is not None, "Target schemas were not inferred."

        mismatches_count = 0
        for stream in control_execution_result.stream_schemas:
            control_schema = control_execution_result.stream_schemas.get(stream, {})
            if not control_schema:
                logger.warning(f"Stream {stream} was not found in the control results.")

            target_schema = target_execution_result.stream_schemas.get(stream, {})
            if control_schema and not target_schema:
                logger.warning(f"Stream {stream} was present in the control results but not in the target results.")

            diff = DeepDiff(control_schema, target_schema, ignore_order=True)
            if diff:
                record_property(f"{stream} diff between control and target version", diff.pretty())
                try:
                    control_record = next(control_execution_result.get_records_per_stream(stream))
                    control_example = json.dumps(control_record.record.data, indent=2)
                    record_property(f"{stream} example record for control version", control_example)
                except StopIteration:
                    logger.warning(f"Stream {stream} has no record in the control version.")
                try:
                    target_record = next(target_execution_result.get_records_per_stream(stream))
                    target_example = json.dumps(target_record.record.data, indent=2)
                    record_property(f"{stream} example record for target version", target_example)
                except StopIteration:
                    logger.warning(f"Stream {stream} has no record in the target version.")
                mismatches_count += 1

        if mismatches_count > 0:
            pytest.fail(f"{mismatches_count} streams have mismatching schemas between control and target versions.")

    @pytest.mark.with_state()
    async def test_record_count_with_state(
        self,
        record_property: Callable,
        configured_streams: Iterable[str],
        read_with_state_control_execution_result: ExecutionResult,
        read_with_state_target_execution_result: ExecutionResult,
    ) -> None:
        """This test compares the record counts between the control and target versions on each stream.
        Records are pulled from the output of the read command to which the connection state is passed.
        It fails if there are any differences in the record counts.
        It is not bulletproof, if the upstream source supports insertion or deletion it may lead to false positives.
        The HTTP cache used between the control and target versions command execution might limit this problem.
        Extra records in the target version might mean that a bug was fixed, but it could also mean that the target version produces duplicates.
        We should add a new test for duplicates and not fail this one if extra records are found.
        More advanced checks are done in the other tests.
        """
        fail_test_on_failing_execution_results(
            record_property,
            [
                read_with_state_control_execution_result,
                read_with_state_target_execution_result,
            ],
        )
        await self._check_record_counts(
            record_property,
            configured_streams,
            read_with_state_control_execution_result,
            read_with_state_target_execution_result,
        )

    @pytest.mark.without_state()
    async def test_record_count_without_state(
        self,
        record_property: Callable,
        configured_streams: Iterable[str],
        read_control_execution_result: ExecutionResult,
        read_target_execution_result: ExecutionResult,
    ) -> None:
        """This test compares the record counts between the control and target versions on each stream.
        Records are pulled from the output of the read command to which no connection state is passed (leading to a full-refresh like sync).
        It fails if there are any differences in the record counts.
        It is not bulletproof, if the upstream source supports insertion or deletion it may lead to false positives.
        The HTTP cache used between the control and target versions command execution might limit this problem.
        Extra records in the target version might mean that a bug was fixed, but it could also mean that the target version produces duplicates.
        We should add a new test for duplicates and not fail this one if extra records are found.
        More advanced checks are done in the other tests.
        """
        fail_test_on_failing_execution_results(
            record_property,
            [
                read_control_execution_result,
                read_target_execution_result,
            ],
        )
        await self._check_record_counts(
            record_property,
            configured_streams,
            read_control_execution_result,
            read_target_execution_result,
        )

    @pytest.mark.with_state()
    async def test_all_pks_are_produced_in_target_version_with_state(
        self,
        request: SubRequest,
        record_property: Callable,
        configured_streams: Iterable[str],
        primary_keys_per_stream: dict[str, Optional[list[str]]],
        read_with_state_control_execution_result: ExecutionResult,
        read_with_state_target_execution_result: ExecutionResult,
    ) -> None:
        """This test checks if all primary key values produced by the control version are present in the target version for each stream.
        It is reading the records from the output of the read command to which the connection state is passed.
        A failing test means that the target version is missing some records.
        """
        fail_test_on_failing_execution_results(
            record_property,
            [
                read_with_state_control_execution_result,
                read_with_state_target_execution_result,
            ],
        )
        await self._check_all_pks_are_produced_in_target_version(
            request,
            record_property,
            configured_streams,
            primary_keys_per_stream,
            read_with_state_control_execution_result,
            read_with_state_target_execution_result,
        )

    @pytest.mark.without_state()
    async def test_all_pks_are_produced_in_target_version_without_state(
        self,
        request: SubRequest,
        record_property: Callable,
        configured_streams: Iterable[str],
        primary_keys_per_stream: dict[str, Optional[list[str]]],
        read_control_execution_result: ExecutionResult,
        read_target_execution_result: ExecutionResult,
    ) -> None:
        """This test checks if all primary key values produced by the control version are present in the target version for each stream.
        Records are pulled from the output of the read command to which no connection state is passed (leading to a full-refresh like sync).
        A failing test means that the target version is missing some records.
        """
        fail_test_on_failing_execution_results(
            record_property,
            [
                read_control_execution_result,
                read_target_execution_result,
            ],
        )
        await self._check_all_pks_are_produced_in_target_version(
            request,
            record_property,
            configured_streams,
            primary_keys_per_stream,
            read_control_execution_result,
            read_target_execution_result,
        )

    @pytest.mark.with_state()
    async def test_record_schema_match_with_state(
        self,
        request: SubRequest,
        record_property: Callable,
        read_with_state_control_execution_result: ExecutionResult,
        read_with_state_target_execution_result: ExecutionResult,
    ) -> None:
        """This test checks if the schema of the streams in the control and target versions match.
        It produces a meta schema for each stream on control and target version and compares them.
        It is not using the catalog schema, but inferring schemas from the actual records produced by the read command.
        Records are pulled from the output of the read command to which the connection state is passed.
        """
        self._check_record_schema_match(
            request,
            record_property,
            read_with_state_control_execution_result,
            read_with_state_target_execution_result,
        )

    @pytest.mark.without_state()
    async def test_record_schema_match_without_state(
        self,
        request: SubRequest,
        record_property: Callable,
        read_control_execution_result: ExecutionResult,
        read_target_execution_result: ExecutionResult,
    ) -> None:
        """This test checks if the schema of the streams in the control and target versions match.
        It produces a meta schema for each stream on control and target version and compares them.
        It is not using the catalog schema, but inferring schemas from the actual records produced by the read command.
        Records are pulled from the output of the read command to which the connection state is passed.
        """
        self._check_record_schema_match(
            request,
            record_property,
            read_control_execution_result,
            read_target_execution_result,
        )

    @pytest.mark.allow_diagnostic_mode
    @pytest.mark.with_state()
    async def test_all_records_are_the_same_with_state(
        self,
        request: SubRequest,
        record_property: Callable,
        configured_streams: Iterable[str],
        primary_keys_per_stream: dict[str, Optional[list[str]]],
        read_with_state_control_execution_result: ExecutionResult,
        read_with_state_target_execution_result: ExecutionResult,
    ) -> None:
        """This test compares all records between the control and target versions on each stream.
        It is very sensitive to record schema and order changes.
        It fails if there are any differences in the records.
        It is reading the records from the output of the read command to which the connection state is passed.
        """
        fail_test_on_failing_execution_results(
            record_property,
            [
                read_with_state_control_execution_result,
                read_with_state_target_execution_result,
            ],
        )
        await self._check_all_records_are_the_same(
            request,
            record_property,
            configured_streams,
            primary_keys_per_stream,
            read_with_state_control_execution_result,
            read_with_state_target_execution_result,
        )

    @pytest.mark.allow_diagnostic_mode
    @pytest.mark.without_state()
    async def test_all_records_are_the_same_without_state(
        self,
        request: SubRequest,
        record_property: Callable,
        configured_streams: Iterable[str],
        primary_keys_per_stream: dict[str, Optional[list[str]]],
        read_control_execution_result: ExecutionResult,
        read_target_execution_result: ExecutionResult,
    ) -> None:
        """This test compares all records between the control and target versions on each stream.
        It is very sensitive to record schema and order changes.
        It fails if there are any differences in the records.
        It is reading the records from the output of the read command to which no connection state is passed (leading to a full-refresh like sync).
        """
        fail_test_on_failing_execution_results(
            record_property,
            [
                read_control_execution_result,
                read_target_execution_result,
            ],
        )
        await self._check_all_records_are_the_same(
            request,
            record_property,
            configured_streams,
            primary_keys_per_stream,
            read_control_execution_result,
            read_target_execution_result,
        )

    def _get_diff_on_stream_with_pk(
        self,
        request: SubRequest,
        record_property: Callable,
        stream: str,
        control_records: list[AirbyteMessage],
        target_records: list[AirbyteMessage],
        primary_key: list[str],
    ) -> Optional[Iterable[str]]:
        control_pks = {r.record.data[primary_key[0]] for r in control_records}
        target_pks = {r.record.data[primary_key[0]] for r in target_records}

        # Compare the diff for all records whose primary key is in
        record_diff_path_prefix = f"{stream}_record_diff"
        record_diff = get_and_write_diff(
            request,
            _get_filtered_sorted_records(control_records, target_pks, True, primary_key),
            _get_filtered_sorted_records(target_records, control_pks, True, primary_key),
            record_diff_path_prefix,
            ignore_order=False,
            exclude_paths=EXCLUDE_PATHS,
        )

        control_records_diff_path_prefix = f"{stream}_control_records_diff"
        control_records_diff = get_and_write_diff(
            request,
            _get_filtered_sorted_records(control_records, target_pks, False, primary_key),
            [],
            control_records_diff_path_prefix,
            ignore_order=False,
            exclude_paths=EXCLUDE_PATHS,
        )

        target_records_diff_path_prefix = f"{stream}_target_records_diff"
        target_records_diff = get_and_write_diff(
            request,
            [],
            _get_filtered_sorted_records(target_records, control_pks, False, primary_key),
            target_records_diff_path_prefix,
            ignore_order=False,
            exclude_paths=EXCLUDE_PATHS,
        )

        has_diff = record_diff or control_records_diff or target_records_diff

        if has_diff:
            record_property(
                f"{stream} stream: records with primary key in target & control whose values differ",
                record_diff,
            )
            record_property(
                f"{stream} stream: records in control but not target",
                control_records_diff,
            )
            record_property(
                f"{stream} stream: records in target but not control",
                target_records_diff,
            )

            return (record_diff, control_records_diff, target_records_diff)
        return None

    def _get_diff_on_stream_without_pk(
        self,
        request: SubRequest,
        record_property: Callable,
        stream: str,
        control_records: list[AirbyteMessage],
        target_records: list[AirbyteMessage],
    ) -> Optional[Iterable[str]]:
        diff = get_and_write_diff(
            request,
            [json.loads(r.record.json(sort_keys=True)) for r in control_records],
            [json.loads(r.record.json(sort_keys=True)) for r in target_records],
            f"{stream}_diff",
            ignore_order=True,
            exclude_paths=EXCLUDE_PATHS,
        )
        if diff:
            record_property(f"Diff for stream {stream}", diff)
            return (diff,)
        return None


def _get_filtered_sorted_records(
    records: list[AirbyteMessage],
    primary_key_set: set[Generator[Any, Any, None]],
    include_target: bool,
    primary_key: list[str],
) -> list[dict]:
    """
    Get a list of records sorted by primary key, and filtered as specified.

    For example, if `include_target` is true, we filter the records such that
    only those whose primary key is in `primary_key_set` are returned.
    If `include_target` is false, we only return records whose primary key
    is not in `primary_key_set`.
    """
    if include_target:
        _filter = lambda x: x["data"].get(primary_key[0]) in primary_key_set
    else:
        _filter = lambda x: x["data"].get(primary_key[0]) not in primary_key_set

    return sorted(
        filter(
            _filter,
            [json.loads(s.record.json(sort_keys=True)) for s in records],
        ),
        key=lambda x: x["data"][primary_key[0]],
    )
