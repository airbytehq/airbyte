#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import re
from logging import Logger
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, MutableMapping, Optional, Tuple, Union
from uuid import uuid4

import dagger
import pytest
from airbyte_protocol.models import (
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStateStats,
    AirbyteStateType,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    SyncMode,
    Type,
)
from connector_acceptance_test import BaseTest
from connector_acceptance_test.config import ClientContainerConfig, Config, EmptyStreamConfiguration, IncrementalConfig
from connector_acceptance_test.utils import ConnectorRunner, SecretDict, filter_output, incremental_only_catalog
from connector_acceptance_test.utils.timeouts import TWENTY_MINUTES
from deepdiff import DeepDiff

MIN_BATCHES_TO_TEST: int = 5

SCHEMA_TYPES_MAPPING = {
    "str": str,
    "string": str,
    "int": int,
    "integer": int,
    "int32": int,
    "int64": int,
    "float": float,
    "double": float,
    "number": float,
}


@pytest.fixture(name="future_state_configuration")
def future_state_configuration_fixture(inputs, base_path, test_strictness_level) -> Tuple[Path, List[EmptyStreamConfiguration]]:
    """Fixture with connector's future state path (relative to base_path)"""
    if inputs.future_state and inputs.future_state.bypass_reason is not None:
        pytest.skip("`future_state` has a bypass reason, skipping.")
    elif inputs.future_state and inputs.future_state.future_state_path:
        return Path(base_path) / inputs.future_state.future_state_path, inputs.future_state.missing_streams
    elif test_strictness_level is Config.TestStrictnessLevel.high:
        pytest.fail(
            "High test strictness level error: a future state configuration must be provided in high test strictness level or a bypass reason should be filled."
        )
    else:
        pytest.skip("`future_state` not specified, skipping.")


@pytest.fixture(name="future_state")
def future_state_fixture(future_state_configuration, test_strictness_level, configured_catalog) -> List[MutableMapping]:
    """"""
    future_state_path, missing_streams = future_state_configuration
    with open(str(future_state_path), "r") as file:
        contents = file.read()
    states = json.loads(contents)
    if test_strictness_level is Config.TestStrictnessLevel.high:
        if not all([missing_stream.bypass_reason is not None for missing_stream in missing_streams]):
            pytest.fail("High test strictness level error: all missing_streams must have a bypass reason specified.")
        all_stream_names = {
            stream.stream.name for stream in configured_catalog.streams if SyncMode.incremental in stream.stream.supported_sync_modes
        }
        streams_in_states = set([state["stream"]["stream_descriptor"]["name"] for state in states])
        declared_missing_streams_names = set([missing_stream.name for missing_stream in missing_streams])
        undeclared_missing_streams_names = all_stream_names - declared_missing_streams_names - streams_in_states
        if undeclared_missing_streams_names:
            pytest.fail(
                f"High test strictness level error: {', '.join(undeclared_missing_streams_names)} streams are missing in your future_state file, please declare a state for those streams or fill-in a valid bypass_reason."
            )
    return states


@pytest.fixture(name="configured_catalog_for_incremental")
def configured_catalog_for_incremental_fixture(configured_catalog) -> ConfiguredAirbyteCatalog:
    catalog = incremental_only_catalog(configured_catalog)
    for stream in catalog.streams:
        if not stream.cursor_field:
            if stream.stream.default_cursor_field:
                stream.cursor_field = stream.stream.default_cursor_field[:]
            else:
                pytest.fail(
                    f"All incremental streams should either have `cursor_field` \
                    declared in the configured_catalog or `default_cursor_field` \
                    specified in the catalog output by discover. \
                    Stream {stream.stream.name} does not have either property defined."
                )

    return catalog


def is_per_stream_state(message: AirbyteMessage) -> bool:
    return message.state and isinstance(message.state, AirbyteStateMessage) and message.state.type == AirbyteStateType.STREAM


def is_global_state(message: AirbyteMessage) -> bool:
    return message.state and isinstance(message.state, AirbyteStateMessage) and message.state.type == AirbyteStateType.GLOBAL


def construct_latest_state_from_messages(messages: List[AirbyteMessage]) -> Dict[str, Mapping[str, Any]]:
    """
    Because connectors that have migrated to per-stream state only emit state messages with the new state value for a single
    stream, this helper method reconstructs the final state of all streams after going through each AirbyteMessage
    """
    latest_per_stream_by_name = dict()
    for message in messages:
        current_state = message.state
        if current_state and current_state.type == AirbyteStateType.STREAM:
            per_stream = current_state.stream
            latest_per_stream_by_name[per_stream.stream_descriptor.name] = per_stream.stream_state.dict() if per_stream.stream_state else {}
    return latest_per_stream_by_name


