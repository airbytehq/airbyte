from destination_palantir_foundry.foundry_schema.providers.stream_schema_provider import StreamSchemaProvider
from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema, FoundryFieldSchema, FoundryFieldType
from destination_palantir_foundry.foundry_schema.providers.streams.common import DATA_FRAME_READER_CLASS
from typing import Dict, Any
from airbyte_cdk.models.airbyte_protocol import AirbyteStream, AirbyteRecordMessage
import json


class BasicStreamSchemaProvider(StreamSchemaProvider):
    """
    Always returns schema of type:
    {
        "emittedAt": TIMESTAMP,
        "message": '{ full raw message json }'
    }
    """

    def get_foundry_stream_schema(self, _airbyte_stream: AirbyteStream) -> FoundrySchema:
        return FoundrySchema(
            fieldSchemaList=[
                FoundryFieldSchema(
                    type=FoundryFieldType.TIMESTAMP,
                    name="emittedAt",
                    nullable=False,
                    customMetadata={}
                ),
                FoundryFieldSchema(
                    type=FoundryFieldType.STRING,
                    name="message",
                    nullable=False,
                    customMetadata={}
                )
            ],
            dataFrameReaderClass=DATA_FRAME_READER_CLASS,
            customMetadata={
                "format": "avro",
                "streaming": {
                    "type": "avro"
                }
            }
        )

    def get_converted_record(self, airbyte_record: AirbyteRecordMessage) -> Dict[str, Any]:
        return {
            "emittedAt": airbyte_record.emitted_at,
            "message": json.dumps(airbyte_record.data),
        }
