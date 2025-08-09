#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from connector_acceptance_test.config import NoPrimaryKeyConfiguration
from connector_acceptance_test.tests import test_core

from airbyte_protocol.models import AirbyteCatalog, AirbyteMessage, AirbyteStream, Type


pytestmark = pytest.mark.anyio


@pytest.mark.parametrize(
    "stream_configs, excluded_streams, expected_error_streams",
    [
        pytest.param([{"name": "stream_with_primary_key", "primary_key": [["id"]]}], [], None, id="test_stream_with_primary_key_succeeds"),
        pytest.param(
            [{"name": "stream_without_primary_key"}], [], ["stream_without_primary_key"], id="test_stream_without_primary_key_fails"
        ),
        pytest.param([{"name": "report_stream"}], ["report_stream"], None, id="test_primary_key_excluded_from_test"),
        pytest.param(
            [
                {"name": "freiren", "primary_key": [["mage"]]},
                {"name": "himmel"},
                {"name": "eisen", "primary_key": [["warrior"]]},
                {"name": "heiter"},
            ],
            [],
            ["himmel", "heiter"],
            id="test_multiple_streams_that_are_missing_primary_key",
        ),
        pytest.param(
            [
                {"name": "freiren", "primary_key": [["mage"]]},
                {"name": "himmel"},
                {"name": "eisen", "primary_key": [["warrior"]]},
                {"name": "heiter"},
            ],
            ["himmel", "heiter"],
            None,
            id="test_multiple_streams_that_exclude_primary_key",
        ),
        pytest.param(
            [
                {"name": "freiren", "primary_key": [["mage"]]},
                {"name": "himmel"},
                {"name": "eisen", "primary_key": [["warrior"]]},
                {"name": "heiter"},
            ],
            ["heiter"],
            ["himmel"],
            id="test_multiple_streams_missing_primary_key_or_excluded",
        ),
    ],
)
async def test_streams_define_primary_key(mocker, stream_configs, excluded_streams, expected_error_streams):
    t = test_core.TestConnectorAttributes()

    streams = [
        AirbyteStream.parse_obj(
            {
                "name": stream_config.get("name"),
                "json_schema": {},
                "default_cursor_field": ["updated_at"],
                "supported_sync_modes": ["full_refresh", "incremental"],
                "source_defined_primary_key": stream_config.get("primary_key"),
            }
        )
        for stream_config in stream_configs
    ]

    streams_without_primary_key = [NoPrimaryKeyConfiguration(name=stream, bypass_reason="") for stream in excluded_streams]

    docker_runner_mock = mocker.MagicMock(
        call_discover=mocker.AsyncMock(return_value=[AirbyteMessage(type=Type.CATALOG, catalog=AirbyteCatalog(streams=streams))])
    )

    if expected_error_streams:
        with pytest.raises(AssertionError) as e:
            await t.test_streams_define_primary_key(
                operational_certification_test=True,
                streams_without_primary_key=streams_without_primary_key,
                connector_config={},
                docker_runner=docker_runner_mock,
            )
        streams_in_error_message = [stream_name for stream_name in expected_error_streams if stream_name in e.value.args[0]]
        assert streams_in_error_message == expected_error_streams
    else:
        await t.test_streams_define_primary_key(
            operational_certification_test=True,
            streams_without_primary_key=streams_without_primary_key,
            connector_config={},
            docker_runner=docker_runner_mock,
        )


@pytest.mark.parametrize(
    "metadata_yaml, should_raise_assert_error, expected_error",
    [
        pytest.param(
            {"data": {"ab_internal": {"ql": 400}}},
            True,
            "The `allowedHosts` property is missing in `metadata.data` for `metadata.yaml`",
        ),
        pytest.param(
            {"data": {"ab_internal": {"ql": 400}, "allowedHosts": {}}},
            True,
            "The `hosts` property is missing in `metadata.data.allowedHosts` for `metadata.yaml`",
        ),
        pytest.param(
            {"data": {"ab_internal": {"ql": 400}, "allowedHosts": {"hosts": []}}},
            True,
            "'The `hosts` empty list is not allowed for `metadata.data.allowedHosts` for certified connectors",
        ),
        pytest.param(
            {"data": {"ab_internal": {"ql": 400}, "allowedHosts": {"hosts": ["*.test.com"]}}},
            False,
            None,
        ),
    ],
    ids=[
        "No `allowedHosts`",
        "Has `allowdHosts` but no `hosts`",
        "Has `hosts` but it's empty list",
        "Has non-empty `hosts`",
    ],
)
async def test_certified_connector_has_allowed_hosts(metadata_yaml, should_raise_assert_error, expected_error) -> None:
    t = test_core.TestConnectorAttributes()

    if should_raise_assert_error:
        with pytest.raises(AssertionError) as e:
            await t.test_certified_connector_has_allowed_hosts(
                operational_certification_test=True, allowed_hosts_test=True, connector_metadata=metadata_yaml
            )
        assert expected_error in repr(e.value)
    else:
        await t.test_certified_connector_has_allowed_hosts(
            operational_certification_test=True, allowed_hosts_test=True, connector_metadata=metadata_yaml
        )


@pytest.mark.parametrize(
    "metadata_yaml, should_raise_assert_error, expected_error",
    [
        pytest.param(
            {"data": {"ab_internal": {"ql": 400}}},
            True,
            "The `suggestedStreams` property is missing in `metadata.data` for `metadata.yaml`",
        ),
        pytest.param(
            {"data": {"ab_internal": {"ql": 400}, "suggestedStreams": {}}},
            True,
            "The `streams` property is missing in `metadata.data.suggestedStreams` for `metadata.yaml`",
        ),
        pytest.param(
            {"data": {"ab_internal": {"ql": 400}, "suggestedStreams": {"streams": []}}},
            True,
            "'The `streams` empty list is not allowed for `metadata.data.suggestedStreams` for certified connectors",
        ),
        pytest.param(
            {"data": {"ab_internal": {"ql": 400}, "suggestedStreams": {"streams": ["stream_1", "stream_2"]}}},
            False,
            None,
        ),
    ],
    ids=[
        "No `suggestedStreams`",
        "Has `suggestedStreams` but no `streams`",
        "Has `streams` but it's empty list",
        "Has non-empty `streams`",
    ],
)
async def test_certified_connector_has_suggested_streams(metadata_yaml, should_raise_assert_error, expected_error) -> None:
    t = test_core.TestConnectorAttributes()

    if should_raise_assert_error:
        with pytest.raises(AssertionError) as e:
            await t.test_certified_connector_has_suggested_streams(
                operational_certification_test=True, suggested_streams_test=True, connector_metadata=metadata_yaml
            )
        assert expected_error in repr(e.value)
    else:
        await t.test_certified_connector_has_suggested_streams(
            operational_certification_test=True, suggested_streams_test=True, connector_metadata=metadata_yaml
        )
