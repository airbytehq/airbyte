from airbyte_cdk.sources import Source
from airbyte_cdk.models import (
    ConnectorSpecification,
    AirbyteConnectionStatus,
    AirbyteCatalog,
    AirbyteStream,
    SyncMode,
    AirbyteRecordMessage,
)
import hdbcli.dbapi
import datetime

class SourceSapHana(Source):
    def spec(self, logger):
        return ConnectorSpecification(
            connectionSpecification={
                "type": "object",
                "required": [
                    "host",
                    "port",
                    "username",
                    "password",
                    "database"
                ],
                "properties": {
                    "host": {
                        "type": "string",
                        "description": "Hostname of the SAP HANA instance."
                    },
                    "port": {
                        "type": "integer",
                        "description": "Port number of the SAP HANA instance."
                    },
                    "username": {
                        "type": "string",
                        "description": "Username to connect to SAP HANA."
                    },
                    "password": {
                        "type": "string",
                        "description": "Password to connect to SAP HANA.",
                        "airbyte_secret": True
                    },
                    "database": {
                        "type": "string",
                        "description": "Name of the database to connect to."
                    }
                }
            }
        )

    def check(self, logger, config):
        host = config["host"]
        port = config["port"]
        username = config["username"]
        password = config["password"]
        database = config["database"]

        try:
            connection = hdbcli.dbapi.connect(
                address=host,
                port=port,
                user=username,
                password=password,
                databasename=database
            )
            connection.close()
            return AirbyteConnectionStatus(status="SUCCEEDED")
        except Exception as e:
            return AirbyteConnectionStatus(status="FAILED", message=f"Could not connect to SAP HANA: {e}")

    def discover(self, logger, config):
        host = config["host"]
        port = config["port"]
        username = config["username"]
        password = config["password"]
        database = config["database"]

        connection = None
        try:
            connection = hdbcli.dbapi.connect(
                address=host,
                port=port,
                user=username,
                password=password,
                databasename=database
            )
            logger.info("Successfully connected to SAP HANA for discovery.")

            cursor = connection.cursor()

            # Query to get schema_name, table_name, column_name, data_type_name, and primary key info
            # Using SYS.TABLE_COLUMNS for column details and joining with SYS.INDEX_COLUMNS and SYS.INDEXES for PK
            # This query assumes standard access to these system views.
            # Schemas like SYS, _SYS_REPO, _SYS_BI, _SYS_BIC, _SYS_RT, _SYS_XS should usually be excluded.
            query = """
            SELECT
                TC.SCHEMA_NAME,
                TC.TABLE_NAME,
                TC.COLUMN_NAME,
                TC.DATA_TYPE_NAME,
                TC.LENGTH,
                TC.SCALE,
                CASE WHEN IC.INDEX_NAME IS NOT NULL THEN TRUE ELSE FALSE END AS IS_PRIMARY_KEY
            FROM SYS.TABLE_COLUMNS TC
            LEFT JOIN (
                SELECT SCHEMA_NAME, TABLE_NAME, COLUMN_NAME, INDEX_NAME
                FROM SYS.INDEX_COLUMNS
            ) IC ON TC.SCHEMA_NAME = IC.SCHEMA_NAME AND TC.TABLE_NAME = IC.TABLE_NAME AND TC.COLUMN_NAME = IC.COLUMN_NAME
            LEFT JOIN (
                SELECT SCHEMA_NAME, INDEX_NAME
                FROM SYS.INDEXES
                WHERE CONSTRAINT = 'PRIMARY KEY'
            ) IDX ON IC.SCHEMA_NAME = IDX.SCHEMA_NAME AND IC.INDEX_NAME = IDX.INDEX_NAME
            WHERE TC.SCHEMA_NAME NOT IN ('SYS', '_SYS_REPO', '_SYS_BI', '_SYS_BIC', '_SYS_RT', '_SYS_XS', 'SAP_PA_APL')
            ORDER BY TC.SCHEMA_NAME, TC.TABLE_NAME, TC.POSITION;
            """

            logger.info(f"Executing query for schema discovery: {query}")
            cursor.execute(query)

            streams = []
            current_table_id = None
            stream_properties = {}
            primary_keys = []

            # Basic SAP HANA to JSON Schema type mapping
            # This is a simplified mapping and might need to be expanded.
            # NCHAR, NVARCHAR, VARCHAR, CHAR -> string
            # SMALLINT, INTEGER, BIGINT, TINYINT -> integer
            # DECIMAL, REAL, DOUBLE, FLOAT -> number
            # DATE, TIMESTAMP, SECONDDATE -> string (with format)
            # BOOLEAN -> boolean
            # BLOB, CLOB, NCLOB, TEXT -> string
            # VARBINARY -> string (base64 encoded) - not directly supported by JSON schema types, often mapped to string
            type_mapping = {
                "NVARCHAR": {"type": "string"}, "VARCHAR": {"type": "string"}, "CHAR": {"type": "string"}, "NCHAR": {"type": "string"},
                "SMALLINT": {"type": "integer"}, "INTEGER": {"type": "integer"}, "BIGINT": {"type": "integer"}, "TINYINT": {"type": "integer"},
                "DECIMAL": {"type": "number"}, "REAL": {"type": "number"}, "DOUBLE": {"type": "number"}, "FLOAT": {"type": "number"},
                "DATE": {"type": "string", "format": "date"}, "TIMESTAMP": {"type": "string", "format": "date-time"},
                "SECONDDATE": {"type": "string", "format": "date-time"}, #  SAP specific, similar to TIMESTAMP
                "BOOLEAN": {"type": "boolean"},
                "BLOB": {"type": "string"}, "CLOB": {"type": "string"}, "NCLOB": {"type": "string"}, "TEXT": {"type": "string"},
                "VARBINARY": {"type": "string"}, # Or handle as object with content encoding
                # Add more types as needed: ST_GEOMETRY, ALPHANUM, SMALLDECIMAL, etc.
            }

            for row in cursor:
                schema_name, table_name, column_name, data_type_name, length, scale, is_pk = row
                table_id = f"{schema_name}.{table_name}"

                if table_id != current_table_id:
                    if current_table_id: # Finalize previous stream
                        streams.append(AirbyteStream(
                            name=current_table_id.split('.')[1], # Use table name as stream name
                            namespace=current_table_id.split('.')[0], # Use schema name as namespace
                            json_schema={"type": "object", "properties": stream_properties},
                            supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental], # Default, can be adjusted
                            source_defined_primary_key=[primary_keys] if primary_keys and primary_keys[0] else None # Corrected
                        ))
                    current_table_id = table_id
                    stream_properties = {}
                    primary_keys = []

                json_type = type_mapping.get(data_type_name.upper(), {"type": "string"}) # Default to string if type unknown
                stream_properties[column_name] = json_type
                if is_pk:
                    primary_keys.append(column_name)

            if current_table_id: # Finalize the last stream
                streams.append(AirbyteStream(
                    name=current_table_id.split('.')[1],
                    namespace=current_table_id.split('.')[0],
                    json_schema={"type": "object", "properties": stream_properties},
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                    source_defined_primary_key=[primary_keys] if primary_keys and primary_keys[0] else None # Corrected
                ))

            cursor.close()
            return AirbyteCatalog(streams=streams)

        except Exception as e:
            logger.error(f"Error during SAP HANA discovery: {e}")
            # It's better to raise the exception or return an empty catalog with an error message if the CDK supports it.
            # For now, re-raising to make it clear something went wrong.
            raise
        finally:
            if connection:
                connection.close()
                logger.info("SAP HANA connection closed.")

    def read(self, logger, config, catalog, state=None):
        host = config["host"]
        port = config["port"]
        username = config["username"]
        password = config["password"]
        database = config["database"]

        connection = None
        try:
            connection = hdbcli.dbapi.connect(
                address=host,
                port=port,
                user=username,
                password=password,
                databasename=database
            )
            logger.info("Successfully connected to SAP HANA for reading data.")
            cursor = connection.cursor()

            for configured_stream in catalog.streams:
                stream_name = configured_stream.stream.name
                namespace = configured_stream.stream.namespace
                logger.info(f"Starting to read stream: {namespace}.{stream_name}")

                # Construct SELECT query
                # Ensure table and schema names are properly quoted to handle special characters or case sensitivity if necessary
                # For HANA, standard SQL quoting is double quotes.
                query = f'SELECT * FROM "{namespace}"."{stream_name}"'

                try:
                    logger.info(f"Executing query for stream {namespace}.{stream_name}: {query}")
                    cursor.execute(query)

                    col_names = [desc[0] for desc in cursor.description]

                    row = cursor.fetchone()
                    while row:
                        data = dict(zip(col_names, row))
                        yield AirbyteRecordMessage(
                            stream=stream_name,
                            data=data,
                            emitted_at=int(datetime.datetime.now().timestamp()) * 1000
                        )
                        row = cursor.fetchone()
                    logger.info(f"Finished reading stream: {namespace}.{stream_name}")
                except Exception as e:
                    logger.error(f"Error reading stream {namespace}.{stream_name}: {e}")
                    # Decide if to raise, or skip and continue with other streams.
                    # For now, logging and continuing.
                    # Consider emitting an AirbyteLogMessage as well.
                    pass # Or raise e if one stream failure should stop the sync

            cursor.close()

        except Exception as e:
            logger.error(f"Error during SAP HANA read operation: {e}")
            raise # Main connection or setup error should be raised
        finally:
            if connection:
                connection.close()
                logger.info("SAP HANA connection closed after reading.")
