# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pathlib
from unittest.mock import patch
from xml.etree import ElementTree

import pytest


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
                    "_ab_is_unbounded": True,
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
                    "_ab_is_unbounded": True,
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
        (
            "report_with_dates.xml",
            {
                "data": {"type": ["object", "null"]},
                "SomeDate": {"type": ["string", "null"], "format": "date"},
                "SomeDateTime": {"type": ["string", "null"], "format": "date-time"},
            },
        ),
    ],
)
def test_get_properties(xml_file, expected_output, components_module):
    with open(
        str(pathlib.Path(__file__).parent / "resource/http/response/xml" / xml_file),
        "r",
    ) as f:
        xml_tree = ElementTree.fromstring(f.read())

    with patch.object(components_module.ReportXMLSchemaHelper, "_get_xml_tree", return_value=xml_tree):
        schema_helper = components_module.ReportXMLSchemaHelper({}, "")
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
def test_xml_schema_url(config, report_id, expected_output, components_module):
    with patch.object(components_module.ReportXMLSchemaHelper, "_get_xml_tree", return_value=""):
        with patch.object(components_module.ReportXMLSchemaHelper, "_extract_namespace", return_value={}):
            schema_helper = components_module.ReportXMLSchemaHelper(config, report_id)
            actual = schema_helper._xml_schema_url
    assert actual == expected_output


@pytest.mark.parametrize(
    "xml_file, unbounded_field",
    [
        ("report_1.xml", "Eligibility_Rules"),
        ("report_2.xml", "Job_Family_Group_for_Job_Family"),
    ],
)
def test_fields_transform_string_array(xml_file, unbounded_field, components_module):
    with open(
        str(pathlib.Path(__file__).parent / "resource/http/response/xml" / xml_file),
        "r",
    ) as f:
        xml_tree = ElementTree.fromstring(f.read())

    with patch.object(components_module.ReportXMLSchemaHelper, "_get_xml_tree", return_value=xml_tree):
        schema_helper = components_module.ReportXMLSchemaHelper({}, "")
        actual = schema_helper.get_properties()

    assert actual
    assert "_ab_is_unbounded" in str(actual)
    for field_name, field_type in actual.items():
        if field_type.get("_ab_is_unbounded", False):
            assert field_name == unbounded_field
    assert actual[unbounded_field]["_ab_is_unbounded"] is True
