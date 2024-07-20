from destination_palantir_foundry.writer.writer import Writer
from destination_palantir_foundry.writer.foundry_streams.unbuffered_foundry_stream_writer import UnbufferedFoundryStreamWriter
from destination_palantir_foundry.foundry_api.service_factory import FoundryServiceFactory
from destination_palantir_foundry.config.foundry_config import FoundryConfig
from destination_palantir_foundry.foundry_api.foundry_auth import ConfidentialClientAuthFactory
from destination_palantir_foundry.writer.dataset_registry import DatasetRegistry
from destination_palantir_foundry.foundry_schema.providers.stream_schema_provider_factory import StreamSchemaProviderFactory


class WriterFactory:
    def create(self, config: FoundryConfig) -> Writer:
        auth = ConfidentialClientAuthFactory().create(
            config, UnbufferedFoundryStreamWriter.SCOPES)

        service_factory = FoundryServiceFactory(config.host, auth)

        return UnbufferedFoundryStreamWriter(
            service_factory.compass(),
            service_factory.stream_catalog(),
            service_factory.stream_proxy(),
            service_factory.foundry_metadata(),
            DatasetRegistry(),
            self.stream_schema_provider_factory.create(),
            config.destination_config.project_rid
        )
