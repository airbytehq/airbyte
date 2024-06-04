#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union

import pytest
from airbyte_protocol.models import (
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStateStats,
    AirbyteStateType,
    ConfiguredAirbyteCatalog,
    SyncMode,
    Type,
)
from connector_acceptance_test import BaseTest
from connector_acceptance_test.config import Config, EmptyStreamConfiguration, IncrementalConfig
from connector_acceptance_test.utils import ConnectorRunner, SecretDict, filter_output, incremental_only_catalog
from connector_acceptance_test.utils.timeouts import TWENTY_MINUTES
from deepdiff import DeepDiff

MIN_BATCHES_TO_TEST: int = 5


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
class TestIncremental(BaseTest):
    async def test_two_sequential_reads(
        self,
        connector_config: SecretDict,
        configured_catalog_for_incremental: ConfiguredAirbyteCatalog,
        docker_runner: ConnectorRunner,
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
        is_per_stream = is_per_stream_state(states_1[-1])
        if is_per_stream:
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
        else:
            state_input = states_1[-1].state.data

        # READ #2

        output_2 = await docker_runner.call_read_with_state(connector_config, configured_catalog_for_incremental, state=state_input)
        records_2 = filter_output(output_2, type_=Type.RECORD)

        diff = naive_diff_records(records_1, records_2)
        assert (
            diff
        ), f"Records should change between reads but did not.\n\n records_1: {records_1} \n\n state: {state_input} \n\n records_2: {records_2} \n\n diff: {diff}"

    async def test_read_sequential_slices(
        self, inputs: IncrementalConfig, connector_config, configured_catalog_for_incremental, docker_runner: ConnectorRunner
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

                diff = naive_diff_records(records_1, records_N)
                assert (
                    diff
                ), f"Records for subsequent reads with new state should be different.\n\n records_1: {records_1} \n\n state: {state_input} \n\n records_{idx + 1}: {records_N} \n\n diff: {diff}"

    async def test_state_with_abnormally_large_values(
        self, connector_config, configured_catalog, future_state, docker_runner: ConnectorRunner
    ):
        configured_catalog = incremental_only_catalog(configured_catalog)
        output = await docker_runner.call_read_with_state(config=connector_config, catalog=configured_catalog, state=future_state)
        records = filter_output(output, type_=Type.RECORD)
        states = filter_output(output, type_=Type.STATE)

        assert (
            not records
        ), f"The sync should produce no records when run with the state with abnormally large values {records[0].record.stream}"
        assert states, "The sync should produce at least one STATE message"

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
        state_input = [
            {"type": "STREAM", "stream": {"stream_descriptor": {"name": stream_name}, "stream_state": stream_state}}
            for stream_name, stream_state in stream_name_to_per_stream_state.items()
        ]
        return state_input, stream_name_to_per_stream_state

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
