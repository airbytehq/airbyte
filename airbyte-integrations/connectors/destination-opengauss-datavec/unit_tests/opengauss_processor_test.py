#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from airbyte_cdk.models import AirbyteRecordMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream
from airbyte_cdk.destinations.vector_db_based.document_processor import ProcessingConfigModel

from destination_opengauss_datavec.opengauss_processor import (
    OpenGaussConfig,
    OpenGaussDataVecProcessor,
)
from destination_opengauss_datavec.globals import (
    CHUNK_ID_COLUMN,
    DOCUMENT_CONTENT_COLUMN,
    DOCUMENT_ID_COLUMN,
    EMBEDDING_COLUMN,
    METADATA_COLUMN,
)


class TestOpenGaussConfig(unittest.TestCase):
    """Test OpenGaussConfig class."""

    def setUp(self):
        self.config = OpenGaussConfig(
            host="MYACCOUNT",
            port=5432,
            database="MYDATABASE",
            username="MYUSERNAME",
            password="MYPASSWORD",
            schema_name="MYSCHEMA",
        )

    def test_get_sql_alchemy_url(self):
        """Test SQL Alchemy URL generation."""
        url = self.config.get_sql_alchemy_url()
        url_str = str(url)
        
        self.assertIn("opengauss+psycopg2://", url_str)
        self.assertIn("MYUSERNAME", url_str)            
        self.assertIn("MYPASSWORD", url_str)
        self.assertIn("5432", url_str)
        self.assertIn("MYDATABASE", url_str)
        # Note: schema_name is not part of the SQLAlchemy URL

    def test_get_database_name(self):
        """Test database name retrieval."""
        db_name = self.config.get_database_name()
        self.assertEqual(db_name, "MYDATABASE")

    def test_config_with_default_schema(self):
        """Test config initialization with default schema."""
        config = OpenGaussConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="testuser",
            password="testpass",
        )
        self.assertIsNotNone(config.schema_name)


