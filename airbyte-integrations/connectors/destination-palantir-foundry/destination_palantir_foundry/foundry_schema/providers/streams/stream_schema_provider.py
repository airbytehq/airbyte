from abc import ABC, abstractmethod
from typing import Dict, Any

from airbyte_cdk.models.airbyte_protocol import AirbyteStream, AirbyteRecordMessage

from destination_palantir_foundry.foundry_schema.foundry_schema import FoundrySchema


class StreamSchemaProvider(ABC):
    @abstractmethod
    def get_foundry_stream_schema(self, airbyte_stream: AirbyteStream) -> FoundrySchema:
        pass

    @abstractmethod
    def get_converted_record(
            self,
            airbyte_record: AirbyteRecordMessage,
            foundry_schema: FoundrySchema,
    ) -> Dict[str, Any]:
        pass
