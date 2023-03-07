#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
import textwrap
import inspect
from source_adaptive_insights.source import (
    AdaptiveInsightsStream,
    ExportDimensions,
    ExportLevels,
    ExportAccounts,
    ExportData,
    ExportHeadcount
)

dimensions_expected = {
    'id': 25707643020,
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
    'value_short_name': '',
    'version': 'c',
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
    'version': 'c',
    'attributes': str([
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
    ])
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
    'version': 'c',
    'rollup_to_code': 'D',
    'rollup_to_text': 'TT',
    'attributes': str([
        {
            'name': 'FF', 
            'value': 'ghjk', 
            'attributeId': '22', 
            'valueId': '11'
        }
    ])
}

data_expected = {
    'account_code': 'b',
    'account_name': 'a',
    'amount': 1223.12,
    'assignment': 123.12,
    'contract': 'i',
    'date': '2022-04-01',
    'gl_account': 'e',
    'id': 809651416006,
    'level': 'c',
    'location': 'g',
    'version': 'c'
}

@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(AdaptiveInsightsStream, "path", "v0/example_endpoint")
    mocker.patch.object(AdaptiveInsightsStream, "primary_key", "test_primary_key")
    mocker.patch.object(AdaptiveInsightsStream, "__abstractmethods__", set())


