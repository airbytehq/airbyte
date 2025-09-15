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

from destination_opengauss_datavec import opengauss_processor
from destination_opengauss_datavec.config import ConfigModel
from destination_opengauss_datavec.common.catalog.catalog_providers import CatalogProvider


BATCH_SIZE = 150


class DestinationOpenGaussDataVec(Destination):
    sql_processor: opengauss_processor.OpenGaussDataVecProcessor

    def _init_sql_processor(
        self, config: ConfigModel, configured_catalog: Optional[ConfiguredAirbyteCatalog] = None
    ) -> None:
        self.sql_processor = opengauss_processor.OpenGaussDataVecProcessor(
            sql_config=opengauss_processor.OpenGaussConfig(
                host=config.indexing.host,
                port=config.indexing.port,
                database=config.indexing.database,
                schema_name=config.indexing.default_schema,
                username=config.indexing.username,
                password=SecretString(config.indexing.password),
            ),
            splitter_config=config.processing,
            embedder_config=config.embedding,  # type: ignore [arg-type]
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
            self.sql_processor.sql_config.get_sql_engine().connect()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(
                status=Status.FAILED, message=f"An exception occurred: {repr(e)}"
            )

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/destinations/opengauss-datavec",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.overwrite, DestinationSyncMode.append, DestinationSyncMode.append_dedup],
            connectionSpecification=ConfigModel.schema(),  # type: ignore[attr-defined]
        )
