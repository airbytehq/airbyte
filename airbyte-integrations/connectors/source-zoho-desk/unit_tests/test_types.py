
import pytest
from decimal import Decimal
from source_zoho_desk.types_zoho import (
    ZohoJsonType,
    ZohoDataType,
    ZohoPickListItem,
    FieldMeta,
    ModuleMeta,
    FromDictMixin
)


def test_zoho_json_type_all():
    assert ZohoJsonType.all() == ["string", "integer", "double", "boolean", "jsonarray", "jsonobject"]

def test_zoho_data_type_all():
    assert ZohoDataType.all() == [
        "textarea", "event_reminder", "phone", "text", "profileimage", "picklist", "bigint", 
        "website", "email", "date", "datetime", "integer", "currency", "double", "boolean", 
        "lookup", "ownerlookup", "autonumber", "multiselectpicklist", "RRULE", "ALARM"
    ]


def test_zoho_pick_list_item_from_dict():
    dct = {'value': 'Example Value'}
    item = ZohoPickListItem.from_dict(dct)
    assert item.display_value == 'Example Value'
    assert item.actual_value == 'Example Value'


def test_field_meta_from_dict():
    data = {
        'type': 'string',
        'maxLength': 255,
        'apiName': 'exampleField',
        'displayLabel': 'Example Field',
        'isMandatory': True,
        'allowedValues': [{'value': 'Option 1'}, {'value': 'Option 2'}]
    }
    field_meta = FieldMeta.from_dict(data)
    assert field_meta.json_type == 'string'
    assert field_meta.length == 255
    assert field_meta.api_name == 'exampleField'
    assert field_meta.display_label == 'Example Field'
    assert field_meta.system_mandatory is True
    assert field_meta.pick_list_values[0].display_value == 'Option 1'
    assert field_meta.pick_list_values[1].display_value == 'Option 2'

def test_field_meta_string_field():
    field_meta = FieldMeta(
        json_type='string',
        length=255,
        api_name='exampleField',
        data_type='Text',
        decimal_place=None,
        system_mandatory=True,
        display_label='Example Field'
    )
    typedef = field_meta._string_field()
    assert typedef['type'] == ['null', 'string']
    assert typedef['maxLength'] == 255
    assert typedef['title'] == 'Example Field'

def test_field_meta_jsonarray_field():
    field_meta = FieldMeta(
        json_type='array',
        length=None,
        api_name='exampleArray',
        data_type='Multiselect',
        decimal_place=None,
        system_mandatory=False,
        display_label='Example Array'
    )
    typedef = field_meta._jsonarray_field()
    assert typedef['type'] == 'array'
    assert typedef['title'] == 'Example Array'
    assert typedef['minItems'] == 1
    assert typedef['uniqueItems'] is True
    assert 'items' in typedef


def test_module_meta_from_dict():
    data = {
        'apiName': 'exampleModule',
        'displayLabel': 'Example Module',
        'isCustomModule': False,
        'fields': [
            {
                'type': 'string',
                'maxLength': 255,
                'apiName': 'exampleField',
                'displayLabel': 'Example Field',
                'isMandatory': True
            }
        ]
    }
    module_meta = ModuleMeta.from_dict(data)
    assert module_meta.api_name == 'exampleModule'
    assert module_meta.module_name == 'Example Module'
    assert module_meta.api_supported is True
    assert len(module_meta.fields) == 1
    assert module_meta.fields[0].api_name == 'exampleField'


class TestClass(FromDictMixin):
    dynamic_fields: dict = {}

def test_update_from_dict():
    test_obj = TestClass()
    test_dict = {'key': 'value'}
    test_obj.update_from_dict(test_dict)
    assert test_obj.dynamic_fields['data'] == test_dict
