#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import argparse
import logging
from copy import deepcopy
from datetime import datetime
from functools import reduce
from hashlib import sha256
from operator import iconcat
from typing import Mapping, Any, Iterable, List, Dict, Union

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, ConfiguredAirbyteCatalog, AirbyteMessage, Status, Type, \
    DestinationSyncMode
from dotmap import DotMap
from psycopg2._psycopg import connection as Connection
from psycopg2.pool import ThreadedConnectionPool, SimpleConnectionPool

from destination_redshift_py.csv_writer import CSVWriter
from destination_redshift_py.jsonschema_to_tables import JsonToTables, PARENT_CHILD_SPLITTER
from destination_redshift_py.s3_objects_manager import S3ObjectsManager
from destination_redshift_py.stream import Stream
from destination_redshift_py.table import AIRBYTE_EMITTED_AT, AIRBYTE_ID_NAME, Table

logger = logging.getLogger("airbyte")


class DestinationRedshiftPy(Destination):
    def __init__(self):
        self.streams: Dict[str, Stream] = dict()

        self.csv_writers: Dict[str, CSVWriter] = dict()

    def run_cmd(self, parsed_args: argparse.Namespace) -> Iterable[AirbyteMessage]:
        cmd = parsed_args.command

        if cmd in ["write", "check"]:
            config = self.read_config(config_path=parsed_args.config)
            self._create_pool(config=config)

            if cmd == "write":
                self._initialize_streams(configured_catalog=ConfiguredAirbyteCatalog.parse_file(parsed_args.catalog))
                self._create_final_tables()
                self._initialize_staging_schema()
                self._initialize_csv_writers()
                self._initialize_s3_object_manager(config=config)
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
                nested_record = DotMap({message.record.stream: message.record.data})

                # Build a simple tree out of the dictionary and visit the parent nodes before children to assign the IDs to the parents
                # before the children so that the children can use the parent IDs in the references (foreign key).
                # Parents key always have shorter length than the children as the children combine the parent and the child keys.
                # The return value is a list of lists.
                #
                # For example, if the input is:
                #       `['orders', 'orders.account', 'orders.accounts.address']`
                # The output is:
                #       `[['orders'], ['orders', 'account'], ['orders', 'accounts', 'address']]`
                stream = self.streams[message.record.stream]

                nodes = sorted(map(lambda k: k.split(PARENT_CHILD_SPLITTER), stream.final_tables.keys()), key=len)
                emitted_at = message.record.emitted_at

                for node in nodes:
                    final_table = stream.final_tables[PARENT_CHILD_SPLITTER.join(node)]

                    def get_records(parents: Union[DotMap, List[DotMap]], method: str) -> List[DotMap]:
                        if not isinstance(parents, list):
                            parents = [parents]

                        children_records = []
                        for parent_item in parents:
                            children = getattr(parent_item, method)
                            if not isinstance(children, list):
                                children = [children]

                            for child_item in children:
                                if child_item and final_table.references and method == node[-1]:
                                    child_item[final_table.reference_key.name] = parent_item[AIRBYTE_ID_NAME]

                                children_records.append(child_item)

                        return children_records

                    records = reduce(get_records, [nested_record] + node)
                    records = list(filter(None.__ne__, records))

                    if records:
                        # Choose primary keys (other than the Airbyte auto generated ID). If there are no primary keys (except the auto
                        # generated Airbyte ID, this happens with children), then choose all the fields as hash keys to generate the ID.
                        hashing_keys = [pk for pk in final_table.primary_keys if pk != AIRBYTE_ID_NAME] or final_table.field_names

                        self._assign_id_and_emitted_at(records=records, hashing_keys=hashing_keys, emitted_at=emitted_at)

                        # Assign only the table fields and drop other fields
                        records = [
                            DotMap([field_name, record[field_name] or None] for field_name in final_table.field_names) for record in records
                        ]

                        csv_writer = self.csv_writers[final_table.name]
                        csv_writer.write(records)

        self._flush()
        self.connection_pool.closeall()

    @staticmethod
    def _assign_id_and_emitted_at(records: List[DotMap], emitted_at: int, hashing_keys: List[str]):
        for record in records:
            DestinationRedshiftPy._assign_id(record=record, hashing_keys=hashing_keys)
            record[AIRBYTE_EMITTED_AT.name] = datetime.utcfromtimestamp(emitted_at / 1000).isoformat(timespec="seconds")

    @staticmethod
    def _assign_reference_id(records: List[DotMap], reference_key: str, reference_id: str):
        for record in records:
            record[reference_key] = reference_id

    @staticmethod
    def _assign_id(record: DotMap, hashing_keys: List[str]):
        if AIRBYTE_ID_NAME not in record:
            data = "".join([str(record[hashing_key]) for hashing_key in hashing_keys]).encode()

            record[AIRBYTE_ID_NAME] = sha256(data).hexdigest()[-32:]

    def _initialize_streams(self, configured_catalog: ConfiguredAirbyteCatalog):
        for stream in configured_catalog.streams:
            schema = stream.stream.namespace
            stream_name = stream.stream.name
            primary_keys = reduce(iconcat, stream.primary_key, [])

            converter = JsonToTables(stream.stream.json_schema, schema=schema, root_table=stream_name, primary_keys=primary_keys)
            converter.convert()

            sync_mode = stream.destination_sync_mode
            self.streams[stream_name] = Stream(name=stream_name, destination_sync_mode=sync_mode, final_tables=converter.tables)

    def _create_final_tables(self):
        cursor = self._get_connection(autocommit=True).cursor()

        for stream in self.streams.values():
            for table in stream.final_tables.values():
                cursor.execute(table.create_statement())

                if stream.destination_sync_mode == DestinationSyncMode.overwrite:
                    cursor.execute(table.truncate_statement())

    def _initialize_staging_schema(self):
        cursor = self._get_connection(autocommit=True).cursor()

        for stream in self.streams.values():
            if stream.destination_sync_mode == DestinationSyncMode.append_dedup:
                random_table = list(stream.final_tables.values())[0]  # All final_tables will be stored in the same schema

                staging_schema = f"_airbyte_{random_table.schema}"
                create_schema_statement = f"CREATE SCHEMA IF NOT EXISTS {staging_schema}"
                cursor.execute(create_schema_statement)

                for key, table in stream.final_tables.items():
                    staging_table = deepcopy(table)
                    staging_table.schema = staging_schema

                    stream.staging_tables[key] = staging_table

                    cursor.execute(staging_table.create_statement(staging=True))

    def _create_pool(self, config: Mapping[str, Any]):
        self.connection_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=config.get("max_connections"),
            host=config.get("host"),
            port=config.get("port"),
            database=config.get("database"),
            user=config.get("username"),
            password=config.get("password")
        )

    def _get_connection(self, autocommit: bool = False) -> Connection:
        connection = self.connection_pool.getconn()
        connection.autocommit = autocommit

        return connection

    def _put_connection(self, connection: Connection):
        self.connection_pool.putconn(connection)

    def _initialize_csv_writers(self):
        for stream in self.streams.values():
            for table in stream.final_tables.values():
                csv_writer = CSVWriter(table=table)
                csv_writer.initialize_writer()

                self.csv_writers[table.name] = csv_writer

    def _initialize_s3_object_manager(self, config: Mapping[str, Any]):
        bucket = config.get("s3_bucket_name")
        s3_path = config.get("s3_bucket_path")
        access_key_id = config.get("access_key_id")
        secret_access_key = config.get("secret_access_key")

        self.s3_object_manager = S3ObjectsManager(
            bucket=bucket,
            s3_path=s3_path,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key
        )

    def _initialize_iam_role_arn(self, iam_role_arn: str):
        self.iam_role_arn = iam_role_arn

    def _flush(self):
        for stream in self.streams.values():
            for key, final_table in stream.final_tables.items():
                self._flush_csv_writer_to_destination(
                    csv_writer=self.csv_writers[final_table.name],
                    final_table=final_table,
                    staging_table=stream.staging_tables[key],
                    mode=stream.destination_sync_mode
                )

    def _flush_csv_writer_to_destination(self, csv_writer: CSVWriter, final_table: Table, staging_table: Table, mode: DestinationSyncMode):
        rows_count = csv_writer.rows_count()
        temporary_gzip_file = csv_writer.flush_gzipped()

        if temporary_gzip_file:
            logger.info(f"Flushing {rows_count} to destination")

            connection = self._get_connection()
            cursor = connection.cursor()

            s3_full_path = self.s3_object_manager.upload_file_to_s3(temporary_gzip_file.name)
            CSVWriter.delete_gzip_file(temporary_gzip_file)

            if mode in [DestinationSyncMode.append, DestinationSyncMode.overwrite]:
                copy_statement = final_table.copy_csv_gzip_statement(iam_role_arn=self.iam_role_arn, s3_full_path=s3_full_path)
                cursor.execute(copy_statement)
            else:
                copy_statement = staging_table.copy_csv_gzip_statement(iam_role_arn=self.iam_role_arn, s3_full_path=s3_full_path)
                cursor.execute(copy_statement)

                upsert_statements = final_table.upsert_statements(staging_table=staging_table)
                cursor.execute(upsert_statements)

            connection.commit()

            self.s3_object_manager.delete_file_from_s3(s3_full_path)

            self._put_connection(connection)
