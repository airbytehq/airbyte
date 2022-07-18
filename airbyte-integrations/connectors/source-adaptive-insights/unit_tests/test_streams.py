#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_adaptive_insights.source import AdaptiveInsightsStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(AdaptiveInsightsStream, "path", "v0/example_endpoint")
    mocker.patch.object(AdaptiveInsightsStream, "primary_key", "test_primary_key")
    mocker.patch.object(AdaptiveInsightsStream, "__abstractmethods__", set())


# def test_parse_response(patch_base_class):
#     stream = AdaptiveInsightsStream()
#     # TODO: replace this with your input parameters
#     inputs = {"response": MagicMock()}
#     # TODO: replace this with your expected parced object
#     expected_parsed_object = {}
#     assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_request_headers(patch_base_class):
    stream = AdaptiveInsightsStream(username="a", password="b")
    inputs = {}
    expected_headers = {'Content-Type': 'text/xml; charset=UTF-8'}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = AdaptiveInsightsStream(username="a", password="b")
    expected_method = "GET"
    assert stream.http_method == expected_method
