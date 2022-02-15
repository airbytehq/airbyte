#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import argparse
import logging
from datetime import datetime
from functools import reduce
from operator import iconcat
from typing import Mapping, Any, Iterable
from uuid import uuid4

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, ConfiguredAirbyteCatalog, AirbyteMessage, Status, Type
from dotmap import DotMap
from psycopg2.pool import ThreadedConnectionPool

from destination_redshift_py.jsonschema_to_tables import JsonToTables, PARENT_CHILD_SPLITTER
from destination_redshift_py.table import AIRBYTE_AB_ID, AIRBYTE_EMITTED_AT, Table

logger = logging.getLogger("airbyte")


class DestinationRedshiftPy(Destination):
    def __init__(self):
        self.connection_pool: ThreadedConnectionPool = None

        self.tables = dict()

    def run_cmd(self, parsed_args: argparse.Namespace) -> Iterable[AirbyteMessage]:
        cmd = parsed_args.command

        if cmd in ["write", "check"]:
            config = self.read_config(config_path=parsed_args.config)
            self._create_pool(config=config)

        if cmd == "write":
            self._extract_tables_from_json_schema(ConfiguredAirbyteCatalog.parse_file(parsed_args.catalog))
            self._create_tables()
            return super().run_cmd(parsed_args)
        else:
            return super().run_cmd(parsed_args)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            cursor = self._get_connection(autocommit=True).cursor()
            cursor.execute("SELECT 1")
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")

    def write(
            self,
            config: Mapping[str, Any],
            configured_catalog: ConfiguredAirbyteCatalog,
            input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:

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
        for message in input_messages:
            if message.type == Type.STATE:
                yield message
            elif message.type == Type.RECORD:
                data = DotMap({message.record.stream: message.record.data})

                # Build a simple tree out of the dictionary and visit the leave nodes before parents to clear the leave nodes
                # attributes. The leave nodes are the dictionary keys with the largest length after splitting the name
                nodes = sorted(map(lambda k: k.split(PARENT_CHILD_SPLITTER), self.tables.keys()), key=len, reverse=True)

                for node in nodes:
                    table = self.tables[PARENT_CHILD_SPLITTER.join(node)]

                    parent = reduce(self._visit_node, [data] + node[0:-1])
                    records = getattr(parent, node[-1])

                    if isinstance(records, list):
                        for record in records:
                            self._process_record(table=table, parent_record=parent, record=record, emitted_at=message.record.emitted_at)
                    else:
                        self._process_record(table=table, parent_record=parent, record=records, emitted_at=message.record.emitted_at)

                    # Delete the child after visiting
                    delattr(parent, node[-1])

                    print(f"{table.name} -> {records}")

    def _process_record(self, table: Table, parent_record: DotMap, record: DotMap, emitted_at: int):
        record[AIRBYTE_EMITTED_AT.name] = datetime.utcfromtimestamp(emitted_at / 1000).isoformat()

        self._assign_unique_id(record)

        if table.reference_key:
            record[table.reference_key] = parent_record[AIRBYTE_AB_ID.name]

    def _extract_tables_from_json_schema(self, configured_catalog: ConfiguredAirbyteCatalog):
        for stream in configured_catalog.streams:
            schema = stream.stream.namespace
            root_table = stream.stream.name
            primary_keys = reduce(iconcat, stream.primary_key, [])

            converter = JsonToTables(stream.stream.json_schema, schema=schema, root_table=root_table, primary_keys=primary_keys)
            converter.convert()

            self.tables = dict(**self.tables, **converter.tables)

    def _create_tables(self):
        cursor = self._get_connection(autocommit=True).cursor()

        for _, table_def in self.tables.items():
            sql = table_def.create_statement()
            cursor.execute(sql)

    def _create_pool(self, config: Mapping[str, Any]):
        self.connection_pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=config.get("max_connections"),
            host=config.get("host"),
            port=config.get("port"),
            database=config.get("database"),
            user=config.get("username"),
            password=config.get("password")
        )

    def _get_connection(self, autocommit=False):
        connection = self.connection_pool.getconn()
        connection.autocommit = autocommit

        return connection

    @staticmethod
    def _visit_node(parent: DotMap, attr: str) -> DotMap:
        node = getattr(parent, attr)

        DestinationRedshiftPy._assign_unique_id(node)

        return node

    @staticmethod
    def _assign_unique_id(fields: DotMap):
        if AIRBYTE_AB_ID.name not in fields:
            fields[AIRBYTE_AB_ID.name] = uuid4().hex
