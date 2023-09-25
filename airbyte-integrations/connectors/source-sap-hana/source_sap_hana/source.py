from typing import Any, List, Mapping, Tuple

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from hdbcli import dbapi
from hdbcli.dbapi import Connection as SAPHanaConnection, Cursor as SAPHanaCursor


from .stream import SAPHanaStream
from typing import Any, List, Mapping, Tuple

from .const import SAPHANA_TO_JSONSCHEMA_DATATYPE

class SourceSapHana(AbstractSource):
    def get_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> SAPHanaConnection:
        return dbapi.connect(address=config["host"], port=config["port"], user=config["username"], password=config["password"])

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            conn = self.get_connection(logger, config)
            return conn.isconnected(), None
        except Exception as e:
            return False, e
    
    def get_operational_schemas(self, logger: AirbyteLogger, cursor: SAPHanaCursor) -> List[str]:
        INTERNAL_SCHEMAS = ("SYS", "_SYS_BIC", "_SYS_TASK", "_SYS_BI")

        query = f"SELECT DISTINCT schema_name FROM tables WHERE schema_name NOT IN {INTERNAL_SCHEMAS}"

        cursor.execute(query)

        return [row[0] for row in cursor.fetchall()]

    def get_tables(self, logger: AirbyteLogger, cursor: SAPHanaCursor, discover_tables: List[str]) -> List[str]:
        params = []
        schemas = self.get_operational_schemas(logger, cursor)

        query = f"""
        SELECT
            schema_name||'.'||table_name 
        FROM tables 
        WHERE schema_name IN ({', '.join('?' for _ in schemas)})
            AND table_name IN ({', '.join('?' for _ in discover_tables)})
        """

        params.extend(schemas)
        params.extend(discover_tables)

        cursor.execute(query, params)

        return [row[0] for row in cursor.fetchall()]

    def generate_table_schema(self, logger: AirbyteLogger, cursor: SAPHanaCursor, table_path: str) -> dict:
        schema_name, table_name = table_path.split(".")

        query = f"""
            SELECT
                COLUMN_NAME,
                DATA_TYPE_NAME
            FROM TABLE_COLUMNS 
            WHERE schema_name = '{schema_name}'
             AND table_name = '{table_name}'"""

        cursor.execute(query)
        data = cursor.fetchall()

        properties = {row[0] : {"type" : [SAPHANA_TO_JSONSCHEMA_DATATYPE.get(row[1], "string"), "null"]} for row in data}

        return {"type": "object", "additionalProperties": True, "properties": properties}
    
    def get_primary_keys(self, cursor: SAPHanaCursor) -> Mapping[str, List[str]]:
        
        schemas = self.get_operational_schemas(None, cursor)
        query = f"""
            SELECT 
                schema_name||'.'||table_name,
                column_name
            FROM constraints
            WHERE is_primary_key = 'TRUE' 
                AND schema_name IN ({', '.join('?' for _ in schemas)})"""
        
        cursor.execute(query, schemas)
        r = cursor.fetchall()

        tables = set([row[0] for row in r])

        return {table:[row[1] for row in r if row[0] == table] for table in tables}

    def build_streams(self, logger: AirbyteLogger, cursor: SAPHanaCursor, discover_tables: List[str]) -> List[Stream]:
        streams = []
        for table_path in self.get_tables(logger, cursor, discover_tables):

            schema, table = table_path.split('.')

            stream_name = f'{schema}.{table}'
            # namespace = schema
            json_schema = self.generate_table_schema(logger, cursor, table_path)

            streams.append(
                SAPHanaStream(stream_name=stream_name, json_schema=json_schema, records_per_slice=None, config= None)
            )
        
        primary_keys = self.get_primary_keys(cursor=cursor)
        for stream in streams:
            stream.primary_key = primary_keys.get(stream.stream_name)

        return streams

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        records_per_slice: int = config["records_per_slice"] if "records_per_slice" in config else 20000

        conn = self.get_connection(logger=None, config=config)
        cursor = conn.cursor()

        streams = self.build_streams(logger=None, cursor=cursor, discover_tables=config['discover_tables'])

        for stream in streams:
            stream.config = config
            stream.records_per_slice = records_per_slice

        return streams