#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
import requests_mock
from airbyte_cdk.models import SyncMode
from requests.exceptions import HTTPError
from source_salesforce.api import Salesforce
from source_salesforce.source import SourceSalesforce
from source_salesforce.streams import BulkIncrementalSalesforceStream, BulkSalesforceStream, IncrementalSalesforceStream, SalesforceStream


@pytest.fixture(scope="module")
def stream_bulk_config():
    """Generates streams settings for BULK logic"""
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "start_date": "2010-01-18T21:18:20Z",
        "is_sandbox": False,
        "wait_timeout": 15,
        "api_type": "BULK",
    }


@pytest.fixture(scope="module")
def stream_bulk_config_without_start_date():
    """Generates streams settings for BULK logic without start_date"""
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "is_sandbox": False,
        "wait_timeout": 15,
        "api_type": "BULK",
    }


@pytest.fixture(scope="module")
def stream_rest_config():
    """Generates streams settings for BULK logic"""
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "start_date": "2010-01-18T21:18:20Z",
        "is_sandbox": False,
        "wait_timeout": 15,
        "api_type": "REST",
    }


@pytest.fixture(scope="module")
def stream_rest_config_date_format():
    """Generates streams settings with `start_date` in format YYYY-MM-DD"""
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "start_date": "2010-01-18",
        "is_sandbox": False,
        "wait_timeout": 15,
        "api_type": "REST",
    }


@pytest.fixture(scope="module")
def stream_rest_config_without_start_date():
    """Generates streams settings for REST logic without start_date"""
    return {
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
        "is_sandbox": False,
        "wait_timeout": 15,
        "api_type": "REST",
    }


def _stream_api(stream_config):
    sf_object = Salesforce(**stream_config)
    sf_object.login = Mock()
    sf_object.access_token = Mock()
    sf_object.instance_url = "https://fase-account.salesforce.com"
    sf_object.describe = Mock(return_value={"fields": [{"name": "LastModifiedDate", "type": "string"}]})
    return sf_object


@pytest.fixture(scope="module")
def stream_rest_api(stream_rest_config):
    return _stream_api(stream_rest_config)


@pytest.fixture(scope="module")
def stream_bulk_api(stream_bulk_config):
    return _stream_api(stream_bulk_config)


def _generate_stream(stream_name, stream_config, stream_api):
    return SourceSalesforce.generate_streams(stream_config, [stream_name], stream_api)[0]


@pytest.mark.parametrize(
    "api_type,stream_name,expected_cls",
    [
        ("BULK", "Account", BulkIncrementalSalesforceStream),
        ("BULK", "FormulaFunctionAllowedType", BulkSalesforceStream),
        ("REST", "ActiveFeatureLicenseMetric", IncrementalSalesforceStream),
        ("REST", "AppDefinition", SalesforceStream),
    ],
)
def test_stream_generator(api_type, stream_name, expected_cls, stream_bulk_config, stream_bulk_api, stream_rest_config, stream_rest_api):
    stream_config, stream_api = (stream_rest_config, stream_rest_api) if api_type == "REST" else (stream_bulk_config, stream_bulk_api)
    stream = _generate_stream(stream_name, stream_config, stream_api)
    assert stream.name == stream_name
    assert isinstance(stream, expected_cls)


def test_bulk_sync_creation_failed(stream_bulk_config, stream_bulk_api):
    stream: BulkIncrementalSalesforceStream = _generate_stream("Account", stream_bulk_config, stream_bulk_api)
    with requests_mock.Mocker() as m:
        m.register_uri("POST", stream.path(), status_code=400, json=[{"message": "test_error"}])
        with pytest.raises(HTTPError) as err:
            next(stream.read_records(sync_mode=SyncMode.full_refresh))
        assert err.value.response.json()[0]["message"] == "test_error"


def test_bulk_sync_unsupported_stream(stream_bulk_config, stream_bulk_api, caplog):
    stream_name = "AcceptedEventRelation"
    stream: BulkIncrementalSalesforceStream = _generate_stream(stream_name, stream_bulk_config, stream_bulk_api)
    with requests_mock.Mocker() as m:
        m.register_uri(
            "POST",
            stream.path(),
            status_code=400,
            json=[{"errorCode": "INVALIDENTITY", "message": f"Entity '{stream_name}' is not supported by the Bulk API."}],
        )
        list(stream.read_records(sync_mode=SyncMode.full_refresh))

        logs = caplog.records

        assert logs
        assert logs[1].levelname == "ERROR"
        assert (
            logs[1].msg
            == f"Cannot receive data for stream '{stream_name}' using BULK API, error message: 'Entity '{stream_name}' is not supported by the Bulk API.'"
        )
