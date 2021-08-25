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

import pytest
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_google_analytics_v4.source import GoogleAnalyticsV4Stream, GoogleAnalyticsV4TypesList


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
