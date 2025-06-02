import unittest
from unittest.mock import MagicMock, patch
import logging

from airbyte_cdk.models import (
    ConnectorSpecification,
    AirbyteConnectionStatus,
    AirbyteCatalog,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    SyncMode,
    AirbyteRecordMessage,
)
# Adjust the import path according to your project structure
# Assuming source_sap_hana.py is in the parent directory relative to the tests directory
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from source_sap_hana import SourceSapHana


class TestSourceSapHana(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger("airbyte")
        self.source = SourceSapHana()
        self.sample_config = {
            "host": "testhost",
            "port": 30015,
            "username": "testuser",
            "password": "testpassword",
            "database": "TESTDB"
        }

    def test_spec(self):
        spec = self.source.spec(self.logger)
        self.assertIsNotNone(spec)
        self.assertIsInstance(spec, ConnectorSpecification)
        self.assertIn("host", spec.connectionSpecification["properties"])
        self.assertIn("port", spec.connectionSpecification["properties"])
        self.assertIn("username", spec.connectionSpecification["properties"])
        self.assertIn("password", spec.connectionSpecification["properties"])
        self.assertIn("database", spec.connectionSpecification["properties"])
        self.assertEqual(spec.connectionSpecification["properties"]["password"].get("airbyte_secret"), True)

    @patch('source_sap_hana.hdbcli.dbapi.connect')
    def test_check_success(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        status = self.source.check(self.logger, self.sample_config)

        mock_connect.assert_called_once_with(
            address="testhost",
            port=30015,
            user="testuser",
            password="testpassword",
            databasename="TESTDB"
        )
        mock_connection.close.assert_called_once()
        self.assertEqual(status.status, "SUCCEEDED")

    @patch('source_sap_hana.hdbcli.dbapi.connect')
    def test_check_failure(self, mock_connect):
        mock_connect.side_effect = Exception("Connection Failed")

        status = self.source.check(self.logger, self.sample_config)

        mock_connect.assert_called_once_with(
            address="testhost",
            port=30015,
            user="testuser",
            password="testpassword",
            databasename="TESTDB"
        )
        self.assertEqual(status.status, "FAILED")
        self.assertIn("Connection Failed", status.message)

    @patch('source_sap_hana.hdbcli.dbapi.connect')
    def test_discover(self, mock_connect):
        mock_cursor = MagicMock()
        mock_cursor.description = [('COLUMN_NAME',), ('DATA_TYPE_NAME',)] # Simplified for this example
        # Schema, Table, Column, Type, Length, Scale, IsPK
        mock_cursor.__iter__.return_value = iter([
            ("SCHEMA1", "TABLE1", "COL1_ID", "INTEGER", 10, 0, True),
            ("SCHEMA1", "TABLE1", "COL2_NAME", "NVARCHAR", 50, 0, False),
            ("SCHEMA1", "TABLE2", "COL_A", "DATE", 10, 0, True),
            ("SCHEMA2", "TABLE3", "DATA_COL", "DECIMAL", 12, 2, False),
        ])

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        catalog = self.source.discover(self.logger, self.sample_config)

        self.assertIsNotNone(catalog)
        self.assertIsInstance(catalog, AirbyteCatalog)
        self.assertEqual(len(catalog.streams), 3)

        stream1 = next(s for s in catalog.streams if s.name == "TABLE1" and s.namespace == "SCHEMA1")
        stream2 = next(s for s in catalog.streams if s.name == "TABLE2" and s.namespace == "SCHEMA1")
        stream3 = next(s for s in catalog.streams if s.name == "TABLE3" and s.namespace == "SCHEMA2")

        self.assertIn("COL1_ID", stream1.json_schema["properties"])
        self.assertEqual(stream1.json_schema["properties"]["COL1_ID"]["type"], "integer")
        self.assertIn("COL2_NAME", stream1.json_schema["properties"])
        self.assertEqual(stream1.json_schema["properties"]["COL2_NAME"]["type"], "string")
        self.assertEqual(stream1.source_defined_primary_key, [["COL1_ID"]])


        self.assertIn("COL_A", stream2.json_schema["properties"])
        self.assertEqual(stream2.json_schema["properties"]["COL_A"]["type"], "string") # Mapped from DATE
        self.assertEqual(stream2.json_schema["properties"]["COL_A"]["format"], "date")
        self.assertEqual(stream2.source_defined_primary_key, [["COL_A"]])

        self.assertIn("DATA_COL", stream3.json_schema["properties"])
        self.assertEqual(stream3.json_schema["properties"]["DATA_COL"]["type"], "number") # Mapped from DECIMAL
        self.assertIsNone(stream3.source_defined_primary_key) # No PK for DATA_COL

        mock_connection.close.assert_called_once()
        mock_cursor.close.assert_called_once()


    @patch('source_sap_hana.hdbcli.dbapi.connect')
    def test_read(self, mock_connect):
        mock_cursor = MagicMock()
        # Mock cursor description for column names
        mock_cursor.description = [('ID',), ('NAME',), ('VALUE',)]
        # Mock row data
        mock_cursor.fetchone.side_effect = [
            (1, "Record1", 100.5),
            (2, "Record2", 200.0),
            None # End of data
        ]

        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Define a sample configured catalog
        configured_catalog = ConfiguredAirbyteCatalog(streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name="TEST_TABLE",
                    namespace="TEST_SCHEMA",
                    json_schema={"type": "object", "properties": {"ID": {"type": "integer"}, "NAME": {"type": "string"}, "VALUE": {"type": "number"}}},
                    supported_sync_modes=[SyncMode.full_refresh]
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=SyncMode.full_refresh # Not strictly needed for source tests but good practice
            )
        ])

        messages = list(self.source.read(self.logger, self.sample_config, configured_catalog, {}))

        self.assertEqual(len(messages), 2)

        msg1 = messages[0]
        self.assertIsInstance(msg1, AirbyteRecordMessage)
        self.assertEqual(msg1.stream, "TEST_TABLE")
        self.assertEqual(msg1.data["ID"], 1)
        self.assertEqual(msg1.data["NAME"], "Record1")
        self.assertEqual(msg1.data["VALUE"], 100.5)
        self.assertIsNotNone(msg1.emitted_at)

        msg2 = messages[1]
        self.assertIsInstance(msg2, AirbyteRecordMessage)
        self.assertEqual(msg2.stream, "TEST_TABLE")
        self.assertEqual(msg2.data["ID"], 2)
        self.assertEqual(msg2.data["NAME"], "Record2")
        self.assertEqual(msg2.data["VALUE"], 200.0)

        # Check if connect and close were called
        mock_connect.assert_called_once_with(
            address="testhost", port=30015, user="testuser", password="testpassword", databasename="TESTDB"
        )
        mock_cursor.execute.assert_called_once_with('SELECT * FROM "TEST_SCHEMA"."TEST_TABLE"')
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
