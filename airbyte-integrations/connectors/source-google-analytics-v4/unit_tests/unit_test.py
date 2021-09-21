#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.parse import unquote

import pytest
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_google_analytics_v4.source import GoogleAnalyticsV4Stream, GoogleAnalyticsV4TypesList, SourceGoogleAnalyticsV4


def read_file(file_name):
    parent_location = Path(__file__).absolute().parent
    file = open(parent_location / file_name).read()
    return file


expected_metrics_dimensions_type_map = ({"ga:users": "INTEGER", "ga:newUsers": "INTEGER"}, {"ga:date": "STRING", "ga:country": "STRING"})


@pytest.fixture
def mock_metrics_dimensions_type_list_link(requests_mock):
    requests_mock.get(
        "https://www.googleapis.com/analytics/v3/metadata/ga/columns", json=json.loads(read_file("metrics_dimensions_type_list.json"))
    )


@pytest.fixture
def mock_auth_call(requests_mock):
    yield requests_mock.post("https://oauth2.googleapis.com/token", json={"access_token": "", "expires_in": 0})


def test_metrics_dimensions_type_list(mock_metrics_dimensions_type_list_link):
    test_metrics, test_dimensions = GoogleAnalyticsV4TypesList().read_records(sync_mode=None)

    assert test_metrics, test_dimensions == expected_metrics_dimensions_type_map


def get_metrics_dimensions_mapping():
    test_metrics_dimensions_map = {
        "metric": [("ga:users", "integer"), ("ga:newUsers", "integer")],
        "dimension": [("ga:dimension", "string")],
    }
    for field_type, attribute_expected_pairs in test_metrics_dimensions_map.items():
        for attribute_expected_pair in attribute_expected_pairs:
            attribute, expected = attribute_expected_pair
            yield field_type, attribute, expected


@pytest.mark.parametrize("metrics_dimensions_mapping", get_metrics_dimensions_mapping())
def test_lookup_metrics_dimensions_data_type(metrics_dimensions_mapping, mock_metrics_dimensions_type_list_link):
    test_config = json.loads(read_file("../integration_tests/sample_config.json"))
    test_config["authenticator"] = NoAuth()
    test_config["metrics"] = []
    test_config["dimensions"] = []

    field_type, attribute, expected = metrics_dimensions_mapping
    g = GoogleAnalyticsV4Stream(config=test_config)

    test = g.lookup_data_type(field_type, attribute)

    assert test == expected


@patch("source_google_analytics_v4.source.jwt")
def test_check_connection_jwt(jwt_encode_mock, mocker, mock_metrics_dimensions_type_list_link, mock_auth_call):
    test_config = json.loads(read_file("../integration_tests/sample_config.json"))
    del test_config["custom_reports"]
    test_config["credentials"] = {"credentials_json": '{"client_email": "", "private_key": "", "private_key_id": ""}'}
    source = SourceGoogleAnalyticsV4()
    assert source.check_connection(MagicMock(), test_config) == (True, None)
    jwt_encode_mock.encode.assert_called()
    assert mock_auth_call.called


@patch("source_google_analytics_v4.source.jwt")
def test_check_connection_oauth(jwt_encode_mock, mocker, mock_metrics_dimensions_type_list_link, mock_auth_call):
    test_config = json.loads(read_file("../integration_tests/sample_config.json"))
    del test_config["custom_reports"]
    test_config["credentials"] = {
        "client_id": "client_id_val",
        "client_secret": "client_secret_val",
        "refresh_token": "refresh_token_val",
    }
    source = SourceGoogleAnalyticsV4()
    assert source.check_connection(MagicMock(), test_config) == (True, None)
    jwt_encode_mock.encode.assert_not_called()
    assert "https://www.googleapis.com/auth/analytics.readonly" in unquote(mock_auth_call.last_request.body)
    assert "client_id_val" in unquote(mock_auth_call.last_request.body)
    assert "client_secret_val" in unquote(mock_auth_call.last_request.body)
    assert "refresh_token_val" in unquote(mock_auth_call.last_request.body)
    assert mock_auth_call.called
