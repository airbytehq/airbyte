#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import tempfile
from logging import Logger
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

import pydevd_pycharm
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
    Type,
)

import logging
logger = logging.getLogger("airbyte")

from destination_mariadb import mariadb_processor
from destination_mariadb.common.catalog.catalog_providers import CatalogProvider
from destination_mariadb.config import ConfigModel
# import pydevd_pycharm
BATCH_SIZE = 150


class DestinationMariaDB(Destination):
    sql_processor: mariadb_processor.MariaDBProcessor

    def _init_sql_processor(
        self, config: ConfigModel, configured_catalog: Optional[ConfiguredAirbyteCatalog] = None
    ) -> None:
        self.sql_processor = mariadb_processor.MariaDBProcessor(
            sql_config=mariadb_processor.DatabaseConfig(
                host=config.indexing.host,
                port=config.indexing.port,
                database=config.indexing.database,
                # schema_name=config.indexing.default_schema,
                username=config.indexing.username,
                password=SecretString(config.indexing.credentials.password),
            ),
            splitter_config=config.processing,
            embedder_config=config.embedding,  # type: ignore [arg-type]  # No common base class
            catalog_provider=CatalogProvider(configured_catalog),
            #temp_dir=Path(tempfile.mkdtemp()),
            #temp_file_cleanup=True,
        )



    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        #pydevd_pycharm.settrace('192.168.178.27', port=55507, stdoutToServer=True, stderrToServer=True)
        logger.info("Write starting up")
        parsed_config = ConfigModel.parse_obj(config)
        self._init_sql_processor(config=parsed_config, configured_catalog=configured_catalog)
        try:
            logger.info("Before the yield from call")
            yield from self.sql_processor.process_airbyte_messages_as_generator(
                input_messages=input_messages,
                write_strategy=WriteStrategy.AUTO,
            )
        except Exception as e:
            raise e

        logger.info("After this, I should terminate")


    def check(self, logger: Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        _ = logger  # Unused

        #pydevd_pycharm.settrace('192.168.178.27', port=55507, stdoutToServer=True, stderrToServer=True)

        try:
            parsed_config = ConfigModel.parse_obj(config)
            self._init_sql_processor(config=parsed_config)
            foo = self.sql_processor.sql_config.get_sql_engine().connect()
            foo.close()
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(
                status=Status.FAILED, message=f"An exception occurred: {repr(e)}"
            )

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/destinations/mariadb", # TODO something
            supportsIncremental=True,
            supported_destination_sync_modes=[
                DestinationSyncMode.overwrite,
                DestinationSyncMode.append,
                DestinationSyncMode.append_dedup,
            ],
            connectionSpecification=ConfigModel.schema(),  # type: ignore[attr-defined]
        )
