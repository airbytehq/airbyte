# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from unittest import TestCase
from unittest.mock import Mock, patch

import pytest
from config_builder import ConfigBuilder
from requests import exceptions
from salesforce_describe_response_builder import SalesforceDescribeResponseBuilder
from source_salesforce import SourceSalesforce
from source_salesforce.source import AirbyteStopSync

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from integration.utils import create_base_url, given_authentication


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
            CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build(), self._config, StateBuilder().build()
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
            [HttpResponse("", status_code=406), SalesforceDescribeResponseBuilder().field("a_field_name").build()],
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

    def test_read_stream_with_malformed_json_response_error_then_raise_exception(self) -> None:
        mock_response = Mock()
        mock_response.json.side_effect = exceptions.JSONDecodeError("Expecting value", "<html>Error</html>", 0)
        mock_response.url = _BASE_URL
        http_error = exceptions.HTTPError(response=mock_response)

        with patch(
            "airbyte_cdk.sources.concurrent_source.concurrent_source_adapter.ConcurrentSourceAdapter._read_stream"
        ) as mock_read_stream:
            mock_read_stream.side_effect = http_error
            with pytest.raises(exceptions.HTTPError) as exception:
                list(self._source._read_stream(Mock(), Mock(), Mock(), Mock(), Mock()))

        assert type(exception.value.__cause__) == exceptions.JSONDecodeError
        assert exception.value.response.url == _BASE_URL
        assert type(exception.value) == exceptions.HTTPError
        assert exception.value == http_error

    def test_read_stream_with_correct_json_response_error_then_raise_exception(self) -> None:
        mock_response = Mock()
        mock_response.json.return_value = [{"errorCode": "REQUEST_LIMIT_EXCEEDED"}]
        mock_response.url = _BASE_URL
        http_error = exceptions.HTTPError(response=mock_response)

        with patch(
            "airbyte_cdk.sources.concurrent_source.concurrent_source_adapter.ConcurrentSourceAdapter._read_stream"
        ) as mock_read_stream:
            mock_read_stream.side_effect = http_error
            with pytest.raises(exceptions.HTTPError) as exception:
                list(self._source._read_stream(Mock(), Mock(), Mock(), Mock(), Mock()))

        assert exception.value.response.json()[0]["errorCode"] == "REQUEST_LIMIT_EXCEEDED"
        assert exception.value.response.url == _BASE_URL
        assert exception.value == http_error
        assert type(exception.value) == exceptions.HTTPError

    def test_read_stream_with_forbidden_and_limit_exceeded_error_code_then_raise_exception(self) -> None:
        mock_response = Mock()
        mock_response.json.return_value = [{"errorCode": "REQUEST_LIMIT_EXCEEDED"}]
        mock_response.url = _BASE_URL
        mock_response.status_code = 403
        http_error = exceptions.HTTPError(response=mock_response)

        with patch(
            "airbyte_cdk.sources.concurrent_source.concurrent_source_adapter.ConcurrentSourceAdapter._read_stream"
        ) as mock_read_stream:
            mock_read_stream.side_effect = http_error
            with pytest.raises(AirbyteStopSync) as exception:
                list(self._source._read_stream(Mock(), Mock(), Mock(), Mock(), Mock()))

        assert type(exception.value) == AirbyteStopSync
