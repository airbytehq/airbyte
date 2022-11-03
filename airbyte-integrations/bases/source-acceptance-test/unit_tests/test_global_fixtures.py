#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
from airbyte_cdk.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode
from source_acceptance_test import conftest
from source_acceptance_test.config import BasicReadTestConfig, Config, EmptyStreamConfiguration, ExpectedRecordsConfig


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
            ExpectedRecordsConfig(path="expected_records.json"),
            False,
            id="High strictness level: test_stream_b and test_stream_c are declared as empty streams, expected records only contains test_stream_a record -> Not failing",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            TEST_CONFIGURED_CATALOG,
            set(),
            [{"stream": "test_stream_a", "data": {"k": "foo"}, "emitted_at": 1634387507000}],
            ExpectedRecordsConfig(path="expected_records.json"),
            True,
            id="High strictness level: test_stream_b and test_stream_c are not declared as empty streams, expected records only contains test_stream_a record -> Failing",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            TEST_CONFIGURED_CATALOG,
            {EmptyStreamConfiguration(name="test_stream_b")},
            [{"stream": "test_stream_a", "data": {"k": "foo"}, "emitted_at": 1634387507000}],
            ExpectedRecordsConfig(path="expected_records.json"),
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
            ExpectedRecordsConfig(path="expected_records.json"),
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
    with open(f"{base_path}/expected_records.json", "w") as expected_records_file:
        for record in expected_records:
            expected_records_file.write(json.dumps(record) + "\n")

    conftest.expected_records_by_stream_fixture.__wrapped__(
        test_strictness_level, configured_catalog, empty_streams, expected_records_config, base_path
    )
    if should_fail:
        conftest.pytest.fail.assert_called_once()
    else:
        conftest.pytest.fail.assert_not_called()


@pytest.mark.parametrize(
    "test_strictness_level, configured_catalog_path",
    [
        (Config.TestStrictnessLevel.high, None),
        (Config.TestStrictnessLevel.high, "custom_configured_catalog_path"),
        (Config.TestStrictnessLevel.low, None),
        (Config.TestStrictnessLevel.low, "custom_configured_catalog_path"),
    ],
)
def test_configured_catalog_fixture(mocker, test_strictness_level, configured_catalog_path):
    mocker.patch.object(conftest, "build_configured_catalog_from_discovered_catalog_and_empty_streams")
    mocker.patch.object(conftest, "build_configured_catalog_from_custom_catalog")
    mock_discovered_catalog = mocker.Mock()
    mock_empty_streams = mocker.Mock()
    configured_catalog = conftest.configured_catalog_fixture.__wrapped__(
        test_strictness_level, configured_catalog_path, mock_discovered_catalog, mock_empty_streams
    )
    if test_strictness_level is Config.TestStrictnessLevel.high:
        conftest.build_configured_catalog_from_discovered_catalog_and_empty_streams.assert_called_once_with(
            mock_discovered_catalog, mock_empty_streams
        )
        conftest.build_configured_catalog_from_custom_catalog.assert_not_called()
        assert configured_catalog == conftest.build_configured_catalog_from_discovered_catalog_and_empty_streams.return_value
    else:
        if configured_catalog_path is None:
            conftest.build_configured_catalog_from_discovered_catalog_and_empty_streams.assert_called_once_with(
                mock_discovered_catalog, mock_empty_streams
            )
            conftest.build_configured_catalog_from_custom_catalog.assert_not_called()
            assert configured_catalog == conftest.build_configured_catalog_from_discovered_catalog_and_empty_streams.return_value
        else:
            conftest.build_configured_catalog_from_custom_catalog.assert_called_once_with(configured_catalog_path, mock_discovered_catalog)
            conftest.build_configured_catalog_from_discovered_catalog_and_empty_streams.assert_not_called()
            assert configured_catalog == conftest.build_configured_catalog_from_custom_catalog.return_value


