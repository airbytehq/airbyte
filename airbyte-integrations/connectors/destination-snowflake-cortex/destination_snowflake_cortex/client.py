
from destination_snowflake_cortex.config import SnowflakeCortexConfig
from airbyte.caches import SnowflakeCache

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
        # initialize the destination cache with default schema "airbyte_raw"
        self.destination = SnowflakeCache(account=self.account, username=self.username, password=self.password, database=self.database, warehouse=self.warehouse, role=self.role)

    def check(self):
        # check database connection by getting the list of tables in the schema 
        self.destination.processor._get_tables_list()

    