import json
from typing import Dict, Any

from airbyte_cdk.models.airbyte_protocol import AirbyteStream, AirbyteRecordMessage

from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema, TimestampFieldSchema, \
    StringFieldSchema
from destination_palantir_foundry.foundry_schema.providers.stream_schema_provider import StreamSchemaProvider
from destination_palantir_foundry.foundry_schema.providers.streams.common import STREAM_DATA_FRAME_READER_CLASS


class BasicStreamSchemaProvider(StreamSchemaProvider):
    """
    Always returns schema of type:
    {
        "emittedAt": TIMESTAMP,
        "message": '{ full raw message json }'
    }
    """

    def get_foundry_stream_schema(self, _airbyte_stream: AirbyteStream) -> FoundrySchema:
        # TODO(jcrowson): add generation id
        return FoundrySchema(
            fieldSchemaList=[
                TimestampFieldSchema(
                    name="emittedAt",
                    nullable=False,
                ),
                StringFieldSchema(
                    name="message",
                    nullable=False,
                )
            ],
            dataFrameReaderClass=STREAM_DATA_FRAME_READER_CLASS,
            customMetadata={
                "format": "avro",
                "streaming": {
                    "type": "avro"
                }
            }
        )

    def get_converted_record(
            self,
            airbyte_record: AirbyteRecordMessage,
            _foundry_schema: FoundrySchema,
            _generation_id: int
    ) -> Dict[str, Any]:
        return {
            "emittedAt": airbyte_record.emitted_at,
            "message": json.dumps(airbyte_record.data),
        }
