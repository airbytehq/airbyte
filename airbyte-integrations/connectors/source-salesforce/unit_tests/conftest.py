#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import Mock

import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog
from source_salesforce.api import Salesforce
from source_salesforce.source import SourceSalesforce


@pytest.fixture(scope="module")
def configured_catalog():
    with open("unit_tests/configured_catalog.json") as f:
        data = json.loads(f.read())
    return ConfiguredAirbyteCatalog.parse_obj(data)


@pytest.fixture(scope="module")
def state():
    state = {"Account": {"LastModifiedDate": "2021-10-01T21:18:20.000Z"}, "Asset": {"SystemModstamp": "2021-10-02T05:08:29.000Z"}}
    return state


@pytest.fixture(scope="module")
def stream_config():
    """Generates streams settings for BULK logic"""
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "start_date": "2010-01-18T21:18:20Z",
        "is_sandbox": False,
        "wait_timeout": 15,
    }


@pytest.fixture(scope="module")
def stream_config_date_format():
    """Generates streams settings with `start_date` in format YYYY-MM-DD"""
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "start_date": "2010-01-18",
        "is_sandbox": False,
        "wait_timeout": 15,
    }


@pytest.fixture(scope="module")
def stream_config_without_start_date():
    """Generates streams settings for REST logic without start_date"""
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "is_sandbox": False,
        "wait_timeout": 15,
    }


def _stream_api(stream_config, describe_response_data=None):
    sf_object = Salesforce(**stream_config)
    sf_object.login = Mock()
    sf_object.access_token = Mock()
    sf_object.instance_url = "https://fase-account.salesforce.com"

    response_data = {"fields": [{"name": "LastModifiedDate", "type": "string"}]}
    if describe_response_data:
        response_data = describe_response_data
    sf_object.describe = Mock(return_value=response_data)
    return sf_object


@pytest.fixture(scope="module")
def stream_api(stream_config):
    return _stream_api(stream_config)


@pytest.fixture(scope="module")
def stream_api_v2(stream_config):
    describe_response_data = {"fields": [{"name": "LastModifiedDate", "type": "string"}, {"name": "BillingAddress", "type": "address"}]}
    return _stream_api(stream_config, describe_response_data=describe_response_data)


def generate_stream(stream_name, stream_config, stream_api, state=None):
    return SourceSalesforce.generate_streams(stream_config, {stream_name: None}, stream_api, state=state)[0]
