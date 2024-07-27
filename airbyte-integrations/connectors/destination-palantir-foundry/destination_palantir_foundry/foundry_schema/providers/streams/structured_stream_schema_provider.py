from typing import Dict, Any

from airbyte_cdk.models.airbyte_protocol import AirbyteStream, AirbyteRecordMessage

from destination_palantir_foundry.foundry_schema.converters.airbyte_record_converter import convert_ab_record
from destination_palantir_foundry.foundry_schema.converters.streams.airbyte_to_stream_schema import \
    convert_ab_to_foundry_stream_schema
from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema, TimestampFieldSchema
from destination_palantir_foundry.foundry_schema.providers.streams.stream_schema_provider import StreamSchemaProvider


class StructuredStreamSchemaProvider(StreamSchemaProvider):
    """
    Always returns schema of type:
    {
        "_ab_emittedAt": TIMESTAMP,
        "message": '{ full raw message json }'
    }
    """

    def get_foundry_stream_schema(self, airbyte_stream: AirbyteStream) -> FoundrySchema:
        foundry_schema = convert_ab_to_foundry_stream_schema(airbyte_stream.json_schema)

        metadata_fields = [
            TimestampFieldSchema(
                name="_ab_emittedAt",
                nullable=False,
            )
        ]

        foundry_schema.fieldSchemaList = [*metadata_fields, *foundry_schema.fieldSchemaList]

        return foundry_schema

    def get_converted_record(
            self,
            airbyte_record: AirbyteRecordMessage,
            foundry_schema: FoundrySchema,
    ) -> Dict[str, Any]:
        return {
            "_ab_emittedAt": airbyte_record.emitted_at,
            **convert_ab_record(airbyte_record.data, foundry_schema)
        }
