#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
import dataclasses
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Iterable, List, MutableMapping, Optional, Union

from .exceptions import IncompleteMetaDataException, UnknownDataTypeException


@dataclasses.dataclass
class Schema:
    description: str
    properties: Dict[str, Any]
    schema: str = "http://json-schema.org/draft-07/schema#"
    type: str = "object"
    additionalProperties: Any = True
    required: Optional[List[str]] = dataclasses.field(default_factory=list)


class ZohoBaseType(Enum):
    @classmethod
    def all(cls) -> List[str]:
        return list(map(lambda f: f.value, cls))

    def __eq__(self, other: object) -> bool:
        if type(other) is type(self):
            return super().__eq__(other)
        if type(other) == str:
            return self.value == other
        raise NotImplementedError(f"Type Mismatch: Enum and {type(other).__name__}")


class ZohoJsonType(ZohoBaseType):
    string = "string"
    integer = "integer"
    double = "double"
    boolean = "boolean"
    array = "jsonarray"
    object = "jsonobject"


class ZohoDataType(ZohoBaseType):
    textarea = "textarea"
    event_reminder = "event_reminder"
    phone = "phone"
    text = "text"
    profileimage = "profileimage"
    picklist = "picklist"
    bigint = "bigint"
    website = "website"
    email = "email"
    date = "date"
    datetime = "datetime"
    integer = "integer"
    currency = "currency"
    double = "double"
    boolean = "boolean"
    lookup = "lookup"
    ownerlookup = "ownerlookup"
    autonumber = "autonumber"
    multiselectpicklist = "multiselectpicklist"
    RRULE = "RRULE"
    ALARM = "ALARM"

    @classmethod
    def numeric_string_types(cls) -> Iterable["ZohoDataType"]:
        return cls.autonumber, cls.bigint


class FromDictMixin:

    def update_from_dict(self, dct: MutableMapping[Any, Any]):
        self.dynamic_fields["data"] = dct
      


@dataclasses.dataclass
class ZohoPickListItem(FromDictMixin):
    display_value: str
    actual_value: str

    @classmethod
    def from_dict(cls, dct: Dict[str, str]) -> 'ZohoPickListItem':

        value = dct.get('value', '')
        return cls(display_value=value, actual_value=value)
    
FieldType = Dict[Any, Any]



DATA_TYPE_MAPPING = {
    'Text': '_string_field',
    'Email': '_string_field',
    'Phone': '_string_field',
    'Picklist': '_string_field', 
    'Multiselect': '_jsonarray_field',
    'LookUp': '_jsonobject_field',
    'OwnerLookUp': '_jsonobject_field',
    'Textarea': '_string_field',
    'NumericString': '_string_field', 
    'Date': '_string_field',  
    'Datetime': '_string_field' 
}
@dataclasses.dataclass
class FieldMeta:
    json_type: str
    length: Optional[int]
    api_name: str
    data_type: str
    decimal_place: Optional[int]
    system_mandatory: bool
    display_label: str
    pick_list_values: Optional[List[ZohoPickListItem]] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'FieldMeta':
        mapped_data = {
            "json_type": data.get('type'),
            "length": data.get('maxLength'),
            "api_name": data.get('apiName'),
            "data_type": data.get('type'),
            "decimal_place": None, 
            "display_label": data.get('displayLabel'),
            "system_mandatory": data.get('isMandatory', False),
            "pick_list_values": [ZohoPickListItem.from_dict(item) for item in data.get('allowedValues', [])] if data.get('allowedValues') else None
        }
        return cls(**mapped_data)

    def _default_type_kwargs(self) -> Dict[str, str]:
        return {"title": self.display_label}

    def _picklist_items(self) -> Iterable[Union[str, None]]:
        default_list = [None]
        if not self.pick_list_values:
            return default_list
        return default_list + [pick_item.display_value for pick_item in self.pick_list_values]

    def _boolean_field(self) -> FieldType:
        return {"type": ["null", "boolean"], **self._default_type_kwargs()}

    def _integer_field(self) -> FieldType:
        return {"type": ["null", "integer"], **self._default_type_kwargs()}

    def _double_field(self) -> FieldType:
        typedef = {"type": ["null", "number"], **self._default_type_kwargs()}
        if self.decimal_place:
            typedef["multipleOf"] = float(Decimal("0.1") ** self.decimal_place)
        return typedef

    def _string_field(self) -> FieldType:
        typedef = {"type": ["null", "string"], "maxLength": self.length, **self._default_type_kwargs()}
        if self.data_type == 'Website':
            typedef["format"] = "uri"
        elif self.data_type == 'Email':
            typedef["format"] = "email"
        elif self.data_type == 'Date':
            typedef["format"] = "date"
        elif self.data_type == 'Datetime':
            typedef["format"] = "date-time"
        elif self.data_type in ['NumericString', 'Phone', 'Text']:
            typedef["airbyte_type"] = "big_integer"
        elif self.data_type == 'Picklist' and self.pick_list_values:
            typedef["enum"] = self._picklist_items()
        return typedef

    def _jsonarray_field(self) -> FieldType:
        typedef = {"type": "array", **self._default_type_kwargs()}
        if self.data_type in ['Text', 'NumericString']:
            typedef["items"] = {"type": "string"}
            if self.data_type == 'NumericString':
                typedef["items"]["airbyte_type"] = "big_integer"
        if self.data_type == 'Multiselect':
            typedef["minItems"] = 1
            typedef["uniqueItems"] = True
            items = {"type": ["null", "string"]}
            if self.pick_list_values:
                items["enum"] = self._picklist_items()
            typedef["items"] = items
        return typedef

    def _jsonobject_field(self) -> FieldType:
        lookup_typedef = {
            "type": ["null", "object"],
            "additionalProperties": False,
            "required": ["name", "id"],
            "properties": {"name": {"type": ["null", "string"]}, "id": {"type": "string"}},
            **self._default_type_kwargs(),
        }
        if self.data_type == 'LookUp':
            return lookup_typedef
        if self.data_type == 'OwnerLookUp':
            owner_lookup_typedef = copy.deepcopy(lookup_typedef)
            owner_lookup_typedef["required"] += ["email"]
            owner_lookup_typedef["properties"]["email"] = {"type": "string", "format": "email"}
            return owner_lookup_typedef
        return {"type": ["null", "object"]}

    
@dataclasses.dataclass
class ModuleMeta(FromDictMixin):
    api_name: str
    module_name: str
    api_supported: bool
    fields: Optional[Iterable[FieldMeta]] = dataclasses.field(default_factory=list)
    dynamic_fields: dict = dataclasses.field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> 'ModuleMeta':
        mapped_data = {
            "api_name" : data.get('apiName'),
            "module_name" : data.get('displayLabel'),  
            "api_supported" : not data.get('isCustomModule', False), 
            "fields" : [FieldMeta.from_dict(field) for field in data.get('fields', [])]  
        }
        return cls(**mapped_data)
    
   