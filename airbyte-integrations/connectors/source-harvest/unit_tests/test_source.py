# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
import unittest
from unittest.mock import Mock, patch

import pytest
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import ConfiguredAirbyteCatalog, FailureType, Status, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from airbyte_cdk.utils import AirbyteTracedException
from config import ConfigBuilder
from requests import HTTPError
from source_harvest import SourceHarvest


def _a_response_with_error_code(status_code: int) -> HttpResponse:
    return HttpResponse(json.dumps(find_template(str(status_code), __file__)), status_code)

def _a_request() -> HttpMocker:
    return HttpRequest(
        url="https://api.harvestapp.com/v2/company",
        query_params="any query_parameters"
    )

def _catalog() -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream("company", SyncMode.full_refresh).build()

class SourceTest(unittest.TestCase):

    def setUp(self) -> None:
        self._source = SourceHarvest()
        self._logger = Mock(spec=AirbyteLogger)
        self._config = ConfigBuilder().build()

    def test_given_config_with_client_id_without_account_id_when_check_connection_then_not_available(self) -> None:
        config = ConfigBuilder().with_client_id("a client id").build()
        config.pop("account_id")

        is_available, error = self._source.check_connection(self._logger, config)
        assert not is_available
        assert error == "Unable to connect to stream company - Request to https://api.harvestapp.com/v2/company failed with status code 401 and error message invalid_token"

    def test_given_config_no_authentication_in_config_when_check_connection_then_not_available(self) -> None:
        config = ConfigBuilder().build()
        config["credentials"].pop("api_token", None)
        config["credentials"].pop("client_id", None)

        is_available, error = self._source.check_connection(self._logger, config)
        assert not is_available

    @HttpMocker()
    def test_given_400_http_error_read_then_raises_config_error(self, http_mocker: HttpMocker) -> None:

        http_mocker.get(
            _a_request(),
            _a_response_with_error_code(400)
        )

        output = read(self._source, self._config, _catalog(), state=None, expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type== FailureType.config_error

    @HttpMocker()
    def test_given_401_http_error_when_read_then_raises_config_error(self, http_mocker: HttpMocker) -> None:

        http_mocker.get(
            _a_request(),
            _a_response_with_error_code(401)
        )
        output = read(self._source, self._config, _catalog(), state=None, expecting_exception=True)
        print(output)

        assert output.errors[-1].trace.error.failure_type== FailureType.config_error

    @HttpMocker()
    def test_given_403_http_error_when_read_then_raises_config_error(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _a_request(),
            _a_response_with_error_code(403)
        )

        output = read(self._source, self._config, _catalog(), state=None, expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type== FailureType.config_error

    @HttpMocker()
    def test_given_404_http_error_when_read_then_raises_config_error(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            _a_request(),
            _a_response_with_error_code(404)
        )

        output = read(self._source, self._config, _catalog(), state=None, expecting_exception=True)
        assert output.errors[-1].trace.error.failure_type == FailureType.config_error
