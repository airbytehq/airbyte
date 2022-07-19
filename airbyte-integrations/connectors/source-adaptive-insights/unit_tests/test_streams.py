#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from source_adaptive_insights.source import (
    AdaptiveInsightsStream,
    ExportDimensions,
    ExportLevels,
    ExportAccounts
)

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

accounts_expected = {
    'id': 6, 
    'code': 'E', 
    'name': 'QQ', 
    'description': '', 
    'time_stratum': 'month', 
    'display_as': 'CURRENCY', 
    'account_type_code': 'B', 
    'decimal_precision': '0', 
    'is_assumption': None, 
    'suppress_zeroes': '1', 
    'is_default_root': '0', 
    'short_name': '', 
    'is_intercompany': '0', 
    'balance_type': 'DEBIT', 
    'is_linked': '0', 
    'owning_sheet_id': '', 
    'is_system': '0', 
    'is_importable': None, 
    'data_entry_type': 
    'STANDARD', 'plan_by': 
    'DELTA', 'actuals_by': 
    'BALANCE', 'time_rollup': 
    'LAST', 'time_weight_acct_id': '', 
    'level_dim_rollup': 'SUM', 
    'level_dim_weight_acct_id': '', 
    'rollup_text': '', 
    'start_expanded': None, 
    'has_salary_detail': '0', 
    'data_privacy': 'PUBLIC_ALL', 
    'is_breakback_eligible': '', 
    'sub_type': 'CUMULATIVE', 
    'enable_actuals': '1', 
    'is_group': '0', 
    'has_formula': '0', 
    'attributes': [
        {
            'name': 'FF', 
            'value': 'ghjk', 
            'attributeId': '22', 
            'valueId': '11'
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
    expected_data = f"""<?xml version='1.0' encoding='UTF-8'?>
        <call method="{stream.method}" callerName="Airbyte - auto">
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
    expected_data = f"""<?xml version='1.0' encoding='UTF-8'?>
        <call method="{stream.method}" callerName="Airbyte - auto">
        <credentials login="a" password="b"/>
        <include versionName="Current LBE" inaccessibleValues="true"/>
        </call>
        """.encode('utf-8')
    inputs = {"stream_state": {}}
    assert stream.request_body_data(**inputs) == expected_data


def test_parse_response_export_accounts(patch_base_class, requests_mock):
    stream = ExportAccounts(username="a", password="b")
    with open("unit_tests/sample_data/accounts_output.xml", "r") as fp:
        requests_data = fp.read()
    requests_mock.post("https://api.adaptiveinsights.com/api/v32", text=requests_data)
    resp = requests.post("https://api.adaptiveinsights.com/api/v32")
    inputs = {"response": resp}
    print(next(stream.parse_response(**inputs)))
    assert next(stream.parse_response(**inputs)) == accounts_expected


def test_http_method_export_accounts(patch_base_class):
    stream = ExportAccounts(username="a", password="b")
    expected_method = "POST"
    assert stream.http_method == expected_method


def test_method_export_accounts(patch_base_class):
    stream = ExportAccounts(username="a", password="b")
    expected_method = "exportAccounts"
    assert stream.method == expected_method


def test_request_body_data_export_accounts(patch_base_class):
    stream = ExportAccounts(username="a", password="b")
    expected_data = f"""<?xml version='1.0' encoding='UTF-8'?>
        <call method="{stream.method}" callerName="Airbyte - auto">
        <credentials login="a" password="b"/>
        <include versionName="Current LBE" inaccessibleValues="true"/>
        </call>
        """.encode('utf-8')
    inputs = {"stream_state": {}}
    assert stream.request_body_data(**inputs) == expected_data