def test_request_headers(patch_base_class):
    stream = AdaptiveInsightsStream(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    inputs = {}
    expected_headers = {'Content-Type': 'text/xml; charset=UTF-8'}
    assert stream.request_headers(**inputs) == expected_headers


def test_parse_response_export_dimensions(patch_base_class, requests_mock):
    stream = ExportDimensions(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    with open("unit_tests/sample_data/dimension_output.xml", "r") as fp:
        requests_data = fp.read()
    requests_mock.post("https://api.adaptiveinsights.com/api/v32", text=requests_data)
    resp = requests.post("https://api.adaptiveinsights.com/api/v32")
    inputs = {"response": resp}
    assert next(stream.parse_response(**inputs)) == dimensions_expected


def test_http_method_export_dimensions(patch_base_class):
    stream = ExportDimensions(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    expected_method = "POST"
    assert stream.http_method == expected_method


def test_method_export_dimensions(patch_base_class):
    stream = ExportDimensions(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    expected_method = "exportDimensions"
    assert stream.method == expected_method


def test_request_body_data_export_dimensions(patch_base_class):
    stream = ExportDimensions(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    expected_data = f"""<?xml version='1.0' encoding='UTF-8'?>
        <call method="{stream.method}" callerName="Airbyte - auto">
        <credentials login="a" password="b"/>
        <include versionName="Current LBE" dimensionValues="true"/>
        </call>
        """.encode('utf-8')
    inputs = {"stream_state": {}}
    assert stream.request_body_data(**inputs) == expected_data


def test_parse_response_export_levels(patch_base_class, requests_mock):
    stream = ExportLevels(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    with open("unit_tests/sample_data/levels_output.xml", "r") as fp:
        requests_data = fp.read()
    requests_mock.post("https://api.adaptiveinsights.com/api/v32", text=requests_data)
    resp = requests.post("https://api.adaptiveinsights.com/api/v32")
    inputs = {"response": resp}
    assert next(stream.parse_response(**inputs)) == levels_expected


def test_http_method_export_levels(patch_base_class):
    stream = ExportLevels(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    expected_method = "POST"
    assert stream.http_method == expected_method


def test_method_export_levels(patch_base_class):
    stream = ExportLevels(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    expected_method = "exportLevels"
    assert stream.method == expected_method


def test_request_body_data_export_levels(patch_base_class):
    stream = ExportLevels(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    expected_data = f"""<?xml version='1.0' encoding='UTF-8'?>
        <call method="{stream.method}" callerName="Airbyte - auto">
        <credentials login="a" password="b"/>
        <include versionName="Current LBE" inaccessibleValues="true"/>
        </call>
        """.encode('utf-8')
    inputs = {"stream_state": {}}
    assert stream.request_body_data(**inputs) == expected_data


def test_parse_response_export_accounts(patch_base_class, requests_mock):
    stream = ExportAccounts(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    with open("unit_tests/sample_data/accounts_output.xml", "r") as fp:
        requests_data = fp.read()
    requests_mock.post("https://api.adaptiveinsights.com/api/v32", text=requests_data)
    resp = requests.post("https://api.adaptiveinsights.com/api/v32")
    inputs = {"response": resp}
    assert next(stream.parse_response(**inputs)) == accounts_expected


def test_http_method_export_accounts(patch_base_class):
    stream = ExportAccounts(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    expected_method = "POST"
    assert stream.http_method == expected_method


def test_method_export_accounts(patch_base_class):
    stream = ExportAccounts(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    expected_method = "exportAccounts"
    assert stream.method == expected_method


def test_request_body_data_export_accounts(patch_base_class):
    stream = ExportAccounts(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    expected_data = f"""<?xml version='1.0' encoding='UTF-8'?>
        <call method="{stream.method}" callerName="Airbyte - auto">
        <credentials login="a" password="b"/>
        <include versionName="Current LBE" inaccessibleValues="true"/>
        </call>
        """.encode('utf-8')
    inputs = {"stream_state": {}}
    assert stream.request_body_data(**inputs) == expected_data


def test_parse_response_export_data(patch_base_class, requests_mock):
    stream = ExportData(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    with open("unit_tests/sample_data/data_output.xml", "r") as fp:
        requests_data = fp.read()
    requests_mock.post("https://api.adaptiveinsights.com/api/v32", text=requests_data)
    resp = requests.post("https://api.adaptiveinsights.com/api/v32")
    inputs = {"response": resp}
    assert next(stream.parse_response(**inputs)) == data_expected

def test_parse_response_export_data_no_data(patch_base_class, requests_mock):
    stream = ExportData(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    with open("unit_tests/sample_data/data_output_no_data.xml", "r") as fp:
        requests_data = fp.read()
    requests_mock.post("https://api.adaptiveinsights.com/api/v32", text=requests_data)
    resp = requests.post("https://api.adaptiveinsights.com/api/v32")
    inputs = {"response": resp}
    assert next(stream.parse_response(**inputs), {}) == {}



def test_http_method_export_data(patch_base_class):
    stream = ExportData(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    expected_method = "POST"
    assert stream.http_method == expected_method


def test_method_export_data(patch_base_class):
    stream = ExportData(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    expected_method = "exportData"
    assert stream.method == expected_method


def test_request_body_data_export_data(patch_base_class):
    stream = ExportData(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    expected_data = """<?xml version='1.0' encoding='UTF-8'?>
        <call method="exportData" callerName="Airbyte - auto">
        <credentials login="a" password="b"/>
        <version name="c" isDefault="false"/>
        <format useInternalCodes="true" includeCodes="false" includeNames="true" displayNameEnabled="true"/>
        <filters>
        <accounts><account code="e" isAssumption="false" includeDescendants="true"/><account code="f" isAssumption="false" includeDescendants="true"/></accounts>
        <timeSpan start="01/2019" end="01/2019"/>
        </filters>
        <dimensions>
        <dimension name="GL Account"/>
        <dimension name="Location" />
        <dimension name="Contract"/>
        <dimension name="Assignment"/>
        </dimensions>
        <rules includeZeroRows="false" includeRollupAccounts="true" timeRollups="false">
        <currency override="USD"/>
        </rules>
        </call>
        """.encode('utf-8')
    inputs = {}
    assert stream.construct_xml_body(start_date="01/2019", end_date="01/2019") == expected_data


def test_request_body_data_export_headcount(patch_base_class):
    stream = ExportHeadcount(username="a", password="b", version_type="c", start_date="d", accounts="e,f")
    expected_data = """<?xml version='1.0' encoding='UTF-8'?>
        <call method="exportData" callerName="Airbyte - auto">
        <credentials login="a" password="b"/>
        <version name="c" isDefault="false"/>
        <format useInternalCodes="true" includeCodes="false" includeNames="true" displayNameEnabled="true"/>
        <filters>
        <accounts>
        <account code="personnel.ActualRptHC" isAssumption="false" includeDescendants="true"/>
        </accounts>
        <timeSpan start="01/2019" end="01/2019"/>
        </filters>
        <dimensions>
        <dimension name="Position"/>
        <dimension name="Assignment"/>
        <dimension name="Location"/>
        <dimension name="Personnel_Input_Type"/>
        </dimensions>
        <rules includeZeroRows="false" includeRollupAccounts="true" timeRollups="false">
        <currency override="USD"/>
        </rules>
        </call>
        """.encode('utf-8')
    inputs = {}
    assert stream.construct_xml_body(start_date="01/2019") == expected_data
