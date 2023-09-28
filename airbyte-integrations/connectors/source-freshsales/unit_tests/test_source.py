#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
import requests
from source_freshsales.source import Contacts, FreshsalesStream, OpenDeals, OpenTasks, SourceFreshsales


def test_get_input_stream_args(config):
    source = SourceFreshsales()
    expected_keys = ["authenticator", "domain_name"]
    actual = source.get_input_stream_args(config['api_key'], config["domain_name"])
    for key in expected_keys:
        assert key in actual.keys()


def test_check_connection(mocker, config):
    source = SourceFreshsales()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, config) == (True, None)


def test_count_streams(mocker):
    source = SourceFreshsales()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 9
    assert len(streams) == expected_streams_number


def test_url_base(stream_args):
    stream = FreshsalesStream(**stream_args)
    expected = f"https://{stream_args.get('domain_name')}/crm/sales/api/"
    actual = stream.url_base
    assert actual == expected


def test_next_page_token(stream_args, requests_mock):
    stream = Contacts(**stream_args)
    stream_filters = [{"id": 1, "name": stream.filter_name}]
    with patch.object(stream, "_get_filters", return_value=stream_filters) as mock_method:
        url = f"{stream.url_base}{stream.path()}"
        requests_mock.get(url, json={stream.name: [{'id': 123}]})
        response = requests.get(url)
        assert stream.next_page_token(response) == 2
        mock_method.assert_called()


def test_request_params(stream_args):
    stream = OpenTasks(**stream_args)
    actual = stream.request_params()
    expected = {'filter': 'open', 'page': 1, 'sort': 'updated_at', 'sort_type': 'asc'}
    assert actual == expected


@pytest.mark.parametrize(
    "stream, response, expected",
    [
        (Contacts, [{'id': 123}], [{'id': 123}]),
        (OpenDeals, [{'id': 234, "fc_widget_collaboration": {"test": "test"}}], [{'id': 234}]),
    ],
    ids=["Contacts", "OpenDeals"]
)
def test_parse_response(stream, response, expected, stream_args, requests_mock):
    stream = stream(**stream_args)
    stream_filters = [{"id": 1, "name": stream.filter_name}]
    with patch.object(stream, "_get_filters", return_value=stream_filters) as mock_method:
        url = f"{stream.url_base}{stream.path()}"
        requests_mock.get(url, json={stream.object_name: response})
        _resp = requests.get(url)
        assert list(stream.parse_response(_resp)) == expected
        mock_method.assert_called()


def test_path(stream_args):
    stream = Contacts(**stream_args)
    stream_filters = [{"id": 1, "name": stream.filter_name}]
    with patch.object(stream, "_get_filters", return_value=stream_filters) as mock_method:
        assert stream.path() == 'contacts/view/1'
        mock_method.assert_called()
