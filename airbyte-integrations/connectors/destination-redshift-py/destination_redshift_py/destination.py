#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import argparse
import logging
from datetime import datetime
from functools import reduce
from hashlib import sha256
from operator import iconcat
from typing import Mapping, Any, Iterable, List
from uuid import uuid4

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, ConfiguredAirbyteCatalog, AirbyteMessage, Status, Type
from dotmap import DotMap
from psycopg2.pool import ThreadedConnectionPool

from destination_redshift_py.csv_writer import CSVWriter
from destination_redshift_py.jsonschema_to_tables import JsonToTables, PARENT_CHILD_SPLITTER
from destination_redshift_py.s3_writer import S3Writer
from destination_redshift_py.table import AIRBYTE_EMITTED_AT, AIRBYTE_ID_NAME

logger = logging.getLogger("airbyte")


class DestinationRedshiftPy(Destination):
    def __init__(self):
        self.final_tables = dict()
        self.staging_tables = dict()

        self.csv_writers = dict()

    def run_cmd(self, parsed_args: argparse.Namespace) -> Iterable[AirbyteMessage]:
        cmd = parsed_args.command

        if cmd in ["write", "check"]:
            config = self.read_config(config_path=parsed_args.config)
            self._create_pool(config=config)

            if cmd == "write":
                self._extract_tables_from_json_schema(ConfiguredAirbyteCatalog.parse_file(parsed_args.catalog))
                self._create_tables()
                self._initialize_staging_schema()
                self._initialize_csv_writers()
                self._initialize_s3_writer(config=config)
                self._initialize_iam_role_arn(iam_role_arn=config.get("iam_role_arn"))
                return super().run_cmd(parsed_args)

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
                self._flush()
                yield message
            elif message.type == Type.RECORD:
                data = DotMap({message.record.stream: message.record.data})

                # Build a simple tree out of the dictionary and visit the leave nodes before parents to clear the leave nodes
                # attributes. The leave nodes are the dictionary keys with the largest length after splitting the name.
                # The return value is a list of lists. For example, if the input is:
                #       `['orders', 'orders.account', 'orders.accounts.address']`
                # The output is:
                #       `[['orders', 'accounts', 'address'], ['orders', 'account'], ['orders']]`
                nodes = sorted(map(lambda k: k.split(PARENT_CHILD_SPLITTER), self.final_tables.keys()), key=len, reverse=True)

                for node in nodes:
                    emitted_at = message.record.emitted_at

                    table = self.final_tables[PARENT_CHILD_SPLITTER.join(node)]
                    parent_table = self.final_tables.get(PARENT_CHILD_SPLITTER.join(node[0:-1]))

                    parent_record = reduce(getattr, [data] + node[0:-1])
                    records = getattr(parent_record, node[-1])
                    records = [records] if not isinstance(records, list) else records

                    self._assign_id_and_emitted_at(records=records, primary_keys=table.primary_keys, emitted_at=emitted_at)

                    if parent_table:
                        self._assign_id_and_emitted_at(records=[parent_record], primary_keys=parent_table.primary_keys,
                                                       emitted_at=emitted_at)

                        reference_id = parent_record[AIRBYTE_ID_NAME]
                        self._assign_reference_id(records=records, reference_key=table.reference_key, reference_id=reference_id)

                    # Delete the child after visiting
                    delattr(parent_record, node[-1])

                    self.csv_writers[table.name].write(records)

        self._flush()

    @staticmethod
    def _assign_id_and_emitted_at(records: List[DotMap], emitted_at: int, primary_keys: List[str]):
        for record in records:
            record[AIRBYTE_EMITTED_AT.name] = datetime.utcfromtimestamp(emitted_at / 1000).isoformat(timespec="seconds")
            DestinationRedshiftPy._assign_id(record=record, primary_keys=primary_keys)

    @staticmethod
    def _assign_reference_id(records: List[DotMap], reference_key: str, reference_id: str):
        for record in records:
            record[reference_key] = reference_id

    @staticmethod
    def _assign_id(record: DotMap, primary_keys: List[str]):
        if AIRBYTE_ID_NAME not in record:
            # Ignore the Airbyte ID primary key column as it is going to be set in this method
            if AIRBYTE_ID_NAME in primary_keys: primary_keys.remove(AIRBYTE_ID_NAME)

            if primary_keys:
                record[AIRBYTE_ID_NAME] = sha256("".join([record[primary_key] for primary_key in primary_keys]).encode()).hexdigest()[-32:]
            else:
                record[AIRBYTE_ID_NAME] = uuid4().hex

    def _extract_tables_from_json_schema(self, configured_catalog: ConfiguredAirbyteCatalog):
        for stream in configured_catalog.streams:
            schema = stream.stream.namespace
            root_table = stream.stream.name
            primary_keys = reduce(iconcat, stream.primary_key, [])

            converter = JsonToTables(stream.stream.json_schema, schema=schema, root_table=root_table, primary_keys=primary_keys)
            converter.convert()

            self.final_tables = dict(**self.final_tables, **converter.tables)

    def _create_tables(self):
        cursor = self._get_connection(autocommit=True).cursor()

        for _, table_def in self.final_tables.items():
            sql = table_def.create_statement()
            cursor.execute(sql)

    def _initialize_staging_schema(self):
        cursor = self._get_connection(autocommit=True).cursor()
        random_table = list(self.final_tables.values())[0]  # All final_tables will be stored in the same schema

        staging_schema = f"_airbyte_{random_table.schema}"
        sql = f"CREATE SCHEMA IF NOT EXISTS {staging_schema}"
        cursor.execute(sql)

        for key, table in self.final_tables.items():
            staging_table = table
            staging_table.schema = staging_schema

            self.staging_tables[key] = staging_table

            cursor.execute(staging_table.create_statement())

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

    def _initialize_csv_writers(self):
        for table in self.final_tables.values():
            csv_writer = CSVWriter(table=table)
            csv_writer.initialize_writer()

            self.csv_writers[table.name] = csv_writer

    def _initialize_s3_writer(self, config: Mapping[str, Any]):
        self.s3_writer = S3Writer(bucket=config.get("s3_bucket_name"), s3_path=config.get("s3_bucket_path"))

    def _initialize_iam_role_arn(self, iam_role_arn: str):
        self.iam_role_arn = iam_role_arn

    def _flush(self):
        connection = self._get_connection()
        cursor = connection.cursor()

        for table in self.staging_tables.values():
            csv_writer = self.csv_writers[table.name]
            temporary_gzip_file = csv_writer.flush_gzipped()

            if temporary_gzip_file:
                s3_full_path = self.s3_writer.upload_file_to_s3(temporary_gzip_file.name)
                csv_writer.delete_gzip_file(temporary_gzip_file)
                sql = table.coy_csv_gzip_statement(iam_role_arn=self.iam_role_arn, s3_full_path=s3_full_path)
                cursor.execute(sql)

        connection.commit()

