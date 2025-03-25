#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import time

import pytest
from connector_acceptance_test import conftest
from connector_acceptance_test.config import (
    BasicReadTestConfig,
    Config,
    EmptyStreamConfiguration,
    ExpectedRecordsConfig,
    IgnoredFieldsConfiguration,
)

from airbyte_protocol.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode


@pytest.mark.parametrize(
    "test_strictness_level, basic_read_test_config, expect_test_failure",
    [
        pytest.param(
            Config.TestStrictnessLevel.low,
            BasicReadTestConfig(config_path="config_path", empty_streams={EmptyStreamConfiguration(name="my_empty_stream")}),
            False,
            id="[LOW test strictness level] Empty streams can be declared without bypass_reason.",
        ),
        pytest.param(
            Config.TestStrictnessLevel.low,
            BasicReadTestConfig(
                config_path="config_path", empty_streams={EmptyStreamConfiguration(name="my_empty_stream", bypass_reason="good reason")}
            ),
            False,
            id="[LOW test strictness level] Empty streams can be declared with a bypass_reason.",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            BasicReadTestConfig(config_path="config_path", empty_streams={EmptyStreamConfiguration(name="my_empty_stream")}),
            True,
            id="[HIGH test strictness level] Empty streams can't be declared without bypass_reason.",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            BasicReadTestConfig(
                config_path="config_path", empty_streams={EmptyStreamConfiguration(name="my_empty_stream", bypass_reason="good reason")}
            ),
            False,
            id="[HIGH test strictness level] Empty streams can be declared with a bypass_reason.",
        ),
    ],
)
def test_empty_streams_fixture(mocker, test_strictness_level, basic_read_test_config, expect_test_failure):
    mocker.patch.object(conftest.pytest, "fail")
    # Pytest prevents fixture to be directly called. Using __wrapped__ allows us to call the actual function before it's been wrapped by the decorator.
    assert conftest.empty_streams_fixture.__wrapped__(basic_read_test_config, test_strictness_level) == basic_read_test_config.empty_streams
    if expect_test_failure:
        conftest.pytest.fail.assert_called_once()
    else:
        conftest.pytest.fail.assert_not_called()


TEST_AIRBYTE_STREAM_A = AirbyteStream(name="test_stream_a", json_schema={"k": "v"}, supported_sync_modes=[SyncMode.full_refresh])
TEST_AIRBYTE_STREAM_B = AirbyteStream(name="test_stream_b", json_schema={"k": "v"}, supported_sync_modes=[SyncMode.full_refresh])
TEST_AIRBYTE_STREAM_C = AirbyteStream(name="test_stream_c", json_schema={"k": "v"}, supported_sync_modes=[SyncMode.full_refresh])

TEST_CONFIGURED_AIRBYTE_STREAM_A = ConfiguredAirbyteStream(
    stream=TEST_AIRBYTE_STREAM_A,
    sync_mode=SyncMode.full_refresh,
    destination_sync_mode=DestinationSyncMode.overwrite,
)

TEST_CONFIGURED_AIRBYTE_STREAM_B = ConfiguredAirbyteStream(
    stream=TEST_AIRBYTE_STREAM_B,
    sync_mode=SyncMode.full_refresh,
    destination_sync_mode=DestinationSyncMode.overwrite,
)

TEST_CONFIGURED_AIRBYTE_STREAM_C = ConfiguredAirbyteStream(
    stream=TEST_AIRBYTE_STREAM_C,
    sync_mode=SyncMode.full_refresh,
    destination_sync_mode=DestinationSyncMode.overwrite,
)

TEST_CONFIGURED_CATALOG = ConfiguredAirbyteCatalog(
    streams=[TEST_CONFIGURED_AIRBYTE_STREAM_A, TEST_CONFIGURED_AIRBYTE_STREAM_B, TEST_CONFIGURED_AIRBYTE_STREAM_C]
)


