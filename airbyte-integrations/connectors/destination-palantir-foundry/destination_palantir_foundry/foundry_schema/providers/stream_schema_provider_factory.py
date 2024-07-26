from destination_palantir_foundry.foundry_schema.providers.stream_schema_provider import StreamSchemaProvider
from destination_palantir_foundry.foundry_schema.providers.streams.structured_stream_schema_provider import StructuredStreamSchemaProvider


class StreamSchemaProviderFactory:
    def create(self) -> StreamSchemaProvider:
        return StructuredStreamSchemaProvider()
