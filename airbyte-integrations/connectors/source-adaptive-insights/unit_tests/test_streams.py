#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from source_adaptive_insights.source import AdaptiveInsightsStream, ExportDimensions, ExportLevels

dimensions_expected = {
    'attribute_id': None,
    'attribute_name': None,
    'attribute_value': None,
    'attribute_value_id': None,
    'dimension_id': 1,
    'dimension_name': 'A',
    'dimension_short_name': '',
    'value_description': '',
    'value_id': 2,
    'value_name': 'B',
    'value_short_name': ''
}

levels_expected = {
    'id': 5, 
    'name': 'D', 
    'currency': 'USD', 
    'short_name': '', 
    'is_elimination': '0', 
    'is_linked': '0', 
    'workflow_status': 'I', 
    'is_important': '1', 
    'attributes': [
        {
            'attributeId': '6', 
            'name': 'E', 
            'valueId': '11', 
            'value': 'F'
        }, 
        {
            'attributeId': '7', 
            'name': 'G', 
            'valueId': '12', 
            'value': 'H'
        }
    ]
}


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(AdaptiveInsightsStream, "path", "v0/example_endpoint")
    mocker.patch.object(AdaptiveInsightsStream, "primary_key", "test_primary_key")
    mocker.patch.object(AdaptiveInsightsStream, "__abstractmethods__", set())


def test_request_headers(patch_base_class):
    stream = AdaptiveInsightsStream(username="a", password="b")
    inputs = {}
    expected_headers = {'Content-Type': 'text/xml; charset=UTF-8'}
    assert stream.request_headers(**inputs) == expected_headers


def test_parse_response_export_dimensions(patch_base_class, requests_mock):
    stream = ExportDimensions(username="a", password="b")
    with open("unit_tests/sample_data/dimension_output.xml", "r") as fp:
        requests_data = fp.read()
    requests_mock.post("https://api.adaptiveinsights.com/api/v32", text=requests_data)
    resp = requests.post("https://api.adaptiveinsights.com/api/v32")
    inputs = {"response": resp}
    assert next(stream.parse_response(**inputs)) == dimensions_expected


def test_http_method_export_dimensions(patch_base_class):
    stream = ExportDimensions(username="a", password="b")
    expected_method = "POST"
    assert stream.http_method == expected_method


def test_method_export_dimensions(patch_base_class):
    stream = ExportDimensions(username="a", password="b")
    expected_method = "exportDimensions"
    assert stream.method == expected_method


def test_request_body_data_export_dimensions(patch_base_class):
    stream = ExportDimensions(username="a", password="b")
    expected_data = """<?xml version='1.0' encoding='UTF-8'?>
        <call method="exportDimensions" callerName="Airbyte - auto">
        <credentials login="a" password="b"/>
        <include versionName="Current LBE" dimensionValues="true"/>
        </call>
        """.encode('utf-8')
    inputs = {"stream_state": {}}
    assert stream.request_body_data(**inputs) == expected_data


def test_parse_response_export_levels(patch_base_class, requests_mock):
    stream = ExportLevels(username="a", password="b")
    with open("unit_tests/sample_data/levels_output.xml", "r") as fp:
        requests_data = fp.read()
    requests_mock.post("https://api.adaptiveinsights.com/api/v32", text=requests_data)
    resp = requests.post("https://api.adaptiveinsights.com/api/v32")
    inputs = {"response": resp}
    assert next(stream.parse_response(**inputs)) == levels_expected


def test_http_method_export_levels(patch_base_class):
    stream = ExportLevels(username="a", password="b")
    expected_method = "POST"
    assert stream.http_method == expected_method


def test_method_export_levels(patch_base_class):
    stream = ExportLevels(username="a", password="b")
    expected_method = "exportLevels"
    assert stream.method == expected_method


def test_request_body_data_export_levels(patch_base_class):
    stream = ExportLevels(username="a", password="b")
    expected_data = """<?xml version='1.0' encoding='UTF-8'?>
        <call method="exportLevels" callerName="Airbyte - auto">
        <credentials login="a" password="b"/>
        <include versionName="Current LBE" inaccessibleValues="true"/>
        </call>
        """.encode('utf-8')
    inputs = {"stream_state": {}}
    assert stream.request_body_data(**inputs) == expected_data