@pytest.mark.parametrize(
    "test_strictness_level, configured_catalog, empty_streams, expected_records, expected_records_config, should_fail",
    [
        pytest.param(
            Config.TestStrictnessLevel.high,
            TEST_CONFIGURED_CATALOG,
            set(),
            [],
            None,
            True,
            id="High strictness level: No expected records configuration ->  Failing",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            TEST_CONFIGURED_CATALOG,
            {EmptyStreamConfiguration(name="test_stream_b"), EmptyStreamConfiguration(name="test_stream_c")},
            [{"stream": "test_stream_a", "data": {"k": "foo"}, "emitted_at": 1634387507000}],
            ExpectedRecordsConfig(path="expected_records.jsonl"),
            False,
            id="High strictness level: test_stream_b and test_stream_c are declared as empty streams, expected records only contains test_stream_a record -> Not failing",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            TEST_CONFIGURED_CATALOG,
            set(),
            [{"stream": "test_stream_a", "data": {"k": "foo"}, "emitted_at": 1634387507000}],
            ExpectedRecordsConfig(path="expected_records.jsonl"),
            True,
            id="High strictness level: test_stream_b and test_stream_c are not declared as empty streams, expected records only contains test_stream_a record -> Failing",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            TEST_CONFIGURED_CATALOG,
            {EmptyStreamConfiguration(name="test_stream_b")},
            [{"stream": "test_stream_a", "data": {"k": "foo"}, "emitted_at": 1634387507000}],
            ExpectedRecordsConfig(path="expected_records.jsonl"),
            True,
            id="High strictness level: test_stream_b is declared as an empty stream, test_stream_c is not declared as empty streams, expected records only contains test_stream_a record -> Failing",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            TEST_CONFIGURED_CATALOG,
            set(),
            [],
            ExpectedRecordsConfig(bypass_reason="A good reason to not have expected records"),
            False,
            id="High strictness level: Expected records configuration with bypass_reason ->  Not failing",
        ),
        pytest.param(
            Config.TestStrictnessLevel.low,
            TEST_CONFIGURED_CATALOG,
            set(),
            [],
            None,
            False,
            id="Low strictness level, no empty stream, no expected records ->  Not failing",
        ),
        pytest.param(
            Config.TestStrictnessLevel.low,
            TEST_CONFIGURED_CATALOG,
            set(),
            [{"stream": "test_stream_a", "data": {"k": "foo"}, "emitted_at": 1634387507000}],
            ExpectedRecordsConfig(path="expected_records.jsonl"),
            False,
            id="Low strictness level, no empty stream, incomplete expected records ->  Not failing",
        ),
    ],
)
def test_expected_records_by_stream_fixture(
    tmp_path, mocker, test_strictness_level, configured_catalog, empty_streams, expected_records, expected_records_config, should_fail
):
    mocker.patch.object(conftest.pytest, "fail")

    base_path = tmp_path
    with open(f"{base_path}/expected_records.jsonl", "w") as expected_records_file:
        for record in expected_records:
            expected_records_file.write(json.dumps(record) + "\n")

    conftest.expected_records_by_stream_fixture.__wrapped__(
        test_strictness_level, configured_catalog, empty_streams, expected_records_config, base_path
    )
    if should_fail:
        conftest.pytest.fail.assert_called_once()
    else:
        conftest.pytest.fail.assert_not_called()


@pytest.mark.parametrize("configured_catalog_path", [None, "my_path"])
def test_configured_catalog_fixture(mocker, configured_catalog_path):
    mock_discovered_catalog = mocker.Mock()
    mocker.patch.object(conftest, "build_configured_catalog_from_custom_catalog")
    mocker.patch.object(conftest, "build_configured_catalog_from_discovered_catalog_and_empty_streams")
    configured_catalog = conftest.configured_catalog_fixture.__wrapped__(configured_catalog_path, mock_discovered_catalog)
    if configured_catalog_path:
        assert configured_catalog == conftest.build_configured_catalog_from_custom_catalog.return_value
        conftest.build_configured_catalog_from_custom_catalog.assert_called_once_with(configured_catalog_path, mock_discovered_catalog)
    else:
        assert configured_catalog == conftest.build_configured_catalog_from_discovered_catalog_and_empty_streams.return_value
        conftest.build_configured_catalog_from_discovered_catalog_and_empty_streams.assert_called_once_with(mock_discovered_catalog, set())


@pytest.mark.parametrize(
    "updated_configurations", [[], ["config|created_last.json"], ["config|created_first.json", "config|created_last.json"]]
)
def test_connector_config_path_fixture(mocker, tmp_path, updated_configurations):
    inputs = mocker.Mock(config_path="config.json")
    base_path = tmp_path
    if updated_configurations:
        updated_configurations_dir = tmp_path / "updated_configurations"
        updated_configurations_dir.mkdir()
        for configuration_file_name in updated_configurations:
            updated_configuration_path = updated_configurations_dir / configuration_file_name
            updated_configuration_path.touch()
            # to avoid the equivalent 'ctime' for created files
            time.sleep(0.01)

    connector_config_path = conftest.connector_config_path_fixture.__wrapped__(inputs, base_path)
    if not updated_configurations:
        assert connector_config_path == base_path / "config.json"
    else:
        assert connector_config_path == base_path / "updated_configurations" / "config|created_last.json"
