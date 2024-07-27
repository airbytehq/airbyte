from destination_palantir_foundry.config.foundry_config import FoundryConfig
from destination_palantir_foundry.foundry_api.foundry_auth import ConfidentialClientAuthFactory
from destination_palantir_foundry.foundry_api.service_factory import FoundryServiceFactory
from destination_palantir_foundry.foundry_schema.providers.streams.stream_schema_provider_factory import \
    StreamSchemaProviderFactory
from destination_palantir_foundry.utils.project_helper import ProjectHelper
from destination_palantir_foundry.writer.foundry_streams.foundry_stream_buffer_registry import \
    FoundryStreamBufferRegistry
from destination_palantir_foundry.writer.foundry_streams.foundry_stream_writer import FoundryStreamWriter
from destination_palantir_foundry.writer.writer import Writer


def create_writer(config: FoundryConfig) -> Writer:
    auth = ConfidentialClientAuthFactory().create(
        config, FoundryStreamWriter.SCOPES)
    auth.sign_in_as_service_user()

    service_factory = FoundryServiceFactory(config.host, auth)

    return FoundryStreamWriter(
        ProjectHelper(service_factory.compass()),
        service_factory.stream_catalog(),
        service_factory.stream_proxy(),
        service_factory.foundry_metadata(),
        FoundryStreamBufferRegistry(),
        StreamSchemaProviderFactory().create(),
        config.destination_config.project_rid
    )