class TestOpenGaussDataVecProcessor(unittest.TestCase):
    """Test OpenGaussDataVecProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.sql_config = OpenGaussConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="testuser",
            password="testpass",
            schema_name="public",
        )
        
        self.splitter_config = ProcessingConfigModel(
            chunk_size=1000,
            chunk_overlap=0,
            text_fields=["text"],
        )
        
        self.embedder_config = Mock()
        self.embedder_config.mode = "fake"
        
        # Create mock catalog
        self.mock_catalog = Mock(spec=ConfiguredAirbyteCatalog)
        self.mock_catalog.streams = []
        
        self.catalog_provider = Mock()
        self.catalog_provider.configured_catalog = self.mock_catalog
        
        self.temp_dir = Path("/tmp/test_opengauss")

        # Patch _ensure_schema_exists to avoid actual DB connections during initialization
        self.schema_exists_patcher = patch("destination_opengauss_datavec.common.sql.sql_processor.SqlProcessorBase._ensure_schema_exists")
        self.mock_schema_exists = self.schema_exists_patcher.start()

    def tearDown(self):
        """Tear down test fixtures."""
        self.schema_exists_patcher.stop()

    @patch("destination_opengauss_datavec.opengauss_processor.embedder")
    @patch("destination_opengauss_datavec.opengauss_processor.DocumentSplitter")
    def test_processor_initialization(self, mock_splitter, mock_embedder):
        """Test processor initialization."""
        processor = OpenGaussDataVecProcessor(
            sql_config=self.sql_config,
            splitter_config=self.splitter_config,
            embedder_config=self.embedder_config,
            catalog_provider=self.catalog_provider,
            temp_dir=self.temp_dir,
            temp_file_cleanup=True,
        )
        
        self.assertIsNotNone(processor)
        self.assertEqual(processor.sql_config, self.sql_config)
        self.assertEqual(processor.splitter_config, self.splitter_config)

    @patch("destination_opengauss_datavec.opengauss_processor.embedder")
    @patch("destination_opengauss_datavec.opengauss_processor.DocumentSplitter")
    def test_get_sql_column_definitions(self, mock_splitter, mock_embedder):
        """Test SQL column definitions."""
        # Mock embedder dimensions
        mock_embedder_instance = Mock()
        mock_embedder_instance.embedding_dimensions = 1536
        mock_embedder.create_from_config.return_value = mock_embedder_instance
        
        processor = OpenGaussDataVecProcessor(
            sql_config=self.sql_config,
            splitter_config=self.splitter_config,
            embedder_config=self.embedder_config,
            catalog_provider=self.catalog_provider,
            temp_dir=self.temp_dir,
        )
        
        columns = processor._get_sql_column_definitions("test_stream")
        
        self.assertIn(DOCUMENT_ID_COLUMN, columns)
        self.assertIn(CHUNK_ID_COLUMN, columns)
        self.assertIn(METADATA_COLUMN, columns)
        self.assertIn(DOCUMENT_CONTENT_COLUMN, columns)
        self.assertIn(EMBEDDING_COLUMN, columns)

    @patch("destination_opengauss_datavec.opengauss_processor.embedder")
    @patch("destination_opengauss_datavec.opengauss_processor.DocumentSplitter")
    def test_embedder_property(self, mock_splitter, mock_embedder):
        """Test embedder property."""
        mock_embedder_instance = Mock()
        mock_embedder.create_from_config.return_value = mock_embedder_instance
        
        processor = OpenGaussDataVecProcessor(
            sql_config=self.sql_config,
            splitter_config=self.splitter_config,
            embedder_config=self.embedder_config,
            catalog_provider=self.catalog_provider,
            temp_dir=self.temp_dir,
        )
        
        embedder = processor.embedder
        
        self.assertEqual(embedder, mock_embedder_instance)
        mock_embedder.create_from_config.assert_called()

    @patch("destination_opengauss_datavec.opengauss_processor.embedder")
    @patch("destination_opengauss_datavec.opengauss_processor.DocumentSplitter")
    def test_embedding_dimensions_property(self, mock_splitter, mock_embedder):
        """Test embedding dimensions property."""
        mock_embedder_instance = Mock()
        mock_embedder_instance.embedding_dimensions = 768
        mock_embedder.create_from_config.return_value = mock_embedder_instance
        
        processor = OpenGaussDataVecProcessor(
            sql_config=self.sql_config,
            splitter_config=self.splitter_config,
            embedder_config=self.embedder_config,
            catalog_provider=self.catalog_provider,
            temp_dir=self.temp_dir,
        )
        
        dimensions = processor.embedding_dimensions
        
        self.assertEqual(dimensions, 768)

    @patch("destination_opengauss_datavec.opengauss_processor.embedder")
    @patch("destination_opengauss_datavec.opengauss_processor.DocumentSplitter")
    def test_splitter_property(self, mock_splitter, mock_embedder):
        """Test splitter property."""
        mock_splitter_instance = Mock()
        mock_splitter.return_value = mock_splitter_instance
        
        processor = OpenGaussDataVecProcessor(
            sql_config=self.sql_config,
            splitter_config=self.splitter_config,
            embedder_config=self.embedder_config,
            catalog_provider=self.catalog_provider,
            temp_dir=self.temp_dir,
        )
        
        splitter = processor.splitter
        
        self.assertEqual(splitter, mock_splitter_instance)
        mock_splitter.assert_called_with(
            config=self.splitter_config,
            catalog=self.catalog_provider.configured_catalog,
        )

    @patch("destination_opengauss_datavec.opengauss_processor.embedder")
    @patch("destination_opengauss_datavec.opengauss_processor.DocumentSplitter")
    def test_create_document_id_with_primary_key(self, mock_splitter, mock_embedder):
        """Test document ID creation with primary key."""
        processor = OpenGaussDataVecProcessor(
            sql_config=self.sql_config,
            splitter_config=self.splitter_config,
            embedder_config=self.embedder_config,
            catalog_provider=self.catalog_provider,
            temp_dir=self.temp_dir,
        )
        
        # Mock _get_record_primary_key to return a value
        with patch.object(processor, '_get_record_primary_key', return_value="123"):
            record_msg = AirbyteRecordMessage(
                stream="test_stream",
                data={"id": 123, "name": "test"},
                emitted_at=1000,
            )
            
            doc_id = processor._create_document_id(record_msg)
            
            self.assertEqual(doc_id, "Stream_test_stream_Key_123")

    @patch("destination_opengauss_datavec.opengauss_processor.embedder")
    @patch("destination_opengauss_datavec.opengauss_processor.DocumentSplitter")
    def test_create_document_id_without_primary_key(self, mock_splitter, mock_embedder):
        """Test document ID creation without primary key."""
        processor = OpenGaussDataVecProcessor(
            sql_config=self.sql_config,
            splitter_config=self.splitter_config,
            embedder_config=self.embedder_config,
            catalog_provider=self.catalog_provider,
            temp_dir=self.temp_dir,
        )
        
        # Mock _get_record_primary_key to return None
        with patch.object(processor, '_get_record_primary_key', return_value=None):
            record_msg = AirbyteRecordMessage(
                stream="test_stream",
                data={"name": "test"},
                emitted_at=1000,
            )
            
            doc_id = processor._create_document_id(record_msg)
            
            # Should be a UUID-based string
            self.assertIsInstance(doc_id, str)
            self.assertTrue(len(doc_id) > 0)

    @patch("destination_opengauss_datavec.opengauss_processor.embedder")
    @patch("destination_opengauss_datavec.opengauss_processor.DocumentSplitter")
    def test_get_record_primary_key_with_keys(self, mock_splitter, mock_embedder):
        """Test getting record primary key with defined keys."""
        processor = OpenGaussDataVecProcessor(
            sql_config=self.sql_config,
            splitter_config=self.splitter_config,
            embedder_config=self.embedder_config,
            catalog_provider=self.catalog_provider,
            temp_dir=self.temp_dir,
        )
        
        # Mock _get_primary_keys to return keys
        with patch.object(processor, '_get_primary_keys', return_value=["id", "type"]):
            record_msg = AirbyteRecordMessage(
                stream="test_stream",
                data={"id": 123, "type": "user", "name": "test"},
                emitted_at=1000,
            )
            
            primary_key = processor._get_record_primary_key(record_msg)
            
            self.assertEqual(primary_key, "123_user")

    @patch("destination_opengauss_datavec.opengauss_processor.embedder")
    @patch("destination_opengauss_datavec.opengauss_processor.DocumentSplitter")
    def test_get_record_primary_key_without_keys(self, mock_splitter, mock_embedder):
        """Test getting record primary key without defined keys."""
        processor = OpenGaussDataVecProcessor(
            sql_config=self.sql_config,
            splitter_config=self.splitter_config,
            embedder_config=self.embedder_config,
            catalog_provider=self.catalog_provider,
            temp_dir=self.temp_dir,
        )
        
        # Mock _get_primary_keys to return empty list
        with patch.object(processor, '_get_primary_keys', return_value=[]):
            record_msg = AirbyteRecordMessage(
                stream="test_stream",
                data={"name": "test"},
                emitted_at=1000,
            )
            
            primary_key = processor._get_record_primary_key(record_msg)
            
            self.assertIsNone(primary_key)

    @patch("destination_opengauss_datavec.opengauss_processor.embedder")
    @patch("destination_opengauss_datavec.opengauss_processor.DocumentSplitter")
    def test_get_record_primary_key_with_missing_field(self, mock_splitter, mock_embedder):
        """Test getting record primary key when field is missing."""
        processor = OpenGaussDataVecProcessor(
            sql_config=self.sql_config,
            splitter_config=self.splitter_config,
            embedder_config=self.embedder_config,
            catalog_provider=self.catalog_provider,
            temp_dir=self.temp_dir,
        )
        
        # Mock _get_primary_keys to return keys that don't exist in data
        with patch.object(processor, '_get_primary_keys', return_value=["missing_field"]):
            record_msg = AirbyteRecordMessage(
                stream="test_stream",
                data={"name": "test"},
                emitted_at=1000,
            )
            
            primary_key = processor._get_record_primary_key(record_msg)
            
            self.assertEqual(primary_key, "__not_found__")

    @patch("destination_opengauss_datavec.opengauss_processor.embedder")
    @patch("destination_opengauss_datavec.opengauss_processor.DocumentSplitter")
    def test_process_record_message(self, mock_splitter, mock_embedder):
        """Test processing a record message."""
        # Create mock document chunk
        mock_chunk = Mock()
        mock_chunk.page_content = "Test content"
        mock_chunk.metadata = {"source": "test"}
        
        # Mock splitter
        mock_splitter_instance = Mock()
        mock_splitter_instance.process.return_value = ([mock_chunk], None)
        mock_splitter.return_value = mock_splitter_instance
        
        # Mock embedder
        mock_embedder_instance = Mock()
        mock_embedder_instance.embedding_dimensions = 768
        mock_embedder_instance.embed_documents.return_value = [[0.1] * 768]
        mock_embedder.create_from_config.return_value = mock_embedder_instance
        
        processor = OpenGaussDataVecProcessor(
            sql_config=self.sql_config,
            splitter_config=self.splitter_config,
            embedder_config=self.embedder_config,
            catalog_provider=self.catalog_provider,
            temp_dir=self.temp_dir,
        )
        
        # Mock file writer
        processor.file_writer = Mock()
        
        # Mock _create_document_id
        with patch.object(processor, '_create_document_id', return_value="doc_123"):
            record_msg = AirbyteRecordMessage(
                stream="test_stream",
                data={"text": "Test content"},
                emitted_at=1000,
            )
            
            processor.process_record_message(
                record_msg=record_msg,
                stream_schema={"type": "object"},
            )
            
            # Verify file writer was called
            processor.file_writer.process_record_message.assert_called_once()
            
            # Verify the call arguments
            call_args = processor.file_writer.process_record_message.call_args
            processed_record = call_args.kwargs['record_msg']
            
            self.assertEqual(processed_record.stream, "test_stream")
            self.assertIn(DOCUMENT_ID_COLUMN, processed_record.data)
            self.assertIn(CHUNK_ID_COLUMN, processed_record.data)
            self.assertIn(METADATA_COLUMN, processed_record.data)
            self.assertIn(DOCUMENT_CONTENT_COLUMN, processed_record.data)
            self.assertIn(EMBEDDING_COLUMN, processed_record.data)

    @patch("destination_opengauss_datavec.opengauss_processor.embedder")
    @patch("destination_opengauss_datavec.opengauss_processor.DocumentSplitter")
    def test_add_missing_columns_to_table(self, mock_splitter, mock_embedder):
        """Test add missing columns to table (should be no-op)."""
        processor = OpenGaussDataVecProcessor(
            sql_config=self.sql_config,
            splitter_config=self.splitter_config,
            embedder_config=self.embedder_config,
            catalog_provider=self.catalog_provider,
            temp_dir=self.temp_dir,
        )
        
        # This should not raise any errors (it's a no-op)
        processor._add_missing_columns_to_table(
            stream_name="test_stream",
            table_name="test_table",
        )

    @patch("destination_opengauss_datavec.opengauss_processor.insert")
    @patch("destination_opengauss_datavec.opengauss_processor.select")
    @patch("destination_opengauss_datavec.opengauss_processor.delete")
    @patch("destination_opengauss_datavec.opengauss_processor.embedder")
    @patch("destination_opengauss_datavec.opengauss_processor.DocumentSplitter")
    def test_emulated_merge_temp_table_to_final_table(self, mock_splitter, mock_embedder, mock_delete, mock_select, mock_insert):
        """Test emulated merge operation."""
        # Mock embedder for _get_sql_column_definitions
        mock_embedder_instance = Mock()
        mock_embedder_instance.embedding_dimensions = 768
        mock_embedder.create_from_config.return_value = mock_embedder_instance
        
        processor = OpenGaussDataVecProcessor(
            sql_config=self.sql_config,
            splitter_config=self.splitter_config,
            embedder_config=self.embedder_config,
            catalog_provider=self.catalog_provider,
            temp_dir=self.temp_dir,
        )
        
        # Mock the required methods
        mock_final_table = Mock()
        mock_temp_table = Mock()

        # Configure mocks to behave like dictionaries for column access
        mock_final_table.c = MagicMock()
        mock_final_table.c.__getitem__.return_value = Mock()
        mock_temp_table.c = MagicMock()
        mock_temp_table.c.__getitem__.return_value = Mock()
        
        with patch.object(processor, '_get_table_by_name') as mock_get_table, \
             patch.object(processor, 'get_sql_connection') as mock_get_connection:
            
            # Set up mock returns
            mock_get_table.side_effect = lambda name: (
                mock_final_table if name == "final_table" else mock_temp_table
            )
            
            mock_connection = Mock()
            mock_get_connection.return_value.__enter__ = Mock(return_value=mock_connection)
            mock_get_connection.return_value.__exit__ = Mock(return_value=False)
            
            # Call the method
            processor._emulated_merge_temp_table_to_final_table(
                stream_name="test_stream",
                temp_table_name="temp_table",
                final_table_name="final_table",
            )
            
            # Verify connection execute was called twice (delete + insert)
            self.assertEqual(mock_connection.execute.call_count, 2)


if __name__ == "__main__":
    unittest.main()

