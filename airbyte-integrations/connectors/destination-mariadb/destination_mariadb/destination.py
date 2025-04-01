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
    Type,
)

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
        parsed_config = ConfigModel.parse_obj(config)
        self._init_sql_processor(config=parsed_config, configured_catalog=configured_catalog)

        """
        TODO
        Reads the input stream of messages, config, and catalog to write data to the destination.

        This method returns an iterable (typically a generator of AirbyteMessages via yield) containing state messages received
        in the input message stream. Outputting a state message means that every AirbyteRecordMessage which came before it has been
        successfully persisted to the destination. This is used to ensure fault tolerance in the case that a sync fails before fully completing,
        then the source is given the last state message output from this method as the starting point of the next sync.

        :param config: dict of JSON configuration matching the configuration declared in spec.json
        :param configured_catalog: The Configured Catalog describing the schema of the data being received and how it should be persisted in the
                                    destination
        :param input_messages: The stream of input messages received from the source
        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """
        # So basically, if it's a record, process it as such. If it's a state, yield it back out


        for msg in input_messages:
            if msg.type is Type.RECORD:

                pass
            elif msg.type is Type.STATE:
                yield cast(AirbyteStateMessage, msg)
            else:
                pass

            yield self.sql_processor.process_record_message(
                msg,
                write_strategy=WriteStrategy.AUTO,
            )

        """
        yield from self.sql_processor.process_airbyte_messages_as_generator(
            messages=input_messages,
            write_strategy=WriteStrategy.AUTO,
        )
        """

    def check(self, logger: Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        _ = logger  # Unused

        # pydevd_pycharm.settrace('192.168.178.27', port=55507, stdoutToServer=True, stderrToServer=True)

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
            documentationUrl="https://docs.airbyte.com/integrations/destinations/mariadb", # TODO something
            supportsIncremental=True,
            supported_destination_sync_modes=[
                DestinationSyncMode.overwrite,
                DestinationSyncMode.append,
                DestinationSyncMode.append_dedup,
            ],
            connectionSpecification=ConfigModel.schema(),  # type: ignore[attr-defined]
        )
