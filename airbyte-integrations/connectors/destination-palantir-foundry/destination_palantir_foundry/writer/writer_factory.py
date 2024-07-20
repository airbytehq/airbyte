from destination_palantir_foundry.writer.writer import Writer
from destination_palantir_foundry.writer.foundry_streams.foundry_stream_writer import FoundryStreamWriter
from destination_palantir_foundry.foundry_api.service_factory import FoundryServiceFactory
from destination_palantir_foundry.config.foundry_config import FoundryConfig
from destination_palantir_foundry.foundry_api.foundry_auth import ConfidentialClientAuthFactory
from destination_palantir_foundry.writer.foundry_streams.foundry_stream_buffer_registry import FoundryStreamBufferRegistry


class WriterFactory:
    def create(self, config: FoundryConfig) -> Writer:
        auth = ConfidentialClientAuthFactory().create(
            config, FoundryStreamWriter.SCOPES)

        service_factory = FoundryServiceFactory(config.host, auth)

        return FoundryStreamWriter(
            service_factory.compass(),
            service_factory.stream_catalog(),
            service_factory.stream_proxy(),
            service_factory.foundry_metadata(),
            FoundryStreamBufferRegistry(),
            self.stream_schema_provider_factory.create(),
            config.destination_config.project_rid
        )
