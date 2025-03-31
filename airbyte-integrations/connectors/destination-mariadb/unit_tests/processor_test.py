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

SQL_CREATE_STATEMENT = """
        CREATE TABLE `users_123` (
            `document_id` VARCHAR(255),
            `chunk_id` VARCHAR(255),
            `metadata` JSON,
            `document_content` TEXT,
            `embedding` VECTOR(1536)
        )
        """

SQL_DESTORY_STATEMENT = 'DROP TABLE IF EXISTS `users_123`'



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
        self.testProcessor.get_sql_engine = MagicMock(return_value=fake_sql_engine)

        # The batch_id is used later down the line for the name of the temp table
        self.batches_to_finalize = [BatchHandle(
            stream_name="users",
            batch_id="123",
            files=[Path(
                '/no/such/thing'
            )],
            file_opener=Mock(),
        )]

        # is is what it would write into the temp file
        self.document_content = """academic_degree: Master
            address: 
            city: Austin
            country_code: UG
            postal_code: 49893
            province: North Carolina
            state: Kentucky
            street_name: Princeton
            street_number: 789
            
            age: 53
            blood_type: B−
            created_at: 2012-07-02T08:32:31+00:00
            email: reason1932+1@protonmail.com
            gender: Male
            height: 1.55
            id: 1
            language: Tamil
            name: Patria
            nationality: Italian
            occupation: Word Processing Operator
            telephone: +1-(110)-795-7610
            title: M.A.
            updated_at: 2025-03-27T14:37:27+00:00
            weight: 58"""

        self.stream_schema_expected = {
            'properties': {'chunk_id': {'type': 'string'}, 'document_content': {'type': 'string'},
                           'document_id': {'type': 'string'},
                           'embedding': {'items': {'type': 'float'}, 'type': 'array'},
                           'metadata': {'type': 'object'}}, 'type': 'object'}

    def _multiline_trim(self, text):
        lines = text.split("\n")

        result_lines = []

        for line in lines:
            result_lines.append(line.strip())

        return "\n".join(result_lines).strip()

    def assertMultilineTrimmed(self, expected, actual, msg=None):
        self.assertMultiLineEqual(self._multiline_trim(expected), self._multiline_trim(actual), msg)
        pass

    def find_mock_call(self, mock: Mock, call_name):
        for call in mock.mock_calls:
            if call[0] == call_name:
                return call

        return None


    def test_create_database(self):
        self.testProcessor._table_exists = MagicMock(return_value=False)

        expected_qry = """
            CREATE TABLE `muhkuh` (
                `document_id` VARCHAR(255),
                `chunk_id` VARCHAR(255),
                `metadata` JSON,
                `document_content` TEXT,
                `embedding` VECTOR(1536),
                PRIMARY KEY (document_id)
            )
        """

        self.testProcessor._execute_sql = MagicMock()
        self.testProcessor._ensure_final_table_exists('muhkuh')

        self.assertEqual(self.testProcessor._execute_sql.call_count, 1)

        actual_qry = self.testProcessor._execute_sql.call_args_list[0].args[0]
        self.assertMultilineTrimmed(actual_qry, expected_qry)

    @patch("destination_mariadb.common.sql.sql_processor.pd")
    def test_write_stragegy_append(self, sqlproc_pd):
        # in append mode, the processor will fire INSERT queries directly
        self.testProcessor._table_exists = Mock(return_value=True)

        # see sql_processor._write_temp_table_to_final_table, we should definitely test all 3 WriteStrategys
        mock_dataframe = MagicMock()  # dataframe
        sqlproc_pd.read_json = Mock(return_value=mock_dataframe)

        # Mock away the batch handles. The batch_id is also used later down the line for the name of the temp table
        self.fileWriterMock.get_pending_batches = Mock(return_value=self.batches_to_finalize)

        # Mock away the _execute_sql
        sql_mock = Mock()
        self.testProcessor._execute_sql = sql_mock

        # Process the message
        for _ in self.testProcessor.process_airbyte_messages_as_generator(
                messages=self.input_messages,
                write_strategy=WriteStrategy.APPEND,
        ):
            pass

        # Test that the SQL statements are correct

        self.assertEqual(sql_mock.call_count, 3)
        # now, check the sql statements which have been used, they are in .call_args_list

        sql_create = SQL_CREATE_STATEMENT

        # TODO: is this valid MariaDB?
        sql_insert = """
        INSERT INTO `users` (
            `document_id`,
            `chunk_id`,
            `metadata`,
            `document_content`,
            `embedding`
        )
        SELECT
            `document_id`,
            `chunk_id`,
            `metadata`,
            `document_content`,
            `embedding`
        FROM `users_123`
        """

        sql_drop = SQL_DESTORY_STATEMENT

        self.assertMultilineTrimmed(sql_mock.call_args_list[0].args[0], sql_create)
        self.assertMultilineTrimmed(sql_mock.call_args_list[1].args[0], sql_insert)
        self.assertMultilineTrimmed(sql_mock.call_args_list[2].args[0], sql_drop)

        # Test what the mock_dataframe's to_sql was called
        self.assertEqual(1, mock_dataframe.to_sql.call_count, "to_sql should be called exactly once")

        # Testing that the attempt to write the temporary file is correct
        self.assertEqual(1, self.fileWriterMock.process_record_message.call_count)
        file_writer_kwargs = self.fileWriterMock.process_record_message.call_args_list[0].kwargs

        record_msg = file_writer_kwargs['record_msg']
        stream_schema = file_writer_kwargs['stream_schema']

        self.assertEqual(stream_schema, self.stream_schema_expected)

        self.assertMultilineTrimmed(record_msg.data['document_content'], self.document_content)

    @patch("destination_mariadb.common.sql.sql_processor.pd")
    def test_write_stragegy_merge(self, sqlproc_pd):
        self.testProcessor._table_exists = Mock(return_value=True)

        # see sql_processor._write_temp_table_to_final_table, we should definitely test all 3 WriteStrategys
        mock_dataframe = MagicMock()  # dataframe
        sqlproc_pd.read_json = Mock(return_value=mock_dataframe)

        # Mock away the batch handles.
        self.fileWriterMock.get_pending_batches = Mock(return_value=self.batches_to_finalize)

        # Mock away the _execute_sql
        sql_mock = Mock()
        self.testProcessor._execute_sql = sql_mock

        sql_conn_mock = MagicMock()
        self.testProcessor.get_sql_connection = MagicMock(return_value=sql_conn_mock)

        # Process the message
        for _ in self.testProcessor.process_airbyte_messages_as_generator(
                messages=self.input_messages,
                write_strategy=WriteStrategy.MERGE,
        ):
            pass

        # Test that the SQL statements are correct

        # TODO is this valid MariaDB?
        sql_insert = """
            INSERT INTO users
                (document_id, chunk_id, metadata, document_content, embedding)
            SELECT document_id, chunk_id, metadata, document_content, embedding
            FROM users_123
            ON DUPLICATE KEY UPDATE;
        """

        self.assertEqual(sql_mock.call_count, 2)


        # I have tried to do this in some sane way, but failed. If you know how to improve this, go ahead
        relevant_entry = self.find_mock_call(sql_conn_mock, '__enter__().execute')
        self.assertIsNotNone(relevant_entry, "There must have been a call to conn.execute()")


        self.assertMultilineTrimmed(sql_mock.call_args_list[0].args[0], SQL_CREATE_STATEMENT)
        self.assertMultilineTrimmed(relevant_entry.args[0], sql_insert)
        self.assertMultilineTrimmed(sql_mock.call_args_list[1].args[0], SQL_DESTORY_STATEMENT)



        # Test what the mock_dataframe's to_sql was called
        self.assertEqual(1, mock_dataframe.to_sql.call_count, "to_sql should be called exactly once")

        # Testing that the attempt to write the temporary file is correct
        self.assertEqual(1, self.fileWriterMock.process_record_message.call_count)
        file_writer_kwargs = self.fileWriterMock.process_record_message.call_args_list[0].kwargs

        record_msg = file_writer_kwargs['record_msg']
        stream_schema = file_writer_kwargs['stream_schema']

        self.assertEqual(stream_schema, self.stream_schema_expected)

        self.assertMultilineTrimmed(record_msg.data['document_content'], self.document_content)

    @patch("destination_mariadb.common.sql.sql_processor.pd")
    def test_write_stragegy_replace(self, sqlproc_pd):
        self.testProcessor._table_exists = Mock(return_value=True)

        mock_dataframe = MagicMock()  # dataframe
        sqlproc_pd.read_json = Mock(return_value=mock_dataframe)

        # Mock away the batch handles.
        self.fileWriterMock.get_pending_batches = Mock(return_value=self.batches_to_finalize)

        # Mock away the _execute_sql
        sql_mock = Mock()
        self.testProcessor._execute_sql = sql_mock

        # Process the message
        for _ in self.testProcessor.process_airbyte_messages_as_generator(
                messages=self.input_messages,
                write_strategy=WriteStrategy.REPLACE,
        ):
            pass

        # Test that the SQL statements are correct

        self.assertEqual(sql_mock.call_count, 3)
        # now, check the sql statements which have been used, they are in .call_args_list


        sql_alter = """
            ALTER TABLE `users` RENAME TO users_deleteme;
            ALTER TABLE `users_123` RENAME TO users;
            DROP TABLE `users_deleteme`;
        """

        self.assertMultilineTrimmed(sql_mock.call_args_list[0].args[0], SQL_CREATE_STATEMENT)
        self.assertMultilineTrimmed(sql_mock.call_args_list[1].args[0], sql_alter)
        self.assertMultilineTrimmed(sql_mock.call_args_list[2].args[0], SQL_DESTORY_STATEMENT)

        # Test what the mock_dataframe's to_sql was called
        self.assertEqual(1, mock_dataframe.to_sql.call_count, "to_sql should be called exactly once")

        # Testing that the attempt to write the temporary file is correct
        self.assertEqual(1, self.fileWriterMock.process_record_message.call_count)
        file_writer_kwargs = self.fileWriterMock.process_record_message.call_args_list[0].kwargs

        record_msg = file_writer_kwargs['record_msg']
        stream_schema = file_writer_kwargs['stream_schema']

        self.assertEqual(stream_schema, self.stream_schema_expected)

        self.assertMultilineTrimmed(record_msg.data['document_content'], self.document_content)
