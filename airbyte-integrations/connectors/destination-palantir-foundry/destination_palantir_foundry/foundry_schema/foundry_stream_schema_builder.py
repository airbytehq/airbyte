from typing import List, Dict

from destination_palantir_foundry.foundry_schema.foundry_schema import FoundryFieldSchema, FoundryFieldType, \
    FoundrySchema, BinaryFieldSchema, ByteFieldSchema, ArrayFieldSchema
from destination_palantir_foundry.foundry_schema.providers.streams.common import STREAM_DATA_FRAME_READER_CLASS


def _get_field_custom_metadata(is_key: bool) -> Dict:
    if is_key:
        return {"includeInPartitioning": True}
    else:
        return {}


class FoundryStreamSchemaBuilder:
    def __init__(self, schema):
        self.field_schemas: List[FoundryFieldSchema] = []

    def add_array_field(self, name: str, nullable: bool, is_key: bool, sub_type: FoundryFieldSchema) -> 'FoundryStreamSchemaBuilder':
        self.field_schemas.append(ArrayFieldSchema(
            name=name,
            nullable=nullable,
            custom_metadata=_get_field_custom_metadata(is_key),
            arraySubtype=sub_type
        ))
        return self

    def add_binary_field(self, name: str, nullable: bool, is_key: bool) -> 'FoundryStreamSchemaBuilder':
        self.field_schemas.append(BinaryFieldSchema(
            name=name,
            nullable=nullable,
            custom_metadata=_get_field_custom_metadata(is_key)
        ))
        return self

    def add_byte_field(self, name: str, nullable: bool, is_key: bool) -> 'FoundryStreamSchemaBuilder':
        self.field_schemas.append(ByteFieldSchema(
            name=name,
            nullable=nullable,
            custom_metadata=_get_field_custom_metadata(is_key)
        ))
        return self

    def add_date_field(self, name: str, nullable: bool, is_key: bool) -> 'FoundryStreamSchemaBuilder':
        self.field_schemas.append(FoundryFieldSchema(type=FoundryFieldType.DATE, name=name, nullable=nullable,
                                                     custom_metadata=_get_field_custom_metadata(is_key)))
        return self

    def add_decimal_field(self) -> 'FoundryStreamSchemaBuilder':
        raise NotImplementedError()

    def add_double_field(self, name: str, nullable: bool, is_key: bool) -> 'FoundryStreamSchemaBuilder':
        self.field_schemas.append(FoundryFieldSchema(type=FoundryFieldType.DOUBLE, name=name, nullable=nullable,
                                                     custom_metadata=_get_field_custom_metadata(is_key)))
        return self

    def add_float_field(self, name: str, nullable: bool, is_key: bool) -> 'FoundryStreamSchemaBuilder':
        self.field_schemas.append(FoundryFieldSchema(type=FoundryFieldType.FLOAT, name=name, nullable=nullable,
                                                     custom_metadata=_get_field_custom_metadata(is_key)))
        return self

    def add_integer_field(self, name: str, nullable: bool, is_key: bool) -> 'FoundryStreamSchemaBuilder':
        self.field_schemas.append(FoundryFieldSchema(type=FoundryFieldType.INTEGER, name=name, nullable=nullable,
                                                     custom_metadata=_get_field_custom_metadata(is_key)))
        return self

    def add_long_field(self, name: str, nullable: bool, is_key: bool) -> 'FoundryStreamSchemaBuilder':
        self.field_schemas.append(FoundryFieldSchema(type=FoundryFieldType.LONG, name=name, nullable=nullable,
                                                     custom_metadata=_get_field_custom_metadata(is_key)))
        return self

    def add_map_field(self) -> 'FoundryStreamSchemaBuilder':
        raise NotImplementedError()

    def add_short_field(self, name: str, nullable: bool, is_key: bool) -> 'FoundryStreamSchemaBuilder':
        self.field_schemas.append(FoundryFieldSchema(type=FoundryFieldType.SHORT, name=name, nullable=nullable,
                                                     custom_metadata=_get_field_custom_metadata(is_key)))
        return self

    def add_string_field(self, name: str, nullable: bool, is_key: bool) -> 'FoundryStreamSchemaBuilder':
        self.field_schemas.append(FoundryFieldSchema(type=FoundryFieldType.STRING, name=name, nullable=nullable,
                                                     custom_metadata=_get_field_custom_metadata(is_key)))
        return self

    def add_struct_field(self) -> 'FoundryStreamSchemaBuilder':
        raise NotImplementedError()

    def add_timestamp_field(self, name: str, nullable: bool, is_key: bool) -> 'FoundryStreamSchemaBuilder':
        self.field_schemas.append(FoundryFieldSchema(type=FoundryFieldType.TIMESTAMP, name=name, nullable=nullable,
                                                     custom_metadata=_get_field_custom_metadata(is_key)))
        return self

    def build(self):
        return FoundrySchema(
            fieldSchemaList=self.field_schemas,
            dataFrameReaderClass=STREAM_DATA_FRAME_READER_CLASS,
            customMetadata={
                "streaming": {
                    "type": "avro"
                },
                "format": "avro"
            }
        )
