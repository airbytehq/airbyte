#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from copy import deepcopy

import pytest
from airbyte_cdk.models import AirbyteConnectionStatus, ConnectorSpecification, Status
from facebook_business import FacebookAdsApi, FacebookSession
from source_facebook_marketing import SourceFacebookMarketing
from source_facebook_marketing.spec import ConnectorConfig

from .utils import command_check


@pytest.fixture(name="config")
def config_fixture():
    config = {
        "account_id": "123",
        "access_token": "TOKEN",
        "start_date": "2019-10-10T00:00:00Z",
        "end_date": "2020-10-10T00:00:00Z",
    }

    return config


@pytest.fixture
def config_gen(config):
    def inner(**kwargs):
        new_config = deepcopy(config)
        # WARNING, no support deep dictionaries
        new_config.update(kwargs)
        return {k: v for k, v in new_config.items() if v is not ...}

    return inner


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
        api.assert_called_once_with(account_id="123", access_token="TOKEN", page_size=100)
        logger_mock.info.assert_called_once_with(f"Select account {api.return_value.account}")

    def test_check_connection_future_date_range(self, api, config, logger_mock):
        config["start_date"] = "2219-10-10T00:00:00"
        config["end_date"] = "2219-10-11T00:00:00"
        assert SourceFacebookMarketing().check_connection(logger_mock, config=config) == (
            False,
            "Date range can not be in the future.",
        )

    def test_check_connection_end_date_before_start_date(self, api, config, logger_mock):
        config["start_date"] = "2019-10-10T00:00:00"
        config["end_date"] = "2019-10-09T00:00:00"
        assert SourceFacebookMarketing().check_connection(logger_mock, config=config) == (
            False,
            "end_date must be equal or after start_date.",
        )

    def test_check_connection_empty_config(self, api, logger_mock):
        config = {}
        ok, error_msg = SourceFacebookMarketing().check_connection(logger_mock, config=config)

        assert not ok
        assert error_msg

    def test_check_connection_invalid_config(self, api, config, logger_mock):
        config.pop("start_date")
        ok, error_msg = SourceFacebookMarketing().check_connection(logger_mock, config=config)

        assert not ok
        assert error_msg

    def test_check_connection_exception(self, api, config, logger_mock):
        api.side_effect = RuntimeError("Something went wrong!")

        with pytest.raises(RuntimeError, match="Something went wrong!"):
            SourceFacebookMarketing().check_connection(logger_mock, config=config)

    def test_streams(self, config, api):
        streams = SourceFacebookMarketing().streams(config)

        assert len(streams) == 29

    def test_spec(self):
        spec = SourceFacebookMarketing().spec()

        assert isinstance(spec, ConnectorSpecification)

    def test_get_custom_insights_streams(self, api, config):
        config["custom_insights"] = [
            {"name": "test", "fields": ["account_id"], "breakdowns": ["ad_format_asset"], "action_breakdowns": ["action_device"]},
        ]
        config = ConnectorConfig.parse_obj(config)
        assert SourceFacebookMarketing().get_custom_insights_streams(api, config)

    def test_get_custom_insights_action_breakdowns_allow_empty(self, api, config):
        config["custom_insights"] = [
            {"name": "test", "fields": ["account_id"], "breakdowns": ["ad_format_asset"], "action_breakdowns": []},
        ]

        config["action_breakdowns_allow_empty"] = False
        streams = SourceFacebookMarketing().get_custom_insights_streams(api, ConnectorConfig.parse_obj(config))
        assert len(streams) == 1
        assert streams[0].breakdowns == ["ad_format_asset"]
        assert streams[0].action_breakdowns == ["action_type", "action_target_id", "action_destination"]

        config["action_breakdowns_allow_empty"] = True
        streams = SourceFacebookMarketing().get_custom_insights_streams(api, ConnectorConfig.parse_obj(config))
        assert len(streams) == 1
        assert streams[0].breakdowns == ["ad_format_asset"]
        assert streams[0].action_breakdowns == []


def test_check_config(config_gen, requests_mock):
    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FacebookAdsApi.API_VERSION}/act_123/", {})

    source = SourceFacebookMarketing()
    assert command_check(source, config_gen()) == AirbyteConnectionStatus(status=Status.SUCCEEDED, message=None)

    status = command_check(source, config_gen(start_date="2019-99-10T00:00:00Z"))
    assert status.status == Status.FAILED

    status = command_check(source, config_gen(end_date="2019-99-10T00:00:00Z"))
    assert status.status == Status.FAILED

    with pytest.raises(Exception):
        assert command_check(source, config_gen(start_date=...))

    assert command_check(source, config_gen(end_date=...)) == AirbyteConnectionStatus(status=Status.SUCCEEDED, message=None)
    assert command_check(source, config_gen(end_date="")) == AirbyteConnectionStatus(status=Status.SUCCEEDED, message=None)
