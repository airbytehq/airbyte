# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import csv
import datetime
import json
import ssl
import time
import uuid
from collections import defaultdict
from io import StringIO
from logging import getLogger
from typing import Any, Dict, Iterable, List
from urllib.parse import quote

import requests
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, DestinationSyncMode, Type
from destination_starrocks.config import StarRocksConfig


logger = getLogger("airbyte")


def _coerce(value: Any, sql_type: str) -> Any:
    """Coerce a Python value to a type appropriate for its StarRocks SQL column type."""
    if value is None:
        return None
    if sql_type == "JSON":
        return json.dumps(value) if isinstance(value, (dict, list)) else value
    if sql_type in ("BIGINT", "LARGEINT", "DOUBLE") or sql_type.startswith("DECIMAL"):
        return value
    if sql_type == "BOOLEAN":
        return value
    return str(value)


class StarRocksTypeMapper:
    """Maps Airbyte JSON Schema types to StarRocks column types."""

    TYPE_MAP = {
        "string": "STRING",
        "number": "DOUBLE",
        "integer": "BIGINT",
        "boolean": "BOOLEAN",
        "array": "JSON",
        "object": "JSON",
    }

    FORMAT_MAP = {
        "date": "DATE",
        "date-time": "DATETIME",
        "time": "STRING",
    }

    @classmethod
    def get_sql_type(cls, json_schema: Dict[str, Any]) -> str:
        if "oneOf" in json_schema:
            for schema in json_schema["oneOf"]:
                if schema.get("type") != "null":
                    return cls.get_sql_type(schema)
            return "STRING"

        if "type" in json_schema:
            json_type = json_schema["type"]

            if isinstance(json_type, list):
                non_null_types = [t for t in json_type if t != "null"]
                json_type = non_null_types[0] if non_null_types else None
                if json_type is None:
                    return "STRING"

            if json_type == "string" and "format" in json_schema:
                if json_schema["format"] in cls.FORMAT_MAP:
                    return cls.FORMAT_MAP[json_schema["format"]]

            if "airbyte_type" in json_schema:
                airbyte_type = json_schema["airbyte_type"]
                if airbyte_type in ("timestamp_with_timezone", "timestamp_without_timezone"):
                    return "DATETIME"
                elif airbyte_type == "big_integer":
                    return "LARGEINT"
                elif airbyte_type == "big_number":
                    return "DECIMAL(38,9)"

            if json_type in cls.TYPE_MAP:
                return cls.TYPE_MAP[json_type]

        logger.warning(f"Unknown type in schema {json_schema}, defaulting to STRING")
        return "STRING"


