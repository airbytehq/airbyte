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


def test_module_schema_without_datetime_fields():
    """When module has no datetime field, Modified_Time is injected as fallback."""
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
    schema = asdict(module.schema)
    assert "Modified_Time" in schema["properties"]
    assert "Modified_Time" in schema["required"]
    assert schema["properties"]["Modified_Time"] == {"format": "date-time", "type": "string"}


def test_module_schema_with_modified_time_field():
    """When module fields include Modified_Time, it is NOT separately injected."""
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
        ),
        FieldMeta(
            json_type="string",
            length=None,
            api_name="Modified_Time",
            data_type="datetime",
            decimal_place=None,
            system_mandatory=True,
            display_label="Modified Time",
            pick_list_values=[],
        ),
    ]
    module = ModuleMeta(api_name="Leads", module_name="Leads", api_supported=True, fields=fields)
    schema = asdict(module.schema)
    # Modified_Time comes from fields, not injected
    assert "Modified_Time" in schema["properties"]
    assert schema["properties"]["Modified_Time"] == {
        "format": "date-time",
        "maxLength": None,
        "title": "Modified Time",
        "type": ["null", "string"],
    }


def test_module_schema_with_alternative_datetime_cursor():
    """When module has a datetime field but no Modified_Time, Modified_Time is not injected."""
    fields = [
        FieldMeta(
            json_type="string",
            length=None,
            api_name="Action_Performed_Time",
            data_type="datetime",
            decimal_place=None,
            system_mandatory=True,
            display_label="Action Performed Time",
            pick_list_values=[],
        ),
    ]
    module = ModuleMeta(api_name="Actions_Performed", module_name="Actions Performed", api_supported=True, fields=fields)
    schema = asdict(module.schema)
    # Modified_Time should NOT be injected since module has its own datetime field
    assert "Modified_Time" not in schema["properties"]
    assert "Modified_Time" not in schema["required"]
    assert "Action_Performed_Time" in schema["properties"]


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
