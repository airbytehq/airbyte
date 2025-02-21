#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import tempfile
from logging import Logger
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

from airbyte.secrets import SecretString
from airbyte.strategies import WriteStrategy
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    DestinationSyncMode,
    Status,
)

from destination_pgvector import pgvector_processor
from destination_pgvector.common.catalog.catalog_providers import CatalogProvider
from destination_pgvector.config import ConfigModel

BATCH_SIZE = 150


class DestinationPGVector(Destination):
    sql_processor: pgvector_processor.PGVectorProcessor

    def _init_sql_processor(
        self, config: ConfigModel, configured_catalog: Optional[ConfiguredAirbyteCatalog] = None
    ) -> None:
        self.sql_processor = pgvector_processor.PGVectorProcessor(
            sql_config=pgvector_processor.PostgresConfig(
                host=config.indexing.host,
                port=config.indexing.port,
                database=config.indexing.database,
                schema_name=config.indexing.default_schema,
                username=config.indexing.username,
                password=SecretString(config.indexing.credentials.password),
            ),
            splitter_config=config.processing,
            embedder_config=config.embedding,  # type: ignore [arg-type]  # No common base class
            catalog_provider=CatalogProvider(configured_catalog),
            temp_dir=Path(tempfile.mkdtemp()),
            temp_file_cleanup=True,
        )

    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        parsed_config = ConfigModel.parse_obj(config)
        self._init_sql_processor(config=parsed_config, configured_catalog=configured_catalog)
        yield from self.sql_processor.process_airbyte_messages_as_generator(
            messages=input_messages,
            write_strategy=WriteStrategy.AUTO,
        )

    def check(self, logger: Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        _ = logger  # Unused
        try:
            parsed_config = ConfigModel.parse_obj(config)
            self._init_sql_processor(config=parsed_config)
            self.sql_processor.sql_config.connect()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(
                status=Status.FAILED, message=f"An exception occurred: {repr(e)}"
            )

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/destinations/pgvector",
            supportsIncremental=True,
            supported_destination_sync_modes=[
                DestinationSyncMode.overwrite,
                DestinationSyncMode.append,
                DestinationSyncMode.append_dedup,
            ],
            connectionSpecification=ConfigModel.schema(),  # type: ignore[attr-defined]
        )
