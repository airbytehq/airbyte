#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from pytest import fixture
from source_microsoft_dataverse.source import IncrementalMicrosoftDataverseStream


@fixture
def incremental_config():
    return {
        "url": "http://test-url",
        "stream_name": "test_stream",
        "stream_path": "test_path",
        "primary_key": [["test_primary_key"]],
        "schema": {

        },
        "odata_maxpagesize": 100,
        "config_cursor_field": ["test_cursor_field"],
        "authenticator": MagicMock()
    }


@fixture
def incremental_response(incremental_config):
    return {
        "@odata.deltaLink": f"{incremental_config['url']}?$deltatoken=12644418993%2110%2F06%2F2022%2020%3A06%3A12",
        "value": [
            {
                "test_primary_key": "pk",
                "test_cursor_field": "test-date"
            },
            {
                "id": "pk2",
                "@odata.context": "context",
                "reason": "deleted"
            }
        ]
    }


def test_primary_key(incremental_config):
    stream = IncrementalMicrosoftDataverseStream(**incremental_config)
    expected_primary_key = [["test_primary_key"]]
    assert stream.primary_key == expected_primary_key


def test_stream_name(incremental_config):
    stream = IncrementalMicrosoftDataverseStream(**incremental_config)
    expected_stream_name = "test_stream"
    assert stream.name == expected_stream_name


def test_stream_path(incremental_config):
    stream = IncrementalMicrosoftDataverseStream(**incremental_config)
    expected_stream_path = "test_path"
    assert stream.path() == expected_stream_path


def test_cursor_field(incremental_config):
    stream = IncrementalMicrosoftDataverseStream(**incremental_config)
    expected_cursor_field = ["test_cursor_field"]
    assert stream.cursor_field == expected_cursor_field


def test_supports_incremental(incremental_config, mocker):
    mocker.patch.object(IncrementalMicrosoftDataverseStream, "cursor_field", "dummy_field")
    stream = IncrementalMicrosoftDataverseStream(**incremental_config)
    assert stream.supports_incremental


def test_source_defined_cursor(incremental_config):
    stream = IncrementalMicrosoftDataverseStream(**incremental_config)
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(incremental_config):
    stream = IncrementalMicrosoftDataverseStream(**incremental_config)
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval


def test_parse_request(incremental_config, incremental_response, mocker):
    response_mock, datetime_mock = MagicMock(), MagicMock()
    response_mock.json.return_value = incremental_response
    datetime_mock.now.return_value.isoformat.return_value = "test-time"
    mocker.patch("source_microsoft_dataverse.streams.datetime", datetime_mock)

    stream = IncrementalMicrosoftDataverseStream(**incremental_config)

    iterable = stream.parse_response(response_mock)
    iterable_list = list(iterable)
    assert len(iterable_list) == 2
    assert stream.state[stream.delta_token_field] == "12644418993!10/06/2022 20:06:12"
    assert iterable_list[0]["_ab_cdc_updated_at"] == "test-date"
    assert iterable_list[1]["_ab_cdc_deleted_at"] == "test-time"
    assert iterable_list[1][incremental_config["primary_key"][0][0]] == "pk2"
    assert "id" not in iterable_list[1]
    assert "reason" not in iterable_list[1]
    assert "@odata.context" not in iterable_list[1]


def test_request_headers(incremental_config):
    stream = IncrementalMicrosoftDataverseStream(**incremental_config)
    headers = stream.request_headers(stream_state={})
    assert "Prefer" in headers
    assert headers["Prefer"] == "odata.track-changes,odata.maxpagesize=100"
