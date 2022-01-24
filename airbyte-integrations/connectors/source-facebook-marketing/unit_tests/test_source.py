#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pydantic
import pytest
from airbyte_cdk.models import ConnectorSpecification
from source_facebook_marketing import SourceFacebookMarketing


@pytest.fixture(name="config")
def config_fixture():
    config = {
        "account_id": 123,
        "access_token": "TOKEN",
        "start_date": "2019-10-10T00:00:00"
    }

    return config


@pytest.fixture(name="api")
def api_fixture(mocker):
    api_mock = mocker.patch("source_facebook_marketing.source.API")
    api_mock.return_value = mocker.Mock(account=123)
    return api_mock


@pytest.fixture(name="logger_mock")
def logger_mock_fixture(mocker):
    return mocker.patch("source_facebook_marketing.source.logger")

class TestSourceFacebookMarketing:
    def test_check_connection_ok(self, api, config, logger_mock):
        ok, error_msg = SourceFacebookMarketing().check_connection(logger_mock, config=config)

        assert ok
        assert not error_msg
        api.assert_called_once_with(account_id="123", access_token="TOKEN")
        logger_mock.info.assert_called_once_with(f"Select account {api.return_value.account}")

    def test_check_connection_invalid_config(self, api, config, logger_mock):
        config.pop("start_date")

        with pytest.raises(pydantic.ValidationError):
            SourceFacebookMarketing().check_connection(logger_mock, config=config)

        assert not api.called

    def test_check_connection_exception(self, api, config, logger_mock):
        api.side_effect = RuntimeError("Something went wrong!")

        with pytest.raises(RuntimeError, match="Something went wrong!"):
            SourceFacebookMarketing().check_connection(logger_mock, config=config)

    def test_streams(self, config, api):
        streams = SourceFacebookMarketing().streams(config)

        assert len(streams) == 12

    def test_spec(self):
        spec = SourceFacebookMarketing().spec()

        assert isinstance(spec, ConnectorSpecification)
