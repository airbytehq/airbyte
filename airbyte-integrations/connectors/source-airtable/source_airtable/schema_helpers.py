#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from copy import deepcopy
from typing import Any, Dict

from airbyte_cdk.models import AirbyteStream
from airbyte_cdk.models.airbyte_protocol import DestinationSyncMode, SyncMode


logger: logging.Logger = logging.getLogger("airbyte")


class SchemaTypes:
    string: Dict = {"type": ["null", "string"]}

    number: Dict = {"type": ["null", "number"]}

    boolean: Dict = {"type": ["null", "boolean"]}

    date: Dict = {"type": ["null", "string"], "format": "date"}

    datetime: Dict = {"type": ["null", "string"], "format": "date-time"}

    array_with_strings: Dict = {"type": ["null", "array"], "items": {"type": ["null", "string"]}}

    # array items should be automatically determined
    # based on field complexity
    array_with_any: Dict = {"type": ["null", "array"], "items": {}}


# More info about internal Airtable Data Types
# https://airtable.com/developers/web/api/field-model
SIMPLE_AIRTABLE_TYPES: Dict = {
    "multipleAttachments": SchemaTypes.string,
    "autoNumber": SchemaTypes.number,
    "barcode": SchemaTypes.string,
    "button": SchemaTypes.string,
    "checkbox": SchemaTypes.boolean,
    "singleCollaborator": SchemaTypes.string,
    "count": SchemaTypes.number,
    "createdBy": SchemaTypes.string,
    "createdTime": SchemaTypes.datetime,
    "currency": SchemaTypes.number,
    "email": SchemaTypes.string,
    "date": SchemaTypes.date,
    "dateTime": SchemaTypes.datetime,
    "duration": SchemaTypes.number,
    "lastModifiedBy": SchemaTypes.string,
    "lastModifiedTime": SchemaTypes.datetime,
    "multipleRecordLinks": SchemaTypes.array_with_strings,
    "multilineText": SchemaTypes.string,
    "multipleCollaborators": SchemaTypes.array_with_strings,
    "multipleSelects": SchemaTypes.array_with_strings,
    "number": SchemaTypes.number,
    "percent": SchemaTypes.number,
    "phoneNumber": SchemaTypes.string,
    "rating": SchemaTypes.number,
    "richText": SchemaTypes.string,
    "singleLineText": SchemaTypes.string,
    "singleSelect": SchemaTypes.string,
    "externalSyncSource": SchemaTypes.string,
    "url": SchemaTypes.string,
    # referral default type
    "simpleText": SchemaTypes.string,
}

# returns the `array of Any` where Any is based on Simple Types.
# the final array is fulled with some simple type.
COMPLEX_AIRTABLE_TYPES: Dict = {
    "formula": SchemaTypes.array_with_any,
    "lookup": SchemaTypes.array_with_any,
    "multipleLookupValues": SchemaTypes.array_with_any,
    "rollup": SchemaTypes.array_with_any,
}

ARRAY_FORMULAS = ("ARRAYCOMPACT", "ARRAYFLATTEN", "ARRAYUNIQUE", "ARRAYSLICE")


class SchemaHelpers:
    @staticmethod
    def clean_name(name_str: str) -> str:
        return name_str.replace(" ", "_").lower().strip()

    @staticmethod
    def get_json_schema(table: Dict[str, Any]) -> Dict[str, str]:
        properties: Dict = {
            "_airtable_id": SchemaTypes.string,
            "_airtable_created_time": SchemaTypes.string,
            "_airtable_table_name": SchemaTypes.string,
        }

        fields: Dict = table.get("fields", {})
        for field in fields:
            name: str = SchemaHelpers.clean_name(field.get("name"))
            original_type: str = field.get("type")
            options: Dict = field.get("options", {})
            options_result: Dict = options.get("result", {})
            exec_type: str = options_result.get("type") if options_result else None

            # choose the JsonSchema Type for known Airtable Types
            if original_type in COMPLEX_AIRTABLE_TYPES.keys():
                complex_type = deepcopy(COMPLEX_AIRTABLE_TYPES.get(original_type))
                # process arrays with values
                field_type: str = exec_type if exec_type else "simpleText"
                # For cases with `options.result` == None, we should apply the type `string`.
                # Other edge cases, if `field_type` not in SIMPLE_AIRTABLE_TYPES, fall back to "simpleText" == `string`
                # reference issue: https://github.com/airbytehq/oncall/issues/1432#issuecomment-1412743120
                if complex_type == SchemaTypes.array_with_any:
                    if original_type == "formula" and field_type in ("number", "currency", "percent", "duration"):
                        complex_type = SchemaTypes.number
                    elif original_type == "formula" and not any((options.get("formula").startswith(x) for x in ARRAY_FORMULAS)):
                        complex_type = SchemaTypes.string
                    elif field_type in SIMPLE_AIRTABLE_TYPES:
                        complex_type["items"] = deepcopy(SIMPLE_AIRTABLE_TYPES.get(field_type))
                    else:
                        complex_type["items"] = SchemaTypes.string
                        logger.warning(f"Unknown field type: {field_type}, falling back to `simpleText` type")
                properties.update(**{name: complex_type})
            elif original_type in SIMPLE_AIRTABLE_TYPES.keys():
                field_type: str = exec_type if exec_type else original_type
                properties.update(**{name: deepcopy(SIMPLE_AIRTABLE_TYPES.get(field_type))})
            else:
                # Airtable may add more field types in the future and don't consider it a breaking change
                properties.update(**{name: SchemaTypes.string})

        json_schema: Dict = {
            "$schema": "https://json-schema.org/draft-07/schema#",
            "type": "object",
            "additionalProperties": True,
            "properties": properties,
        }

        return json_schema

    @staticmethod
    def get_airbyte_stream(stream_name: str, json_schema: Dict[str, Any]) -> AirbyteStream:
        return AirbyteStream(
            name=stream_name,
            json_schema=json_schema,
            supported_sync_modes=[SyncMode.full_refresh],
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append_dedup],
        )
