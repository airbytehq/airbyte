#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import pytest
from typing import Any, Mapping
from unittest.mock import patch, MagicMock

from airbyte_cdk.models import OrchestratorType, Type
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources import Source
from source_shopify.config import LTKShopifyConfigCreator, ConfigCreator
from source_shopify.source import SourceShopify
from source_shopify.constants import ADVERTISERS_QUERY, SHOPIFY_ACCESS_TOKEN_PATH

# BASE ARGS
CMD = "check"
TEST_CONFIG_PATH = "unit_tests/test_migrations/test_config.json"
NEW_TEST_CONFIG_PATH = "unit_tests/test_migrations/test_new_config.json"
SOURCE_INPUT_ARGS = [CMD, "--config", TEST_CONFIG_PATH]
SOURCE: Source = SourceShopify()


# HELPERS
def load_config(config_path: str = TEST_CONFIG_PATH) -> Mapping[str, Any]:
    with open(config_path, "r") as config:
        return json.load(config)

def create_config():
    return ConfigCreator()


@pytest.mark.parametrize(
    "db_uri, expected",
    [
        (
            "mysql://user:password@localhost:3306/mydb",
            {
                'scheme': 'mysql',
                'username': 'user',
                'password': 'password',
                'host': 'localhost',
                'port': 3306,
                'database': 'mydb',
                'query_params': {}
            }
        ),
        (
            "postgresql://admin:secret@db.example.com:5432/sampledb?sslmode=require",
            {
                'scheme': 'postgresql',
                'username': 'admin',
                'password': 'secret',
                'host': 'db.example.com',
                'port': 5432,
                'database': 'sampledb',
                'query_params': {'sslmode': ['require']}
            }
        )
    ]
)

def test_extract_db_info(db_uri, expected):
    cfg = create_config()
    result = cfg.extract_db_info(db_uri)
    assert result == expected

@patch("boto3.Session")
def test_get_shopify_token(mock_boto_session):
    config_creator = ConfigCreator()
    config_creator.env = "local"
    aws_credentials = {
        'aws_access_key_id': 'fake_access_key',
        'aws_secret_access_key': 'fake_secret_key',
        'aws_session_token': 'fake_session_token'
    }

    # Mock the response from AWS Secrets Manager
    mock_client = MagicMock()
    mock_client.get_secret_value.return_value = {"SecretString": "fake_token"}
    mock_boto_session.return_value.client.return_value = mock_client

    token = config_creator._get_shopify_token("123", aws_credentials)

    assert token == "fake_token"
    mock_boto_session.assert_called_once()
    mock_client.get_secret_value.assert_called_once_with(SecretId=SHOPIFY_ACCESS_TOKEN_PATH.format("123"))

@patch("mysql.connector.connect")
def test_get_shopify_store_info(mock_mysql_connect):
    config_creator = ConfigCreator()
    config_creator.db_info = {
        'host': 'localhost',
        'username': 'user',
        'password': 'password',
        'database': 'mydb'
    }

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_mysql_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        {'affiliateId': '123', 'advertiser_homepage': 'https://store1.myshopify.com'}
    ]
    mock_conn.is_connected.return_value = True

    result = config_creator._get_shopify_store_info()

    assert result == [{'affiliateId': '123', 'advertiser_homepage': 'https://store1.myshopify.com'}]
    mock_mysql_connect.assert_called_once()
    mock_cursor.execute.assert_called_once_with(ADVERTISERS_QUERY)

@patch("source_shopify.config.ConfigCreator._get_shopify_token")
@patch("source_shopify.config.ConfigCreator._get_shopify_store_info")
def test_gatherShopifyStores(mock_get_shopify_store_info, mock_get_shopify_token):
    config_creator = ConfigCreator()
    db_uri = "mysql://user:password@localhost:3306/mydb"
    env = "local"
    aws_credentials = {
        'aws_access_key_id': 'fake_access_key',
        'aws_secret_access_key': 'fake_secret_key',
        'aws_session_token': 'fake_session_token'
    }

    mock_get_shopify_store_info.return_value = [
        {'affiliateId': '123', 'advertiser_homepage': 'https://store1.myshopify.com'},
        {'affiliateId': '456', 'advertiser_homepage': 'https://store2.myshopify.com'}
    ]
    mock_get_shopify_token.side_effect = ["fake_token_1", None]  # Second call fails

    shops = config_creator.gatherShopifyStores(db_uri, env, aws_credentials)

    assert len(shops) == 1  # Only the first store should be included
    assert shops[0]['shop'] == 'store1'
    assert shops[0]['credentials']['api_password'] == 'fake_token_1'
    mock_get_shopify_store_info.assert_called_once()
    mock_get_shopify_token.assert_any_call('123', aws_credentials)
    mock_get_shopify_token.assert_any_call('456', aws_credentials)

def test_adjust_config():
    config_instance = LTKShopifyConfigCreator()
    with patch('airbyte_cdk.entrypoint.AirbyteEntrypoint') as mock_entrypoint, \
        patch.object(LTKShopifyConfigCreator, 'modify_and_save') as mock_modify_save:
        
        # Mock the return value for extract_config
        mock_entrypoint_instance = mock_entrypoint.return_value
        mock_entrypoint_instance.extract_config.return_value = TEST_CONFIG_PATH

        LTKShopifyConfigCreator.adjustConfig(SOURCE_INPUT_ARGS, SOURCE)

        test_migrated_config = load_config()

        # check migrated property
        assert "shops" in test_migrated_config
        # check the data type
        assert isinstance(test_migrated_config["shops"], list)
        assert len(test_migrated_config["shops"]) == 1   
