#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
import csv
import pytest
import boto3
import unittest
from typing import Any, Mapping
from urllib.parse import urlparse, parse_qs
from moto import mock_secretsmanager
from unittest.mock import patch, MagicMock

from source_shopify.config import AWSClient, DatabaseClient
from source_shopify.constants import ADVERTISERS_QUERY, SHOPIFY_ACCESS_TOKEN_PATH


class TestDatabaseClient(unittest.TestCase):

    def setUp(self):
        self.config = {
            "db_uri": "mysql://user:password@localhost:3306/testdb"
        }
        # Create a test CSV file
        self.csv_file_path = "test_shopify_stores.csv"
        with open(self.csv_file_path, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["advertiser_homepage", "affiliateId"])
            writer.writeheader()
            writer.writerow({"advertiser_homepage": "liana-clothing", "affiliateId": "1234"})
            writer.writerow({"advertiser_homepage": "adriana-shoes", "affiliateId": "123456"})

    def tearDown(self):
        # Clean up the test CSV file
        if os.path.exists(self.csv_file_path):
            os.remove(self.csv_file_path)

    @patch('mysql.connector.connect')
    def test_create_connection(self, mock_connect):
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        client = DatabaseClient(self.config)

        # Assert that the connection was created
        self.assertIsNotNone(client.connection)
        mock_connect.assert_called_once_with(
            host='localhost',
            user='user',
            password='password',
            database='testdb'
        )

    @patch('mysql.connector.connect')
    def test_get_shopify_store_info(self, mock_connect):
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        with open(self.csv_file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            mock_results = list(csv_reader)

        mock_cursor.fetchall.return_value = mock_results

        client = DatabaseClient(self.config)
        results = client._get_shopify_store_info()

        # Assert the results
        self.assertEqual(len(results), 2)
        assert results[0]["advertiser_homepage"] == "liana-clothing"
        assert results[1]["affiliateId"] == "123456"
        mock_cursor.execute.assert_called_once()  # Check if the query was executed

    @patch('mysql.connector.connect')
    def test_connection_error(self, mock_connect):
        mock_connect.side_effect = Exception("Connection failed")

        # Assert that an exception is raised
        with self.assertRaises(Exception):
            DatabaseClient(self.config)

    def test_extract_db_info(self):
        client = DatabaseClient(self.config)
        db_info = client.extract_db_info(self.config["db_uri"])

        self.assertEqual(db_info['scheme'], 'mysql')
        self.assertEqual(db_info['username'], 'user')
        self.assertEqual(db_info['password'], 'password')
        self.assertEqual(db_info['host'], 'localhost')
        self.assertEqual(db_info['port'], 3306)
        self.assertEqual(db_info['database'], 'testdb')


@pytest.fixture
def aws_client():
    config = {
        "secret_manager_account": "123456789012",
        "aws_access_key_id": "fake-access-key",
        "aws_secret_access_key": "fake-secret-key",
        "aws_session_token": "fake-session-token",
        "env": "test",
    }

    return AWSClient(config)

def test_get_shopify_token(aws_client):
        with mock_secretsmanager():
            client = boto3.client('secretsmanager', region_name="us-east-1")

            shopify_id = "shop123"
            secret_id = SHOPIFY_ACCESS_TOKEN_PATH.format(account_id = "123456789012")
            secret_id = secret_id.format(env = "test", shop_id = shopify_id)
            secret_value = "fake-shopify-token"

            # Create a mock secret
            client.create_secret(
                Name=secret_id,
                SecretString=secret_value
            )
            result = aws_client._get_shopify_token(shopify_id)

            assert result == secret_value

def test_get_shopify_token_not_found(aws_client):

    with mock_secretsmanager():
        client = boto3.client('secretsmanager', region_name="us-east-1")

        # Test with a non-existent shopify_id
        shopify_id = "non_existent_shop"

        result = aws_client._get_shopify_token(shopify_id)

        # Assert the method returns None when the secret is not found
        assert result is None