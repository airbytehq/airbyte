from destination_palantir_foundry.writer.writer import Writer
from destination_palantir_foundry.writer.foundry_streams.unbuffered_foundry_stream_writer import UnbufferedFoundryStreamWriter
from destination_palantir_foundry.foundry_api.compass import CompassFactory
from destination_palantir_foundry.foundry_api.stream_catalog import StreamCatalogFactory
from destination_palantir_foundry.foundry_api.stream_proxy import StreamProxyFactory
from destination_palantir_foundry.config.foundry_config import FoundryConfig
from destination_palantir_foundry.foundry_api.foundry_auth import ConfidentialClientAuthFactory
from destination_palantir_foundry.writer.dataset_registry import DatasetRegistry


class WriterFactory:
    def __init__(self) -> None:
        self.compass_factory = CompassFactory()
        self.stream_catalog_factory = StreamCatalogFactory()
        self.stream_proxy_factory = StreamProxyFactory()

    def create(self, config: FoundryConfig) -> Writer:
        auth = ConfidentialClientAuthFactory().create(
            config, UnbufferedFoundryStreamWriter.SCOPES)
        return UnbufferedFoundryStreamWriter(
            self.compass_factory.create(config, auth),
            self.stream_catalog_factory.create(config, auth),
            self.stream_proxy_factory.create(config, auth),
            DatasetRegistry(),
            config.destination_config.project_rid
        )
