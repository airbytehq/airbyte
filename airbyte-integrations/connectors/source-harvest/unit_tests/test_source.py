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

    @patch("source_harvest.source.Users.read_records")
    def test_given_400_http_error_when_check_connection_then_raise_non_config_error(self, mocked_user_read_records) -> None:
        """
        Following https://github.com/airbytehq/airbyte/pull/35305 where no page alerts were emitted
        """
        mocked_user_read_records.side_effect = HTTPError(response=_a_response(400))

        with pytest.raises(Exception) as exception:
            self._source.check_connection(self._logger, self._config)
        assert not isinstance(exception, AirbyteTracedException) or exception.failure_type != FailureType.config_error

    @patch("source_harvest.source.Users.read_records")
    def test_given_401_http_error_when_check_connection_then_is_not_available(self, mocked_user_read_records) -> None:
        mocked_user_read_records.side_effect = HTTPError(response=_a_response(401))
        is_available, _ = self._source.check_connection(self._logger, self._config)
        assert not is_available

    @patch("source_harvest.source.Users.read_records")
    def test_given_403_http_error_when_check_connection_then_is_not_available(self, mocked_user_read_records) -> None:
        mocked_user_read_records.side_effect = HTTPError(response=_a_response(403))
        is_available, _ = self._source.check_connection(self._logger, self._config)
        assert not is_available

    @patch("source_harvest.source.Users.read_records")
    def test_given_404_http_error_when_check_connection_then_is_not_available(self, mocked_user_read_records) -> None:
        mocked_user_read_records.side_effect = HTTPError(response=_a_response(404))
        is_available, _ = self._source.check_connection(self._logger, self._config)
        assert not is_available
