
from destination_snowflake_cortex.config import SnowflakeCortexConfig
from airbyte.caches import SnowflakeCache
from airbyte._processors.sql.snowflake import SnowflakeSqlProcessor
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog
from typing import Iterable
from airbyte.strategies import WriteStrategy

class SnowflakeCortexClient:

    def __init__(self, config: SnowflakeCortexConfig):
        if isinstance(config, dict):
            config = SnowflakeCortexConfig.parse_obj(config)
        self.account = config.account
        self.username = config.username
        self.password = config.password
        self.database = config.database
        self.warehouse = config.warehouse
        self.role = config.role
        cache = SnowflakeCache(account=self.account, username=self.username, password=self.password, database=self.database, warehouse=self.warehouse, role=self.role)
        self.processor = SnowflakeSqlProcessor(cache=cache)

    def check(self):
        # check database connection by getting the list of tables in the schema 
        self.processor._get_tables_list()


    def write(self, configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        

        # to-do: register all sources in the catalog
        self.processor.register_source(
            source_name="example_stream",
            incoming_source_catalog=configured_catalog,
            stream_names=["example_stream"],
        )
        self.processor.process_airbyte_messages(input_messages, WriteStrategy.OVERWRITE)
    

