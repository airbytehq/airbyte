# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import unittest
from unittest.mock import Mock, patch

import pytest
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException
from config import ConfigBuilder
from requests import HTTPError
from source_harvest.source import SourceHarvest


def _a_response(status_code: int) -> requests.Response:
    response = Mock(spec=requests.Response)
    response.status_code = status_code
    response.url = "any url"
    response.reason = "any reason"
    return response


class SourceTest(unittest.TestCase):

    def setUp(self) -> None:
        self._source = SourceHarvest()
        self._logger = Mock(spec=AirbyteLogger)
        self._config = ConfigBuilder().build()

    def test_given_config_with_client_id_without_account_id_when_check_connection_then_raise_config_error(self) -> None:
        config = ConfigBuilder().with_client_id("a client id").build()
        config.pop("account_id")

        with pytest.raises(AirbyteTracedException) as exception_trace:
            self._source.check_connection(self._logger, config)
        assert exception_trace.value.failure_type == FailureType.config_error

    def test_given_config_no_authentication_in_config_when_check_connection_then_raise_config_error(self) -> None:
        config = ConfigBuilder().build()
        config.pop("api_token", None)
        config.pop("client_id", None)

        with pytest.raises(AirbyteTracedException) as exception_trace:
            self._source.check_connection(self._logger, config)
        assert exception_trace.value.failure_type == FailureType.config_error