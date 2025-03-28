import logging
import unittest
from textwrap import dedent
from unittest.mock import MagicMock, Mock, patch

from airbyte._batch_handles import BatchHandle
from airbyte.strategies import WriteStrategy
from airbyte_cdk.destinations.vector_db_based import ProcessingConfigModel
from airbyte_cdk.models import ConnectorSpecification, Status
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStreamState,
    Type,
)
from airbyte_protocol.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode, \
    AirbyteStream

from destination_mariadb.common.catalog.catalog_providers import CatalogProvider
from destination_mariadb.config import ConfigModel
from destination_mariadb.destination import DestinationMariaDB
from destination_mariadb.mariadb_processor import DatabaseConfig
from destination_mariadb.mariadb_processor import MariaDBProcessor
from airbyte_cdk.destinations.vector_db_based import FakeEmbeddingConfigModel
from pathlib import Path
import tempfile
from airbyte.secrets import SecretString


class TestDestinationMariaDB(unittest.TestCase):
    def setUp(self):
        self.config = {
            "processing": {"text_fields": ["str_col"], "metadata_fields": [], "chunk_size": 1000},
            "embedding": {"mode": "openai", "openai_key": "mykey"},
            "indexing": {
                "host": "MYACCOUNT",
                "port": 5432,
                "database": "MYDATABASE",
                "default_schema": "MYSCHEMA",
                "username": "MYUSERNAME",
                "credentials": {"password": "xxxxxxx"},
            },
        }
        self.config_model = ConfigModel.parse_obj(self.config)
        self.logger = logging.getLogger("airbyte")

        test_splitter = ProcessingConfigModel(
            chunk_size=666
        )

        fake_embedder = FakeEmbeddingConfigModel(
            mode="fake"
        )

        # ok, we actually need a catalog provider
        configured_catalog = ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(
                    cursor_field=["updated_at"],
                    destination_sync_mode=DestinationSyncMode.overwrite,
                    generation_id=None,
                    minimum_generation_id=None,
                    primary_key=[['id']],
                    sync_id=None,
                    sync_mode=SyncMode.full_refresh,
                    stream=AirbyteStream(
                        default_cursor_field=['updated_at'],
                        is_resumable=True,
                        name='users',
                        namespace=None,
                        source_defined_cursor=True,
                        source_defined_primary_key=[['id']],
                        supported_sync_modes=[
                            SyncMode.full_refresh,
                            SyncMode.incremental
                        ],
                        json_schema={
                            '$schema': 'http://json-schema.org/schema#', 'additionalProperties': True,
                            'properties': {'academic_degree': {'type': 'string'}, 'address': {
                                'properties': {'city': {'type': 'string'}, 'country_code': {'type': 'string'},
                                               'postal_code': {'type': 'string'},
                                               'province': {'type': 'string'}, 'state': {'type': 'string'},
                                               'street_name': {'type': 'string'},
                                               'street_number': {'type': 'string'}}, 'type': 'object'},
                                           'age': {'type': 'integer'}, 'blood_type': {'type': 'string'},
                                           'created_at': {'airbyte_type': 'timestamp_with_timezone',
                                                          'format': 'date-time', 'type': 'string'},
                                           'email': {'type': 'string'}, 'gender': {'type': 'string'},
                                           'height': {'type': 'string'}, 'id': {'type': 'integer'},
                                           'language': {'type': 'string'}, 'name': {'type': 'string'},
                                           'nationality': {'type': 'string'}, 'occupation': {'type': 'string'},
                                           'telephone': {'type': 'string'}, 'title': {'type': 'string'},
                                           'updated_at': {'airbyte_type': 'timestamp_with_timezone',
                                                          'format': 'date-time', 'type': 'string'},
                                           'weight': {'type': 'integer'}}, 'type': 'object'}
                    )
                )
            ]
        )

        test_message = AirbyteMessage(
            catalog=None,
            connectionStatus=None,
            control=None,
            log=None,
            spec=None,
            state=None,
            trace=None,
            type=Type.RECORD,
            record=AirbyteRecordMessage(
                data={
                    'academic_degree': 'Master',
                    'address': {
                        'city': 'Austin',
                        'country_code': 'UG',
                        'postal_code': '49893',
                        'province': 'North Carolina',
                        'state': 'Kentucky',
                        'street_name': 'Princeton',
                        'street_number': '789'
                    },
                    'age': 53,
                    'blood_type': 'B−',
                    'created_at': '2012-07-02T08:32:31+00:00',
                    'email': 'reason1932+1@protonmail.com',
                    'gender': 'Male',
                    'height': '1.55',
                    'id': 1,
                    'language': 'Tamil',
                    'name': 'Patria',
                    'nationality': 'Italian',
                    'occupation': 'Word Processing Operator',
                    'telephone': '+1-(110)-795-7610',
                    'title': 'M.A.',
                    'updated_at': '2025-03-27T14:37:27+00:00',
                    'weight': 58
                },
                emitted_at=1743086247202,
                meta=None,
                namespace=None,
                stream="users",
            ),

        )

        self.input_messages = [
            test_message
        ]

        self.fileWriterMock = Mock()

        # file_writer: FileWriterBase

        self.testProcessor = MariaDBProcessor(
            DatabaseConfig(
                host=self.config_model.indexing.host,
                port=self.config_model.indexing.port,
                database=self.config_model.indexing.database,
                # schema_name=config.indexing.default_schema,
                username=self.config_model.indexing.username,
                password=SecretString(self.config_model.indexing.credentials.password),
            ),
            splitter_config=test_splitter,
            embedder_config=fake_embedder,
            catalog_provider=CatalogProvider(configured_catalog),
            temp_dir=Path(tempfile.mkdtemp()),
            temp_file_cleanup=True,
        )

        self.testProcessor.file_writer = self.fileWriterMock

        fake_sql_engine = None

        # I think I can mock like this:
        self.testProcessor.get_sql_engine = MagicMock(return_value=fake_sql_engine)

    def _multiline_trim(self, text):
        lines = text.split("\n")

        result_lines = []

        for line in lines:
            result_lines.append(line.strip())

        return "\n".join(result_lines).strip()

    def assertMultilineTrimmed(self, expected, actual):
        self.assertMultiLineEqual(self._multiline_trim(expected), self._multiline_trim(actual))
        pass


    def test_create_database(self):



        # probably also need to overwrite this:
        # get_sql_connection

        # mock this away
        self.testProcessor._table_exists = MagicMock(return_value=False)


        expected = """
            CREATE TABLE `muhkuh` (
                `document_id` VARCHAR(255),
                `chunk_id` VARCHAR(255),
                `metadata` JSON,
                `document_content` TEXT,
                `embedding` VECTOR(1536),
                PRIMARY KEY (document_id)
            )
        """

        self.num_sql_exec_runs = 0

        def testfunc(sql):
            self.assertMultilineTrimmed(sql, expected)
            # print(dedent(sql))

            self.num_sql_exec_runs += 1

            return sql

        # somehow test in this one?
        self.testProcessor._execute_sql = testfunc

        self.testProcessor._ensure_final_table_exists('muhkuh')

        self.assertEqual(self.num_sql_exec_runs, 1)

    #import pandas as pd
    #destination_mariadb.common.sql.sql_processor.SQLRuntimeError
    @patch("destination_mariadb.common.sql.sql_processor.pd")
    def test_write(self, sqlproc_pd):
        self.testProcessor._table_exists = MagicMock(return_value=True)
        # mock this:
        # dataframe = pd.read_json(file_path, lines=True)
        # then, parts of dataframe can be mocked?


        # see sql_processor._write_temp_table_to_final_table, we should definitely test all 3 WriteStrategys



        # MUST MOCK: batches_to_finalize: list[BatchHandle] = self.file_writer.get_pending_batches(stream_name)
        # for destination_mariadb/common/sql/sql_processor.py:506

        batches_to_finalize = [BatchHandle(
            stream_name="users",
            batch_id="123",
            files=[Path(
                '/no/such/thing'
            )],
            file_opener=Mock(),
        )]

        #self.fileWriterMock.batches_to_finalize = batches_to_finalize
        self.fileWriterMock.get_pending_batches = MagicMock(return_value=batches_to_finalize)

        self.num_sql_exec_runs = 0

        def testfunc(sql):
            # self.assertMultilineTrimmed(sql, expected)
            print(dedent(sql))

            self.num_sql_exec_runs += 1

            return sql

        """
        # query 1:
        '
        CREATE TABLE `users_01jqc3g3f2eq6jpdrej4tx10bm` (
            `document_id` VARCHAR(255),
  `chunk_id` VARCHAR(255),
  `metadata` JSON,
  `document_content` TEXT,
  `embedding` VECTOR(1536)
        )
        '
        
        # query 2:
        'ALTER TABLE `users` RENAME TO users_deleteme;
        ALTER TABLE `users_01jqeb6pq9p5fqw5xrsnftnmwr` RENAME TO users;
        # query 3:
        DROP TABLE `users_deleteme`;'
        
        # query 4:
        'DROP TABLE IF EXISTS `users_01jqeb6pq9p5fqw5xrsnftnmwr`'


        """

        # somehow test in this one?
        #self.testProcessor._execute_sql = testfunc
        sql_mock = Mock()
        self.testProcessor._execute_sql = sql_mock


        for something in self.testProcessor.process_airbyte_messages_as_generator(
            messages=self.input_messages,
            write_strategy=WriteStrategy.AUTO,
        ):
            print(something)

        #self.assertGreater(self.num_sql_exec_runs, 0)
        #self.file_writer.process_record_message( <- try assert that this was called
        #dataframe.to_sql( <- this too

        self.assertEqual(sql_mock.call_count, 3)
        # now, check the sql statements which have been used, they are in .call_args_list

        sqlCreate = """
        CREATE TABLE `users_123` (
            `document_id` VARCHAR(255),
            `chunk_id` VARCHAR(255),
            `metadata` JSON,
            `document_content` TEXT,
            `embedding` VECTOR(1536)
        )
        """

        sqlAlter = """
            ALTER TABLE `users` RENAME TO users_deleteme;
            ALTER TABLE `users_123` RENAME TO users;
            DROP TABLE `users_deleteme`;
        """

        sqlDrop = """ 
            DROP TABLE IF EXISTS `users_123` 
        """

        self.assertMultilineTrimmed(sql_mock.call_args_list[0].args[0], sqlCreate)
        self.assertMultilineTrimmed(sql_mock.call_args_list[1].args[0], sqlAlter)
        self.assertMultilineTrimmed(sql_mock.call_args_list[2].args[0], sqlDrop)




