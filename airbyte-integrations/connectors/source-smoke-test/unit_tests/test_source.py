# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
import subprocess
import sys

from source_smoke_test._scenarios import PREDEFINED_SCENARIOS
from source_smoke_test.source import SourceSmokeTest

from airbyte_cdk.models import (
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)


def test_does_not_import_pyairbyte() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import source_smoke_test.run, sys; "
                "modules = [name for name in sys.modules "
                "if name == 'airbyte' or name.startswith('airbyte.')]; "
                "assert not modules, f'PyAirbyte modules imported: {modules}'"
            ),
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_spec() -> None:
    logger = logging.getLogger("airbyte")

    properties = SourceSmokeTest().spec(logger).connectionSpecification["properties"]

    assert {
        "all_fast_streams",
        "all_slow_streams",
        "scenario_filter",
        "custom_scenarios",
    } <= properties.keys()


def test_check_succeeds_with_empty_config() -> None:
    logger = logging.getLogger("airbyte")

    assert SourceSmokeTest().check(logger, {}).status == Status.SUCCEEDED


def test_discover_default_streams() -> None:
    logger = logging.getLogger("airbyte")
    expected = {scenario["name"] for scenario in PREDEFINED_SCENARIOS if not scenario.get("high_volume", False)}

    actual = {stream.name for stream in SourceSmokeTest().discover(logger, {}).streams}

    assert actual == expected


def test_read_emits_records_for_selected_streams() -> None:
    logger = logging.getLogger("airbyte")
    source = SourceSmokeTest()
    selected_streams = source.discover(logger, {}).streams[:2]
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=stream,
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
            for stream in selected_streams
        ]
    )

    messages = list(source.read(logger, {}, catalog))
    records = [message for message in messages if message.type == Type.RECORD]
    selected_names = {stream.name for stream in selected_streams}

    assert {message.record.stream for message in records} == selected_names


def test_custom_scenario_is_discovered_and_read() -> None:
    logger = logging.getLogger("airbyte")
    source = SourceSmokeTest()
    scenario_name = "custom_smoke_test"
    config = {
        "custom_scenarios": [
            {
                "name": scenario_name,
                "json_schema": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}},
                },
                "records": [{"id": 1}],
            }
        ]
    }
    discovered_streams = source.discover(logger, config).streams
    custom_stream = next(stream for stream in discovered_streams if stream.name == scenario_name)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=custom_stream,
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )

    messages = list(source.read(logger, config, catalog))
    records = [message for message in messages if message.type == Type.RECORD]

    assert [message.record.data for message in records] == [{"id": 1}]
    assert {message.record.stream for message in records} == {scenario_name}
