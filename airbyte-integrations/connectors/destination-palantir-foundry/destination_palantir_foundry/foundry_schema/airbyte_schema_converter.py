from typing import Dict, Any, Optional, List

from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema, FoundryFieldSchema, \
    StringFieldSchema, BooleanFieldSchema, DateFieldSchema, TimestampFieldSchema, IntegerFieldSchema, DoubleFieldSchema, \
    ArrayFieldSchema, StructFieldSchema
from destination_palantir_foundry.foundry_schema.providers.streams.common import STREAM_DATA_FRAME_READER_CLASS


def convert_ab_field_to_foundry_field(ab_field_name: Optional[str], ab_field_schema: Dict[str, Any]) -> FoundryFieldSchema:
    ab_field_types = ab_field_schema.get("type", [])

    if not isinstance(ab_field_types, list):
        ab_field_types = [ab_field_types]

    nullable = "null" in ab_field_types
    ab_field_type = list(filter(lambda field_type: field_type != "null", ab_field_types))[0] if len(ab_field_types) > 0 else None

    if ab_field_type == "string":
        string_format = ab_field_schema.get("format", None)

        if string_format is None:
            return StringFieldSchema(
                name=ab_field_name,
                nullable=nullable,
            )
        elif string_format == "date":
            return DateFieldSchema(
                name=ab_field_name,
                nullable=nullable,
            )
        elif string_format == "date-time":
            # date_time_type = property_schema.get("airbyte_type", None) (maybe?)
            return TimestampFieldSchema(
                name=ab_field_name,
                nullable=nullable,
            )
        else:
            # this case includes the 'time' type
            return StringFieldSchema(
                name=ab_field_name,
                nullable=nullable,
            )

    elif ab_field_type == "boolean":
        return BooleanFieldSchema(
            name=ab_field_name,
            nullable=nullable,
        )

    elif ab_field_type == "integer":
        return IntegerFieldSchema(
            name=ab_field_name,
            nullable=nullable,
        )

    elif ab_field_type == "number":
        number_subtype = ab_field_schema.get("airbyte_type", None)

        if number_subtype == "integer":
            return IntegerFieldSchema(
                name=ab_field_name,
                nullable=nullable,
            )
        else:
            return DoubleFieldSchema(
                name=ab_field_name,
                nullable=nullable,
            )

    elif ab_field_type == "array":
        item_type: Optional[Dict] = ab_field_schema.get("items", None)
        if item_type is None:
            array_subtype = StringFieldSchema(
                name=None,
                nullable=True,
            )
        else:
            array_subtype = convert_ab_field_to_foundry_field(None, item_type)

        return ArrayFieldSchema(
            name=ab_field_name,
            nullable=nullable,
            arraySubtype=array_subtype,
        )

    elif ab_field_type == "object" and ab_field_schema.get("oneOf", None) is None:
        # if additional props, probably make map
        sub_schemas: List[FoundryFieldSchema] = []
        for obj_property_name, obj_property_schema in ab_field_schema.get("properties", {}).items():
            sub_schemas.append(convert_ab_field_to_foundry_field(obj_property_name, obj_property_schema))

        return StructFieldSchema(
            name=ab_field_name,
            nullable=nullable,
            subSchemas=sub_schemas,
        )
    elif ab_field_schema.get("oneOf", None) is not None:
        # for json
        return StringFieldSchema(
            name=ab_field_name,
            nullable=nullable,
        )
    else:
        # anything else, just assume json
        return StringFieldSchema(
            name=ab_field_name,
            nullable=nullable,
        )


def convert_ab_to_foundry_stream_schema(ab_json_schema: Dict[str, Any]) -> FoundrySchema:
    field_schemas = []
    for property_name, property_schema in ab_json_schema.get("properties", {}).items():
        field_schemas.append(convert_ab_field_to_foundry_field(property_name, property_schema))

    return FoundrySchema(
        fieldSchemaList=field_schemas,
        dataFrameReaderClass=STREAM_DATA_FRAME_READER_CLASS,
        customMetadata={
            "streaming": {
                "type": "avro"
            },
            "format": "avro"
        }
    )