class StarRocksWriter:
    def __init__(self, config: StarRocksConfig):
        self.config = config
        self.engine = self._create_engine()
        self.session = self._create_http_session()

        scheme = "https" if config.ssl else "http"
        self._stream_load_base_url = f"{scheme}://{config.host}:{config.http_port}"
        self._stream_columns: Dict[str, List[str]] = {}
        self._stream_col_types: Dict[str, Dict[str, str]] = {}

    def _create_engine(self):
        connection_url = URL.create(
            drivername="starrocks",
            username=self.config.username,
            password=self.config.password,
            host=self.config.host,
            port=self.config.port,
            database=self.config.database
        )
        connect_args = {}
        if self.config.ssl:
            connect_args["ssl"] = {"verify_mode": ssl.CERT_NONE}

        return create_engine(connection_url, connect_args=connect_args)

    def _create_http_session(self):
        """
        Create a persistent HTTP session for Stream Load API calls.
        """
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        session = requests.Session()
        session.auth = (self.config.username, self.config.password)
        session.verify = self.config.ssl

        adapter = HTTPAdapter(
            pool_connections=1,
            pool_maxsize=2,
            max_retries=Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def verify_stream_load_connectivity(self) -> bool:
        """
        Verify that the configured Stream Load endpoint is accessible.

        Returns True if accessible, False otherwise.
        """
        try:
            response = self.session.get(self._stream_load_base_url, timeout=5, allow_redirects=True)
            return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.debug(f"Stream Load not accessible at {self._stream_load_base_url}: {str(e)[:100]}")
            return False

    def write_raw(
        self,
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        """
        Write data to StarRocks in raw mode using Stream Load API.

        In raw mode, data is stored in tables with the following schema:
        - _airbyte_ab_id: Unique identifier for each record
        - _airbyte_emitted_at: Timestamp when the record was emitted
        - _airbyte_data: JSON blob containing the raw record data

        :param configured_catalog: The configured catalog describing streams
        :param input_messages: Stream of input messages from the source
        :return: Iterable of state messages
        """
        streams = {s.stream.name for s in configured_catalog.streams}

        with self.engine.connect() as con:
            # Create tables for each stream
            self._create_raw_tables(con, configured_catalog)

            buffer = defaultdict(list)

            for message in input_messages:
                if message.type == Type.STATE:
                    if buffer:
                        self._flush_raw_buffer_stream_load(buffer)
                        buffer = defaultdict(list)
                    yield message

                elif message.type == Type.RECORD:
                    data = message.record.data
                    stream = message.record.stream
                    if stream not in streams:
                        logger.debug(f"Stream {stream} was not present in configured streams, skipping")
                        continue

                    buffer[stream].append((
                        str(uuid.uuid4()),
                        datetime.datetime.now().isoformat(),
                        json.dumps(data)
                    ))

            if buffer:
                self._flush_raw_buffer_stream_load(buffer)

    def _create_raw_tables(self, connection, configured_catalog: ConfiguredAirbyteCatalog):
        """Create raw tables for each stream in the catalog."""
        for configured_stream in configured_catalog.streams:
            name = configured_stream.stream.name
            table_name = f"_airbyte_raw_{name}"

            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                connection.execute(text(
                    f"DROP TABLE IF EXISTS `{self.config.database}`.`{table_name}`"
                ))

            connection.execute(text(f"""
                CREATE TABLE IF NOT EXISTS `{self.config.database}`.`{table_name}` (
                    _airbyte_ab_id VARCHAR(36),
                    _airbyte_emitted_at DATETIME,
                    _airbyte_data JSON
                )
                UNIQUE KEY(_airbyte_ab_id)
                DISTRIBUTED BY HASH(_airbyte_ab_id)
            """))

    def _flush_raw_buffer_stream_load(self, buffer: Dict[str, List]):
        """Flush buffered records using StarRocks Stream Load API."""
        for stream_name, records in buffer.items():
            if not records:
                continue

            table_name = f"_airbyte_raw_{stream_name}"
            record_count = len(records)

            # Build CSV in memory with proper quoting for JSON fields
            csv_buffer = StringIO()
            writer = csv.writer(
                csv_buffer,
                quoting=csv.QUOTE_ALL, 
                doublequote=True, 
                escapechar='\\'
            )
            for record_id, emitted_at, data_json in records:
                writer.writerow([record_id, emitted_at, data_json])

            csv_data = csv_buffer.getvalue()

            self._execute_raw_stream_load(table_name, csv_data, record_count)

    def _execute_raw_stream_load(self, table_name: str, csv_data: str, record_count: int):
        """Execute Stream Load API call."""
        url = f"{self._stream_load_base_url}/api/{quote(self.config.database)}/{quote(table_name)}/_stream_load"

        # Generate unique transaction label
        label = f"airbyte_{table_name}_{int(time.time() * 1000)}"

        headers = {
            "Expect": "100-continue",
            "label": label,
            "column_separator": ",",
            "format": "CSV",
            "enclose": '"',  # Fields enclosed in double quotes (for JSON strings)
            "escape": '\\',  # Escape character for special chars
            "columns": "_airbyte_ab_id,_airbyte_emitted_at,_airbyte_data",
        }

        response = self.session.put(
            url,
            headers=headers,
            data=csv_data.encode('utf-8'),
            timeout=300,
            allow_redirects=True,
        )

        try:
            if response.status_code != 200:
                raise Exception(f"Stream Load failed: {response.status_code} - {response.text}")

            result = response.json()
            if result.get("Status") != "Success":
                raise Exception(f"Stream Load error: {result}")
        finally:
            # Explicitly close response to free memory immediately
            response.close()

    def write_typed(
        self,
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        """
        Write data to StarRocks in typed mode.

        In typed mode, data is stored in tables with columns matching the JSON schema.
        This provides better query performance and type safety.

        :param configured_catalog: The configured catalog describing streams
        :param input_messages: Stream of input messages from the source
        :return: Iterable of state messages
        """
        streams = {s.stream.name: s for s in configured_catalog.streams}

        with self.engine.connect() as con:
            # Create typed tables for each stream
            self._create_typed_tables(con, configured_catalog)

            buffer = defaultdict(list)

            for message in input_messages:
                if message.type == Type.STATE:
                    if buffer:
                        self._flush_typed_buffer_stream_load(buffer)
                        buffer = defaultdict(list)
                    yield message

                elif message.type == Type.RECORD:
                    data = message.record.data
                    stream_name = message.record.stream
                    if stream_name not in streams:
                        logger.debug(f"Stream {stream_name} not in configured streams, skipping")
                        continue

                    row = dict(data)
                    row.setdefault("_airbyte_ab_id", str(uuid.uuid4()))
                    row.setdefault("_airbyte_emitted_at", datetime.datetime.now().isoformat())
                    buffer[stream_name].append(row)

            if buffer:
                self._flush_typed_buffer_stream_load(buffer)

    def _create_typed_tables(self, connection, configured_catalog: ConfiguredAirbyteCatalog):
        """Create typed tables with proper column definitions."""
        for configured_stream in configured_catalog.streams:
            stream = configured_stream.stream
            table_name = stream.name
            json_schema = stream.json_schema

            # Get properties from schema
            properties = json_schema.get("properties", {})

            primary_key = stream.source_defined_primary_key or []
            if primary_key:
                # Use primary key from source
                key_cols = [pk[0] for pk in primary_key]
            else:
                # Use Airbyte ID as key
                key_cols = ["_airbyte_ab_id"]

            # Build column definitions.
            # StarRocks requires UNIQUE KEY columns to appear first.
            col_names = []
            col_defs = []
            col_types = {}

            def _add(name, sql_type):
                col_names.append(name)
                col_defs.append(f"{name} {sql_type}")
                col_types[name] = sql_type

            if primary_key:
                for pk in primary_key:
                    prop_name = pk[0]
                    if prop_name in properties:
                        _add(prop_name, StarRocksTypeMapper.get_sql_type(properties[prop_name]))

            _add("_airbyte_ab_id", "VARCHAR(36)")
            _add("_airbyte_emitted_at", "DATETIME")

            for prop_name, prop_schema in properties.items():
                if prop_name not in key_cols:
                    _add(prop_name, StarRocksTypeMapper.get_sql_type(prop_schema))

            self._stream_columns[table_name] = col_names
            self._stream_col_types[table_name] = col_types

            if configured_stream.destination_sync_mode == DestinationSyncMode.overwrite:
                connection.execute(text(f"DROP TABLE IF EXISTS `{self.config.database}`.`{table_name}`"))

            create_sql = f"""
                CREATE TABLE IF NOT EXISTS `{self.config.database}`.`{table_name}` (
                    {', '.join(col_defs)}
                )
                UNIQUE KEY({', '.join(key_cols)})
                DISTRIBUTED BY HASH({', '.join(key_cols)})
            """

            logger.info(f"Creating typed table: {table_name}")
            logger.debug(f"DDL: {create_sql}")
            connection.execute(text(create_sql))
            connection.commit()

    def _flush_typed_buffer_stream_load(self, buffer: Dict[str, List[Dict]]):
        """Flush typed records using Stream Load."""
        for stream_name, records in buffer.items():
            if not records:
                continue

            col_names = self._stream_columns[stream_name]
            col_types = self._stream_col_types[stream_name]

            csv_buffer = StringIO()
            writer = csv.writer(csv_buffer, quoting=csv.QUOTE_ALL, doublequote=True, escapechar='\\')
            writer.writerows(
                [_coerce(record.get(col), col_types.get(col, "STRING")) for col in col_names]
                for record in records
            )

            self._execute_typed_stream_load(stream_name, csv_buffer.getvalue(), col_names)

    def _execute_typed_stream_load(self, table_name: str, csv_data: str, column_names: List[str]):
        """Execute Stream Load for typed tables."""
        url = f"{self._stream_load_base_url}/api/{quote(self.config.database)}/{quote(table_name)}/_stream_load"

        label = f"airbyte_{table_name}_{int(time.time() * 1000)}"

        headers = {
            "Expect": "100-continue",
            "label": label,
            "column_separator": ",",
            "format": "CSV",
            "enclose": '"',
            "escape": '\\',
            "columns": ','.join(column_names), 
        }

        response = self.session.put(
            url,
            headers=headers,
            data=csv_data.encode('utf-8'),
            timeout=300,
            allow_redirects=True,
        )

        try:
            if response.status_code != 200:
                raise Exception(f"Stream Load failed: {response.status_code} - {response.text}")

            result = response.json()
            if result.get("Status") != "Success":
                raise Exception(f"Stream Load error: {result}")
        finally:
            response.close()
