# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pathlib
from unittest.mock import patch
from xml.etree import ElementTree

import pytest
from source_falcon.schema_helper import ReportXMLSchemaHelper


@pytest.mark.parametrize(
    "xml_file, expected_output",
    [
        (
            "report_1.xml",
            {
                "Eligibility_Rules": {
                    "items": {
                        "properties": {"ID": {"type": ["string", "null"]}},
                        "type": ["object", "null"],
                    },
                    "type": ["array", "null"],
                },
                "Stock_Plan": {"type": ["string", "null"]},
                "Target__": {"type": ["number", "null"]},
                "data": {"type": ["object", "null"]},
            },
        ),
        (
            "report_2.xml",
            {
                "Job_Family_Group_for_Job_Family": {
                    "items": {
                        "properties": {"ID": {"type": ["string", "null"]}},
                        "type": ["object", "null"],
                    },
                    "type": ["array", "null"],
                },
                "Job_Family_Groups_for_Job_Profile_group": {
                    "items": {
                        "properties": {"Job_Family_Group_Ref_ID": {"type": ["string", "null"]}},
                        "type": ["object", "null"],
                    },
                    "type": ["array", "null"],
                },
                "Job_Family_Ref_ID": {"type": ["string", "null"]},
                "Job_Profile": {"type": ["string", "null"]},
                "Job_Profile_Ref_ID": {"type": ["string", "null"]},
                "Management_Level": {"type": ["string", "null"]},
                "PLN_ESI_Job_Profile_Job_Family": {"type": ["string", "null"]},
                "data": {"type": ["object", "null"]},
            },
        ),
    ],
)
def test_get_properties(xml_file, expected_output):
    with open(
        str(pathlib.Path(__file__).parent / "resource/http/response/xml" / xml_file),
        "r",
    ) as f:
        xml_tree = ElementTree.fromstring(f.read())

    with patch.object(ReportXMLSchemaHelper, "_get_xml_tree", return_value=xml_tree):
        schema_helper = ReportXMLSchemaHelper({}, "")
        result = schema_helper.get_properties()

    assert result == expected_output


@pytest.mark.parametrize(
    "config, report_id, expected_output",
    [
        (
            {"tenant_id": "tenant_id", "host": "host.myworkday.com"},
            "report/all_accounts",
            "https://host.myworkday.com/ccx/service/customreport2/tenant_id/report/all_accounts?xsd",
        ),
        (
            {"tenant_id": "tenant_id", "host": "host.myworkday.com"},
            "report/all_accounts?Worktag_Types%21WID=someid",
            "https://host.myworkday.com/ccx/service/customreport2/tenant_id/report/all_accounts?xsd",
        ),
    ],
)
def test_xml_schema_url(config, report_id, expected_output):
    with patch.object(ReportXMLSchemaHelper, "_get_xml_tree", return_value=""):
        with patch.object(ReportXMLSchemaHelper, "_extract_namespace", return_value={}):
            schema_helper = ReportXMLSchemaHelper(config, report_id)
            actual = schema_helper._xml_schema_url
    assert actual == expected_output


@pytest.mark.parametrize(
    "xml_file, expected_output",
    [
        (
            "report_1.xml",
            [
                {
                    "path": ["Eligibility_Rules"],
                    "type": "AddedFieldDefinition",
                    "value": "{{ [{ 'ID': record['Eligibility_Rules'] }] if (record['Eligibility_Rules'] is string) else record['Eligibility_Rules'] }}",
                }
            ],
        ),
        (
            "report_2.xml",
            [
                {
                    "path": ["Job_Family_Group_for_Job_Family"],
                    "type": "AddedFieldDefinition",
                    "value": "{{ [{ 'ID': record['Job_Family_Group_for_Job_Family'] }] if (record['Job_Family_Group_for_Job_Family'] is string) else record['Job_Family_Group_for_Job_Family'] }}",
                }
            ],
        ),
    ],
)
def test_fields_transform_string_array(xml_file, expected_output):
    with open(
        str(pathlib.Path(__file__).parent / "resource/http/response/xml" / xml_file),
        "r",
    ) as f:
        xml_tree = ElementTree.fromstring(f.read())

    with patch.object(ReportXMLSchemaHelper, "_get_xml_tree", return_value=xml_tree):
        schema_helper = ReportXMLSchemaHelper({}, "")
        actual = schema_helper.fields_transform_string_array()
    assert actual == expected_output
