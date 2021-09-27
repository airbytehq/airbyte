#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Tuple

import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog, Type
from source_acceptance_test import BaseTest
from source_acceptance_test.utils import ConnectorRunner, JsonSchemaHelper, filter_output, incremental_only_catalog


@pytest.fixture(name="future_state_path")
def future_state_path_fixture(inputs, base_path) -> Path:
    """Fixture with connector's future state path (relative to base_path)"""
    if getattr(inputs, "future_state_path"):
        return Path(base_path) / getattr(inputs, "future_state_path")
    pytest.skip("`future_state_path` not specified, skipping")


@pytest.fixture(name="future_state")
def future_state_fixture(future_state_path) -> Path:
    """"""
    with open(str(future_state_path), "r") as file:
        contents = file.read()
    return json.loads(contents)


@pytest.fixture(name="cursor_paths")
def cursor_paths_fixture(inputs, configured_catalog_for_incremental) -> Mapping[str, Any]:
    cursor_paths = getattr(inputs, "cursor_paths") or {}
    result = {}

    for stream in configured_catalog_for_incremental.streams:
        path = cursor_paths.get(stream.stream.name, [stream.cursor_field[-1]])
        result[stream.stream.name] = path

    return result


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


def records_with_state(records, state, stream_mapping, state_cursor_paths) -> Iterable[Tuple[Any, Any]]:
    """Iterate over records and return cursor value with corresponding cursor value from state"""
    for record in records:
        stream_name = record.record.stream
        stream = stream_mapping[stream_name]
        helper = JsonSchemaHelper(schema=stream.stream.json_schema)
        cursor_field = helper.field(stream.cursor_field)
        record_value = cursor_field.parse(record=record.record.data)
        try:
            # first attempt to parse the state value assuming the state object is namespaced on stream names
            state_value = cursor_field.parse(record=state[stream_name], path=state_cursor_paths[stream_name])
        except KeyError:
            # try second time as an absolute path in state file (i.e. bookmarks -> stream_name -> column -> value)
            state_value = cursor_field.parse(record=state, path=state_cursor_paths[stream_name])
        yield record_value, state_value


@pytest.mark.default_timeout(20 * 60)
class TestIncremental(BaseTest):
    def test_two_sequential_reads(self, connector_config, configured_catalog_for_incremental, cursor_paths, docker_runner: ConnectorRunner):
        stream_mapping = {stream.stream.name: stream for stream in configured_catalog_for_incremental.streams}

        output = docker_runner.call_read(connector_config, configured_catalog_for_incremental)
        records_1 = filter_output(output, type_=Type.RECORD)
        states_1 = filter_output(output, type_=Type.STATE)

        assert states_1, "Should produce at least one state"
        assert records_1, "Should produce at least one record"

        latest_state = states_1[-1].state.data
        for record_value, state_value in records_with_state(records_1, latest_state, stream_mapping, cursor_paths):
            assert (
                record_value <= state_value
            ), "First incremental sync should produce records younger or equal to cursor value from the state"

        output = docker_runner.call_read_with_state(connector_config, configured_catalog_for_incremental, state=latest_state)
        records_2 = filter_output(output, type_=Type.RECORD)

        for record_value, state_value in records_with_state(records_2, latest_state, stream_mapping, cursor_paths):
            assert (
                record_value >= state_value
            ), "Second incremental sync should produce records older or equal to cursor value from the state"

    def test_state_with_abnormally_large_values(self, connector_config, configured_catalog, future_state, docker_runner: ConnectorRunner):
        configured_catalog = incremental_only_catalog(configured_catalog)
        output = docker_runner.call_read_with_state(config=connector_config, catalog=configured_catalog, state=future_state)
        records = filter_output(output, type_=Type.RECORD)
        states = filter_output(output, type_=Type.STATE)

        assert not records, "The sync should produce no records when run with the state with abnormally large values"
        assert states, "The sync should produce at least one STATE message"
