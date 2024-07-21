from typing import Dict, Any, List

from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema, FoundryFieldSchema, \
    StringFieldSchema, BooleanFieldSchema, DateFieldSchema, TimestampFieldSchema, IntegerFieldSchema, DoubleFieldSchema, \
    ArrayFieldSchema
from destination_palantir_foundry.foundry_schema.providers.streams.common import STREAM_DATA_FRAME_READER_CLASS


def _convert_ab_field_to_foundry_field(ab_field_name: str, ab_field_schema: Dict[str, Any]) -> FoundryFieldSchema:
    ab_field_types = ab_field_schema.get("type", [])

    nullable = "null" in ab_field_types
    ab_field_type = list(filter(lambda field_type: field_type != "null", ab_field_types))[0]

    print(ab_field_type, nullable)

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
                nullable=nullable
            )
        elif string_format == "date-time":
            # date_time_type = property_schema.get("airbyte_type", None) (maybe?)
            return TimestampFieldSchema(
                name=ab_field_name,
                nullable=nullable
            )
        else:
            # TODO(jcrowson): includes time. Makes sense?
            return StringFieldSchema(
                name=ab_field_name,
                nullable=nullable
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
                nullable=nullable
            )

    elif ab_field_type == "array":
        array_subtype = _convert_ab_field_to_foundry_field(ab_field_name, ab_field_schema.get("items", {}))  # broken
        return ArrayFieldSchema(
            name=ab_field_name,
            nullable=nullable,
            arraySubtype=array_subtype
        )

    elif ab_field_type == "object":
        # if additional props, probably make map
        pass

    elif ab_field_type == "oneOf":
        # for json
        return StringFieldSchema(
            name=ab_field_name,
            nullable=nullable
        )


def convert_ab_to_foundry_stream_schema(ab_json_schema: Dict[str, Any]) -> FoundrySchema:
    """
    Convert Airbyte JSON schema to Foundry schema
    """

    def helper(schema: Dict, parent: str = '') -> List[FoundryFieldSchema]:
        fields = []
        for property_name, property_schema in schema.get("properties", {}).items():
            ab_field_types = property_schema.get("type", [])

            nullable = "null" in ab_field_types
            ab_field_type = list(filter(lambda field_type: field_type != "null", ab_field_types))[0]

            print(ab_field_type, nullable)

            if ab_field_type == "string":
                string_format = property_schema.get("format", None)

                if string_format is None:
                    fields.append(StringFieldSchema(
                        name=property_name,
                        nullable=nullable,
                    ))
                elif string_format == "date":
                    fields.append(DateFieldSchema(
                        name=property_name,
                        nullable=nullable
                    ))
                elif string_format == "date-time":
                    # date_time_type = property_schema.get("airbyte_type", None) (maybe?)
                    fields.append(TimestampFieldSchema(
                        name=property_name,
                        nullable=nullable
                    ))
                else:
                    # TODO(jcrowson): includes time. Makes sense?
                    fields.append(StringFieldSchema(
                        name=property_name,
                        nullable=nullable
                    ))

            elif ab_field_type == "boolean":
                fields.append(BooleanFieldSchema(
                    name=property_name,
                    nullable=nullable,
                ))

            elif ab_field_type == "integer":
                fields.append(IntegerFieldSchema(
                    name=property_name,
                    nullable=nullable,
                ))

            elif ab_field_type == "number":
                number_subtype = property_schema.get("airbyte_type", None)

                if number_subtype == "integer":
                    fields.append(IntegerFieldSchema(
                        name=property_name,
                        nullable=nullable,
                    ))
                else:
                    fields.append(DoubleFieldSchema(
                        name=property_name,
                        nullable=nullable
                    ))
            elif ab_field_type == "array":
                array_subtype = helper(property_schema.get("items", {}), property_name)  # broken
                fields.append(ArrayFieldSchema(
                    name=property_name,
                    nullable=nullable,
                    arraySubtype=array_subtype
                ))

            elif ab_field_type == "object":
                # if additional props, probably make map
                pass

            elif ab_field_type == "oneOf":
                # for json
                fields.append(StringFieldSchema(
                    name=property_name,
                    nullable=nullable
                ))

        return fields

    return FoundrySchema(
        fieldSchemaList=helper(ab_json_schema),
        dataFrameReaderClass=STREAM_DATA_FRAME_READER_CLASS,
        customMetadata={
            "streaming": {
                "type": "avro"
            },
            "format": "avro"
        }
    )