def naive_diff_records(records_1: List[AirbyteMessage], records_2: List[AirbyteMessage]) -> DeepDiff:
    """
    Naively diff two lists of records by comparing their data field.
    """
    records_1_data = [record.record.data for record in records_1]
    records_2_data = [record.record.data for record in records_2]

    # ignore_order=True because the order of records in the list is not guaranteed
    diff = DeepDiff(records_1_data, records_2_data, ignore_order=True)
    return diff


@pytest.mark.default_timeout(TWENTY_MINUTES)
@pytest.mark.usefixtures("final_teardown")
class TestIncremental(BaseTest):
    async def test_two_sequential_reads(
        self,
        connector_config: SecretDict,
        configured_catalog_for_incremental: ConfiguredAirbyteCatalog,
        docker_runner: ConnectorRunner,
        client_container: Optional[dagger.Container],
        client_container_config: Optional[ClientContainerConfig],
        detailed_logger: Logger,
    ):
        """
        This test makes two calls to the read method and verifies that the records returned are different.

        Important!

        Assert only that the reads are different. Nothing else.
        This is because there is only a small subset of assertions we can make
        in the absense of enforcing that all connectors return 3 or more state messages
        during the first read.

        To learn more: https://github.com/airbytehq/airbyte/issues/29926
        """
        output_1 = await docker_runner.call_read(connector_config, configured_catalog_for_incremental)
        records_1 = filter_output(output_1, type_=Type.RECORD)
        states_1 = filter_output(output_1, type_=Type.STATE)

        assert states_1, "First Read should produce at least one state"
        assert records_1, "First Read should produce at least one record"

        # For legacy state format, the final state message contains the final state of all streams. For per-stream state format,
        # the complete final state of streams must be assembled by going through all prior state messages received
        if is_per_stream_state(states_1[-1]):
            latest_state = construct_latest_state_from_messages(states_1)
            state_input = []
            for stream_name, stream_state in latest_state.items():
                stream_descriptor = {"name": stream_name}
                if "stream_namespace" in stream_state:
                    stream_descriptor["namespace"] = stream_state["stream_namespace"]
                state_input.append(
                    {
                        "type": "STREAM",
                        "stream": {"stream_descriptor": stream_descriptor, "stream_state": stream_state},
                    }
                )
        elif is_global_state(states_1[-1]):
            # TODO: DB sources to fill out this case
            state_input = states_1[-1].state.data
        else:
            state_input = states_1[-1].state.data

        # READ #2
        if client_container and client_container_config.between_syncs_command:
            detailed_logger.info(
                await client_container.with_env_variable("CACHEBUSTER", str(uuid4()))
                .with_exec(client_container_config.between_syncs_command)
                .stdout()
            )

        output_2 = await docker_runner.call_read_with_state(connector_config, configured_catalog_for_incremental, state=state_input)
        records_2 = filter_output(output_2, type_=Type.RECORD)

        diff = naive_diff_records(records_1, records_2)
        assert (
            diff
        ), f"Records should change between reads but did not.\n\n records_1: {records_1} \n\n state: {state_input} \n\n records_2: {records_2} \n\n diff: {diff}"

    async def test_read_sequential_slices(
        self,
        inputs: IncrementalConfig,
        connector_config,
        configured_catalog_for_incremental,
        docker_runner: ConnectorRunner,
        client_container: Optional[dagger.Container],
        client_container_config: Optional[ClientContainerConfig],
        detailed_logger: Logger,
    ):
        """
        Incremental test that makes calls to the read method without a state checkpoint. Then we partition the results by stream and
        slice checkpoints.
        Then we make additional read method calls using the state message and verify the correctness of the
        messages in the response.
        """
        if inputs.skip_comprehensive_incremental_tests:
            pytest.skip("Skipping new incremental test based on acceptance-test-config.yml")
            return

        for stream in configured_catalog_for_incremental.streams:
            configured_catalog_for_incremental_per_stream = ConfiguredAirbyteCatalog(streams=[stream])

            output_1 = await docker_runner.call_read(connector_config, configured_catalog_for_incremental_per_stream)

            records_1 = filter_output(output_1, type_=Type.RECORD)
            # If the output of a full read is empty, there is no reason to iterate over its state.
            # So, reading from any checkpoint of an empty stream will also produce nothing.
            if len(records_1) == 0:
                continue

            states_1 = filter_output(output_1, type_=Type.STATE)

            # To learn more: https://github.com/airbytehq/airbyte/issues/29926
            if len(states_1) == 0:
                continue

            states_with_expected_record_count = self._state_messages_selector(states_1)
            if not states_with_expected_record_count:
                pytest.fail(
                    "Unable to test because there is no suitable state checkpoint, likely due to a zero record count in the states."
                )

            mutating_stream_name_to_per_stream_state = dict()

            for idx, state_message_data in enumerate(states_with_expected_record_count):
                state_message, expected_records_count = state_message_data
                assert state_message.type == Type.STATE

                state_input, mutating_stream_name_to_per_stream_state = self.get_next_state_input(
                    state_message, mutating_stream_name_to_per_stream_state
                )

                output_N = await docker_runner.call_read_with_state(
                    connector_config, configured_catalog_for_incremental_per_stream, state=state_input
                )
                records_N = filter_output(output_N, type_=Type.RECORD)

                assert (
                    # We assume that the output may be empty when we read the latest state, or it must produce some data if we are in the middle of our progression
                    len(records_N)
                    >= expected_records_count
                ), f"Read {idx + 1} of {len(states_with_expected_record_count)} should produce at least one record.\n\n state: {state_input} \n\n records_{idx + 1}: {records_N}"

                # Temporary comment this to avoid fake failures while handling corner cases such as:
                # - start date is equal to the latest state checkpoint date and date compare condition is >=, so we have two equal sets of data
                # - ...

                # See this issue for more details: https://github.com/airbytehq/airbyte-internal-issues/issues/8056

                # diff = naive_diff_records(records_1, records_N)
                # assert (
                #     diff
                # ), f"Records for subsequent reads with new state should be different.\n\n records_1: {records_1} \n\n state: {state_input} \n\n records_{idx + 1}: {records_N} \n\n diff: {diff}"

    async def test_state_with_abnormally_large_values(
        self, inputs: IncrementalConfig, connector_config, configured_catalog, future_state, docker_runner: ConnectorRunner
    ):
        configured_catalog = incremental_only_catalog(configured_catalog)
        output = await docker_runner.call_read_with_state(config=connector_config, catalog=configured_catalog, state=future_state)
        records = filter_output(output, type_=Type.RECORD)
        states = filter_output(output, type_=Type.STATE)

        assert (
            not records
        ), f"The sync should produce no records when run with the state with abnormally large values {records[0].record.stream}"
        assert states, "The sync should produce at least one STATE message"

        if states and is_global_state(states[0]):
            # TODO: DB sources to fill out this case. Also, can we assume all states will be global if the first one is?
            pass

        # TODO: else:
        cursor_fields_per_stream = {
            stream.stream.name: self._get_cursor_field(stream)
            for stream in configured_catalog.streams
            if stream.sync_mode == SyncMode.incremental
        }
        actual_state_cursor_values_per_stream = {
            state.state.stream.stream_descriptor.name: self._get_cursor_values_from_states_by_cursor(
                state.state.stream.stream_state.dict(), cursor_fields_per_stream[state.state.stream.stream_descriptor.name]
            )
            for state in states
        }
        future_state_cursor_values_per_stream = {
            state["stream"]["stream_descriptor"]["name"]: self._get_cursor_values_from_states_by_cursor(
                state["stream"]["stream_state"], cursor_fields_per_stream[state["stream"]["stream_descriptor"]["name"]]
            )
            for state in future_state
            if state["stream"]["stream_descriptor"]["name"] in cursor_fields_per_stream
        }

        assert all(future_state_cursor_values_per_stream.values()), "Future state must be set up for all given streams"

        expected_cursor_value_schema_per_stream = {
            # TODO: Check if cursor value may be a nested property. If so, then should I use ._get_cursor_values_from_states ?
            stream.stream.name: stream.stream.json_schema["properties"][cursor_fields_per_stream[stream.stream.name]]
            for stream in configured_catalog.streams
        }

        future_state_formatrs_per_stream = {stream.name: stream for stream in inputs.future_state.cursor_format.streams}
        for stream in configured_catalog.streams:
            pattern = future_state_formatrs_per_stream.get(stream.stream.name, inputs.future_state.cursor_format).format

            # All streams must be defined in the abnormal_state.json file due to the high test strictness level rule.
            # However, a state may not be present in the output if a stream was unavailable during sync.
            # Ideally, this should not be the case, but in reality, it often happens.
            # It is not the purpose of this test to check for this, so we just skip it here.
            if stream.stream.name not in actual_state_cursor_values_per_stream:
                continue

            actual_cursor_values = actual_state_cursor_values_per_stream[stream.stream.name]
            future_state_cursor_values = future_state_cursor_values_per_stream[stream.stream.name]

            expected_types = self._get_cursor_value_types(expected_cursor_value_schema_per_stream[stream.stream.name]["type"])

            for actual_cursor_value, future_state_cursor_value in zip(actual_cursor_values, future_state_cursor_values):

                for _type in expected_types:

                    if actual_cursor_value:
                        assert isinstance(
                            actual_cursor_value, _type
                        ), f"Cursor value {actual_cursor_value} is not of type {_type}. Expected {_type}, got {type(actual_cursor_value)}"

                    if future_state_cursor_value:
                        assert isinstance(
                            future_state_cursor_value, _type
                        ), f"Cursor value {future_state_cursor_value} is not of type {_type}. Expected {_type}, got {type(future_state_cursor_value)}"

                if not (actual_cursor_value and future_state_cursor_value):
                    continue

                # If the cursor value is numeric and the type check has passed, it means the format is correct
                if isinstance(actual_cursor_value, (int, float)):
                    continue

                # When the data is of string type, we need to ensure the format is correct for both cursor values
                if pattern:
                    assert self._check_cursor_by_regex_match(
                        actual_cursor_value, pattern
                    ), f"Actual cursor value {actual_cursor_value} does not match pattern: {pattern}"
                    assert self._check_cursor_by_regex_match(
                        future_state_cursor_value, pattern
                    ), f"Future cursor value {future_state_cursor_value} does not match pattern: {pattern}"
                else:
                    assert self._check_cursor_by_char_types(
                        actual_cursor_value, future_state_cursor_value
                    ), f"Actual and future state formats do not match. Actual cursor value: {actual_cursor_value}, future cursor value: {future_state_cursor_value}"

    def get_next_state_input(
        self, state_message: AirbyteStateMessage, stream_name_to_per_stream_state: MutableMapping
    ) -> Tuple[Union[List[MutableMapping], MutableMapping], MutableMapping]:
        # Including all the latest state values from previous batches, update the combined stream state
        # with the current batch's stream state and then use it in the following read() request
        current_state = state_message.state
        if current_state and current_state.type == AirbyteStateType.STREAM:
            per_stream = current_state.stream
            if per_stream.stream_state:
                stream_name_to_per_stream_state[per_stream.stream_descriptor.name] = (
                    per_stream.stream_state.dict() if per_stream.stream_state else {}
                )
        elif current_state and current_state.type == AirbyteStateType.GLOBAL:
            # TODO: DB Sources to fill in this case
            pass
        state_input = [
            {"type": "STREAM", "stream": {"stream_descriptor": {"name": stream_name}, "stream_state": stream_state}}
            for stream_name, stream_state in stream_name_to_per_stream_state.items()
        ]
        return state_input, stream_name_to_per_stream_state

    @staticmethod
    def _get_cursor_values_from_states_by_cursor(states: Union[list, dict], cursor_field: str) -> List[Union[str, int]]:
        values = []
        nodes_to_visit = [states]

        while nodes_to_visit:
            current_node = nodes_to_visit.pop()

            if isinstance(current_node, dict):
                for key, value in current_node.items():
                    # DB sources use a hardcoded field `cursor` to denote cursor value.
                    if key == cursor_field or ("cursor_field" in current_node and key == "cursor"):
                        values.append(value)
                    nodes_to_visit.append(value)
            elif isinstance(current_node, list):
                nodes_to_visit.extend(current_node)

        return values

    @staticmethod
    def _check_cursor_by_char_types(actual_cursor: str, expected_cursor: str) -> bool:
        if len(actual_cursor) != len(expected_cursor):
            return False

        for char1, char2 in zip(actual_cursor, expected_cursor):
            if char1.isalpha() and char2.isalpha():
                continue
            elif char1.isdigit() and char2.isdigit():
                continue
            elif not char1.isalnum() and not char2.isalnum() and char1 == char2:
                continue
            else:
                return False

        return True

    @staticmethod
    def _check_cursor_by_regex_match(cursor: str, pattern: str) -> bool:
        return bool(re.match(pattern, cursor))

    @staticmethod
    def _get_cursor_field(stream: ConfiguredAirbyteStream) -> Optional[str]:
        cursor_field = stream.cursor_field or stream.stream.default_cursor_field
        if cursor_field:
            return next(iter(cursor_field))

    @staticmethod
    def _get_cursor_value_types(schema_type: Union[list, str]) -> List[Callable[..., Any]]:
        if isinstance(schema_type, str):
            schema_type = [schema_type]
        types = []
        for _type in schema_type:
            if _type == "null":
                continue

            if _type not in SCHEMA_TYPES_MAPPING:
                pytest.fail(f"Unsupported type: {_type}. Update SCHEMA_TYPES_MAPPING with the {_type} and its corresponding function")

            types.append(SCHEMA_TYPES_MAPPING[_type])
        return types

    @staticmethod
    def _get_state(airbyte_message: AirbyteMessage) -> AirbyteStateMessage:
        if not airbyte_message.state.stream:
            return airbyte_message.state
        return airbyte_message.state.stream.stream_state

    @staticmethod
    def _get_record_count(airbyte_message: AirbyteMessage) -> float:
        return airbyte_message.state.sourceStats.recordCount

    def _get_unique_state_messages_with_record_count(self, states: List[AirbyteMessage]) -> List[Tuple[AirbyteMessage, float]]:
        """
        Validates a list of state messages to ensure that consecutive messages with the same stream state are represented by only the first message, while subsequent duplicates are ignored.
        """
        if len(states) <= 1:
            return [(state, 0.0) for state in states if self._get_record_count(state)]

        current_idx = 0
        unique_state_messages = []

        # Iterate through the list of state messages
        while current_idx < len(states) - 1:
            next_idx = current_idx + 1
            # Check if consecutive messages have the same stream state
            while self._get_state(states[current_idx]) == self._get_state(states[next_idx]) and next_idx < len(states) - 1:
                next_idx += 1

            states[current_idx].state.sourceStats = AirbyteStateStats(
                recordCount=sum(map(self._get_record_count, states[current_idx:next_idx]))
            )
            # Append the first message with a unique stream state to the result list
            unique_state_messages.append(states[current_idx])
            # If the last message has a different stream state than the previous one, append it to the result list
            if next_idx == len(states) - 1 and self._get_state(states[current_idx]) != self._get_state(states[next_idx]):
                unique_state_messages.append(states[next_idx])
            current_idx = next_idx

        # Drop all states with a record count of 0.0
        unique_non_zero_state_messages = list(filter(self._get_record_count, unique_state_messages))

        total_record_count = sum(map(self._get_record_count, unique_non_zero_state_messages))

        # Calculates the expected record count per state based on the total record count and distribution across states.
        # The expected record count is the number of records we expect to receive when applying a specific state checkpoint.
        unique_non_zero_state_messages_with_record_count = zip(
            unique_non_zero_state_messages,
            [
                total_record_count - sum(map(self._get_record_count, unique_non_zero_state_messages[: idx + 1]))
                for idx in range(len(unique_non_zero_state_messages))
            ],
        )

        return list(unique_non_zero_state_messages_with_record_count)

    def _states_with_expected_record_count_batch_selector(
        self, unique_state_messages_with_record_count: List[Tuple[AirbyteMessage, float]]
    ) -> List[Tuple[AirbyteMessage, float]]:
        # Important!

        # There is only a small subset of assertions we can make
        # in the absense of enforcing that all connectors return 3 or more state messages
        # during the first read.
        if len(unique_state_messages_with_record_count) < 3:
            return unique_state_messages_with_record_count[-1:]

        # To avoid spamming APIs we only test a fraction of batches (4 or 5 states by default)
        sample_rate = (len(unique_state_messages_with_record_count) // MIN_BATCHES_TO_TEST) or 1

        states_with_expected_record_count_batch = []

        for idx, state_message_data in enumerate(unique_state_messages_with_record_count):
            # if first state message, skip
            # this is because we cannot assert if the first state message will result in new records
            # as in this case it is possible for a connector to return an empty state message when it first starts.
            # e.g. if the connector decides it wants to let the caller know that it has started with an empty state.
            if idx == 0:
                continue

            # if batching required, and not a sample, skip
            if idx % sample_rate != 0:
                continue

            # if last state message, skip
            # this is because we cannot assert if the last state message will result in new records
            # as in this case it is possible for a connector to return a previous state message.
            # e.g. if the connector is using pagination and the last page is only partially full
            if idx == len(unique_state_messages_with_record_count) - 1:
                continue

            states_with_expected_record_count_batch.append(state_message_data)

        return states_with_expected_record_count_batch

    def _state_messages_selector(self, state_messages: List[AirbyteMessage]) -> List[Tuple[AirbyteMessage, float]]:
        unique_state_messages_with_record_count = self._get_unique_state_messages_with_record_count(state_messages)
        return self._states_with_expected_record_count_batch_selector(unique_state_messages_with_record_count)
