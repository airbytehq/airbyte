from abc import ABC, abstractmethod
from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema
from airbyte_cdk.models.airbyte_protocol import AirbyteStream, AirbyteRecordMessage
from typing import Dict, Any


class StreamSchemaProvider(ABC):
    @abstractmethod
    def get_foundry_stream_schema(self, airbyte_stream: AirbyteStream) -> FoundrySchema:
        pass

    @abstractmethod
    def get_converted_record(self, airbyte_record: AirbyteRecordMessage) -> Dict[str, Any]:
        pass
