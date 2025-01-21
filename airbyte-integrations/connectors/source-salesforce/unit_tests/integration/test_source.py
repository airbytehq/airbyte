# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase

import pytest
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from config_builder import ConfigBuilder
from integration.utils import create_base_url, given_authentication, given_stream
from salesforce_describe_response_builder import SalesforceDescribeResponseBuilder
from source_salesforce import SourceSalesforce

_CLIENT_ID = "a_client_id"
_CLIENT_SECRET = "a_client_secret"
_FIELD_NAME = "a_field_name"
_INSTANCE_URL = "https://instance.salesforce.com"
_REFRESH_TOKEN = "a_refresh_token"
_STREAM_NAME = "StreamName"

_BASE_URL = create_base_url(_INSTANCE_URL)


class StreamGenerationTest(TestCase):

    def setUp(self) -> None:
        self._config = ConfigBuilder().client_id(_CLIENT_ID).client_secret(_CLIENT_SECRET).refresh_token(_REFRESH_TOKEN).build()
        self._source = SourceSalesforce(
            CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(),
            self._config,
            StateBuilder().build()
        )

        self._http_mocker = HttpMocker()
        self._http_mocker.__enter__()

    def tearDown(self) -> None:
        self._http_mocker.__exit__(None, None, None)

    def test_given_transient_error_fetching_schema_when_streams_then_retry(self) -> None:
        given_authentication(self._http_mocker, _CLIENT_ID, _CLIENT_SECRET, _REFRESH_TOKEN, _INSTANCE_URL)
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/sobjects"),
            HttpResponse(json.dumps({"sobjects": [{"name": _STREAM_NAME, "queryable": True}]})),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/sobjects/{_STREAM_NAME}/describe"),
            [
                HttpResponse("", status_code=406),
                SalesforceDescribeResponseBuilder().field("a_field_name").build()
            ]
        )

        streams = self._source.streams(self._config)

        assert len(streams) == 2  # _STREAM_NAME and Describe which is always added
        assert _FIELD_NAME in next(filter(lambda stream: stream.name == _STREAM_NAME, streams)).get_json_schema()["properties"]

    def test_given_errors_fetching_schema_when_streams_then_raise_exception(self) -> None:
        given_authentication(self._http_mocker, _CLIENT_ID, _CLIENT_SECRET, _REFRESH_TOKEN, _INSTANCE_URL)
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/sobjects"),
            HttpResponse(json.dumps({"sobjects": [{"name": _STREAM_NAME, "queryable": True}]})),
        )
        self._http_mocker.get(
            HttpRequest(f"{_BASE_URL}/sobjects/{_STREAM_NAME}/describe"),
            HttpResponse("", status_code=406),
        )

        with pytest.raises(AirbyteTracedException) as exception:
            self._source.streams(self._config)

        assert exception.value.failure_type == FailureType.system_error
