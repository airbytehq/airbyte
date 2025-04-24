#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from dataclasses import asdict

import pytest
from source_zoho_crm.exceptions import IncompleteMetaDataException, UnknownDataTypeException
from source_zoho_crm.types import FieldMeta, ModuleMeta, ZohoBaseType, ZohoPickListItem

from .parametrize import datatype_inputs


class TestData(ZohoBaseType):
    array = "array"
    object = "object"
    string = "string"
    integer = "integer"


def test_base_type():
    assert TestData.array == TestData.array
    assert TestData.string != TestData.integer
    assert TestData.object == "object"
    assert TestData.all() == ["array", "object", "string", "integer"]
    assert TestData.integer in TestData.all()


def test_module_schema_missing_fields():
    with pytest.raises(IncompleteMetaDataException):
        module = ModuleMeta(api_name="Leads", module_name="Leads", api_supported=True, fields=[])
        _ = module.schema


def test_module_schema():
    fields = [
        FieldMeta(
            json_type="string",
            length=256,
            api_name="Content",
            data_type="text",
            decimal_place=None,
            system_mandatory=True,
            display_label="Note content",
            pick_list_values=[],
        )
    ]
    module = ModuleMeta(api_name="Notes", module_name="Notes", api_supported=True, fields=fields)
    assert asdict(module.schema) == {
        "additionalProperties": True,
        "description": "Notes",
        "properties": {
            "Content": {"maxLength": 256, "title": "Note content", "type": ["null", "string"]},
            "Modified_Time": {"format": "date-time", "type": "string"},
            "id": {"type": "string"},
        },
        "required": ["id", "Modified_Time", "Content"],
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
    }


def test_field_schema_unknown_type():
    field = FieldMeta(
        json_type="datetime",
        length=None,
        api_name="dummy",
        data_type="timestampwtz",
        decimal_place=None,
        system_mandatory=False,
        display_label="",
        pick_list_values=[],
    )
    with pytest.raises(UnknownDataTypeException):
        _ = field.schema


@datatype_inputs
def test_field_schema(json_type, data_type, length, decimal_place, api_name, pick_list_values, autonumber, expected_values):
    if pick_list_values:
        pick_list_values = [ZohoPickListItem(actual_value=value, display_value=value) for value in pick_list_values]
    field = FieldMeta(
        json_type=json_type,
        length=length,
        api_name=api_name,
        data_type=data_type,
        decimal_place=decimal_place,
        system_mandatory=True,
        display_label=api_name,
        pick_list_values=pick_list_values,
        auto_number=autonumber or {"prefix": "", "suffix": ""},
    )

    assert field.schema == expected_values
