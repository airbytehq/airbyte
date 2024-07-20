from destination_palantir_foundry.foundry_schema.providers.stream_schema_provider import StreamSchemaProvider
from destination_palantir_foundry.foundry_schema.providers.streams.basic_stream_schema_provider import BasicStreamSchemaProvider


class StreamSchemaProviderFactory:
    def create(self) -> StreamSchemaProvider:
        return BasicStreamSchemaProvider()