DUMMY_DISCOVERED_CATALOG = {
    "stream_a": AirbyteStream(
        name="stream_a",
        json_schema={"a": {"type": "string"}},
        supported_sync_modes=[SyncMode.full_refresh],
    ),
    "stream_b": AirbyteStream(
        name="stream_b",
        json_schema={"a": {"type": "string"}},
        supported_sync_modes=[SyncMode.full_refresh],
    ),
}

DUMMY_CUSTOM_CATALOG = {
    "stream_a": AirbyteStream(
        name="stream_a",
        json_schema={"a": {"type": "number"}},
        supported_sync_modes=[SyncMode.full_refresh],
    ),
    "stream_b": AirbyteStream(
        name="stream_b",
        json_schema={"a": {"type": "number"}},
        supported_sync_modes=[SyncMode.full_refresh],
    ),
}

DUMMY_CUSTOM_CATALOG_WITH_EXTRA_STREAM = {
    "stream_a": AirbyteStream(
        name="stream_a",
        json_schema={"a": {"type": "number"}},
        supported_sync_modes=[SyncMode.full_refresh],
    ),
    "stream_b": AirbyteStream(
        name="stream_b",
        json_schema={"a": {"type": "number"}},
        supported_sync_modes=[SyncMode.full_refresh],
    ),
    "stream_c": AirbyteStream(
        name="stream_c",
        json_schema={"a": {"type": "number"}},
        supported_sync_modes=[SyncMode.full_refresh],
    ),
}


@pytest.mark.parametrize(
    "discovered_catalog, empty_streams",
    [
        (DUMMY_DISCOVERED_CATALOG, set()),
        (DUMMY_DISCOVERED_CATALOG, {EmptyStreamConfiguration(name="stream_b", bypass_reason="foobar")}),
    ],
)
def test_build_configured_catalog_from_discovered_catalog_and_empty_streams(mocker, discovered_catalog, empty_streams):
    mocker.patch.object(conftest, "logging")
    configured_catalog = conftest.build_configured_catalog_from_discovered_catalog_and_empty_streams(discovered_catalog, empty_streams)
    assert len(configured_catalog.streams) == len(DUMMY_DISCOVERED_CATALOG.values()) - len(empty_streams)
    if empty_streams:
        conftest.logging.warning.assert_called_once()
        configured_stream_names = [configured_stream.stream.name for configured_stream in configured_catalog.streams]
        for empty_stream in empty_streams:
            assert empty_stream.name not in configured_stream_names
    else:
        conftest.logging.info.assert_called_once()


@pytest.mark.parametrize(
    "custom_configured_catalog, expect_failure", [(DUMMY_CUSTOM_CATALOG, False), (DUMMY_CUSTOM_CATALOG_WITH_EXTRA_STREAM, True)]
)
def test_build_configured_catalog_from_custom_catalog(mocker, custom_configured_catalog, expect_failure):
    mocker.patch.object(conftest, "logging")
    mocker.patch.object(conftest.pytest, "fail")

    dummy_configured_catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(stream=stream, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.append)
            for stream in custom_configured_catalog.values()
        ]
    )
    mocker.patch.object(conftest.ConfiguredAirbyteCatalog, "parse_file", mocker.Mock(return_value=dummy_configured_catalog))

    configured_catalog = conftest.build_configured_catalog_from_custom_catalog("path", DUMMY_DISCOVERED_CATALOG)

    if not expect_failure:
        assert len(configured_catalog.streams) == len(dummy_configured_catalog.streams)
        # Checking that the function under test retrieves the stream from the discovered catalog
        assert configured_catalog.streams[0].stream == DUMMY_DISCOVERED_CATALOG["stream_a"]
        assert configured_catalog.streams[0].stream != custom_configured_catalog["stream_a"]
        conftest.logging.info.assert_called_once()
    else:
        conftest.pytest.fail.assert_called_once()
