#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pydantic
import pytest
from airbyte_cdk.models import ConnectorSpecification
from source_facebook_marketing import SourceFacebookMarketing
from source_facebook_marketing.spec import ConnectorConfig


@pytest.fixture(name="config")
def config_fixture():
    config = {
        "account_id": 123,
        "access_token": "TOKEN",
        "start_date": "2019-10-10T00:00:00",
        "end_date": "2020-10-10T00:00:00",
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

    def test_check_connection_end_date_before_start_date(self, api, config, logger_mock):
        config["start_date"] = "2019-10-10T00:00:00"
        config["end_date"] = "2019-10-09T00:00:00"

        with pytest.raises(ValueError, match="end_date must be equal or after start_date."):
            SourceFacebookMarketing().check_connection(logger_mock, config=config)

    def test_check_connection_empty_config(self, api, logger_mock):
        config = {}

        with pytest.raises(pydantic.ValidationError):
            SourceFacebookMarketing().check_connection(logger_mock, config=config)

        assert not api.called

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

        assert len(streams) == 15

    def test_spec(self):
        spec = SourceFacebookMarketing().spec()

        assert isinstance(spec, ConnectorSpecification)

    def test_update_insights_streams(self, api, config):
        config["custom_insights"] = [
            {"name": "test", "fields": ["account_id"], "breakdowns": ["ad_format_asset"], "action_breakdowns": ["action_device"]},
        ]
        streams = SourceFacebookMarketing().streams(config)
        config = ConnectorConfig.parse_obj(config)
        insights_args = dict(
            api=api,
            start_date=config.start_date,
            end_date=config.end_date,
        )
        assert SourceFacebookMarketing()._update_insights_streams(
            insights=config.custom_insights, default_args=insights_args, streams=streams
        )
