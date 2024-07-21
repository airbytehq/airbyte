from typing import Dict, Any

from airbyte_cdk.models.airbyte_protocol import AirbyteStream, AirbyteRecordMessage

from destination_palantir_foundry.foundry_schema.airbyte_schema_converter import convert_ab_to_foundry_stream_schema
from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema, TimestampFieldSchema
from destination_palantir_foundry.foundry_schema.providers.stream_schema_provider import StreamSchemaProvider


class StructuredStreamSchemaProvider(StreamSchemaProvider):
    """
    Always returns schema of type:
    {
        "_airbyte_emittedAt": TIMESTAMP,
        "message": '{ full raw message json }'
    }
    """

    def get_foundry_stream_schema(self, airbyte_stream: AirbyteStream) -> FoundrySchema:
        foundry_schema = convert_ab_to_foundry_stream_schema(airbyte_stream.json_schema)

        foundry_schema.fieldSchemaList.append(TimestampFieldSchema(
            name="_airbyte_emittedAt",
            nullable=False,
        ))

        return foundry_schema

    def get_converted_record(self, airbyte_record: AirbyteRecordMessage) -> Dict[str, Any]:
        return {
            "_airbyte_emittedAt": airbyte_record.emitted_at,
            **airbyte_record.data
        }
