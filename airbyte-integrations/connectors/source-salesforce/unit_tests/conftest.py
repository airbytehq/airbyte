#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
import pathlib
from typing import Any, List, Mapping
from unittest.mock import Mock

import pytest
from config_builder import ConfigBuilder
from source_salesforce.api import Salesforce
from source_salesforce.source import SourceSalesforce

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.state_builder import StateBuilder


_ANY_CATALOG = CatalogBuilder().build()
_ANY_CONFIG = ConfigBuilder().build()
_ANY_STATE = StateBuilder().build()


@pytest.fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock


@pytest.fixture(scope="module")
def bulk_catalog():
    with (pathlib.Path(__file__).parent / "bulk_catalog.json").open() as f:
        data = json.loads(f.read())
    return ConfiguredAirbyteCatalogSerializer.load(data)


@pytest.fixture(scope="module")
def rest_catalog():
    with (pathlib.Path(__file__).parent / "rest_catalog.json").open() as f:
        data = json.loads(f.read())
    return ConfiguredAirbyteCatalogSerializer.load(data)


@pytest.fixture(scope="module")
def state() -> List[AirbyteStateMessage]:
    return (
        StateBuilder()
        .with_stream_state("Account", {"LastModifiedDate": "2021-10-01T21:18:20.000Z"})
        .with_stream_state("Asset", {"SystemModstamp": "2021-10-02T05:08:29.000Z"})
        .build()
    )


@pytest.fixture(scope="module")
def stream_config():
    """Generates streams settings for BULK logic"""
    return ConfigBuilder().build()


@pytest.fixture(scope="function")
def stream_config_date_format():
    """Generates streams settings with `start_date` in format YYYY-MM-DD"""
    config = ConfigBuilder().build()
    config["start_date"] = "2010-01-18"
    return config


@pytest.fixture(scope="module")
def stream_config_without_start_date():
    """Generates streams settings for REST logic without start_date"""
    config = ConfigBuilder().build()
    config.pop("start_date")
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "is_sandbox": False,
        "wait_timeout": 15,
    }


def mock_stream_api(stream_config: Mapping[str, Any], describe_response_data=None):
    sf_object = Salesforce(**stream_config)
    sf_object.login = Mock()
    sf_object.access_token = Mock()
    sf_object.instance_url = "https://fase-account.salesforce.com"

    response_data = {"fields": [{"name": "LastModifiedDate", "type": "string"}, {"name": "Id", "type": "string"}]}
    if describe_response_data:
        response_data = describe_response_data
    sf_object.describe = Mock(return_value=response_data)
    return sf_object


@pytest.fixture(scope="module")
def stream_api(stream_config):
    return mock_stream_api(stream_config)


@pytest.fixture(scope="module")
def stream_api_v2(stream_config):
    describe_response_data = {"fields": [{"name": "LastModifiedDate", "type": "string"}, {"name": "BillingAddress", "type": "address"}]}
    return mock_stream_api(stream_config, describe_response_data=describe_response_data)


@pytest.fixture(scope="module")
def stream_api_pk(stream_config):
    describe_response_data = {"fields": [{"name": "LastModifiedDate", "type": "string"}, {"name": "Id", "type": "string"}]}
    return mock_stream_api(stream_config, describe_response_data=describe_response_data)


@pytest.fixture(scope="module")
def stream_api_v2_too_many_properties(stream_config):
    describe_response_data = {"fields": [{"name": f"Property{str(i)}", "type": "string"} for i in range(Salesforce.REQUEST_SIZE_LIMITS)]}
    describe_response_data["fields"].extend([{"name": "BillingAddress", "type": "address"}])
    return mock_stream_api(stream_config, describe_response_data=describe_response_data)


@pytest.fixture(scope="module")
def stream_api_v2_pk_too_many_properties(stream_config):
    describe_response_data = {"fields": [{"name": f"Property{str(i)}", "type": "string"} for i in range(Salesforce.REQUEST_SIZE_LIMITS)]}
    describe_response_data["fields"].extend([{"name": "BillingAddress", "type": "address"}, {"name": "Id", "type": "string"}])
    return mock_stream_api(stream_config, describe_response_data=describe_response_data)


def generate_stream(stream_name, stream_config, stream_api, state=None, legacy=True):
    if state is None:
        state = _ANY_STATE

    stream = SourceSalesforce(_ANY_CATALOG, _ANY_CONFIG, state).generate_streams(stream_config, {stream_name: None}, stream_api)[0]
    if legacy and hasattr(stream, "_legacy_stream"):
        # Many tests are going through `generate_streams` to test things that are part of the legacy interface. To smooth the transition,
        # we will access the legacy stream through the StreamFacade private field
        return stream._legacy_stream
    return stream
