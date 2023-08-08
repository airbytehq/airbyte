#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from copy import deepcopy

import pytest
from airbyte_cdk.models import AirbyteConnectionStatus, ConnectorSpecification, Status
from facebook_business import FacebookAdsApi, FacebookSession
from source_facebook_marketing import SourceFacebookMarketing
from source_facebook_marketing.spec import ConnectorConfig
from source_facebook_marketing.streams.common import AccountTypeException

from .utils import command_check


@pytest.fixture(name="config")
def config_fixture(requests_mock):
    config = {
        "account_id": "123",
        "access_token": "TOKEN",
        "start_date": "2019-10-10T00:00:00Z",
        "end_date": "2020-10-10T00:00:00Z",
    }
    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FacebookAdsApi.API_VERSION}/act_123/", {})
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


@pytest.fixture
def fb_marketing():
    return SourceFacebookMarketing()


class TestSourceFacebookMarketing:
    def test_check_connection_ok(self, config, logger_mock, fb_marketing):
        ok, error_msg = fb_marketing.check_connection(logger_mock, config=config)

        assert ok
        assert not error_msg

    def test_check_connection_future_date_range(self, api, config, logger_mock, fb_marketing):
        config["start_date"] = "2219-10-10T00:00:00"
        config["end_date"] = "2219-10-11T00:00:00"
        assert fb_marketing.check_connection(logger_mock, config=config) == (
            False,
            "Date range can not be in the future.",
        )

    def test_check_connection_end_date_before_start_date(self, api, config, logger_mock, fb_marketing):
        config["start_date"] = "2019-10-10T00:00:00"
        config["end_date"] = "2019-10-09T00:00:00"
        assert fb_marketing.check_connection(logger_mock, config=config) == (
            False,
            "end_date must be equal or after start_date.",
        )

    def test_check_connection_empty_config(self, api, logger_mock, fb_marketing):
        config = {}
        ok, error_msg = fb_marketing.check_connection(logger_mock, config=config)

        assert not ok
        assert error_msg

    def test_check_connection_invalid_config(self, api, config, logger_mock, fb_marketing):
        config.pop("start_date")
        ok, error_msg = fb_marketing.check_connection(logger_mock, config=config)

        assert not ok
        assert error_msg

    def test_check_connection_exception(self, api, config, logger_mock, fb_marketing):
        api.side_effect = RuntimeError("Something went wrong!")

        with pytest.raises(RuntimeError, match="Something went wrong!"):
            fb_marketing.check_connection(logger_mock, config=config)

    def test_streams(self, config, api, fb_marketing):
        streams = fb_marketing.streams(config)

        assert len(streams) == 29

    def test_spec(self, fb_marketing):
        spec = fb_marketing.spec()

        assert isinstance(spec, ConnectorSpecification)

    def test_get_custom_insights_streams(self, api, config, fb_marketing):
        config["custom_insights"] = [
            {"name": "test", "fields": ["account_id"], "breakdowns": ["ad_format_asset"], "action_breakdowns": ["action_device"]},
        ]
        config = ConnectorConfig.parse_obj(config)
        assert fb_marketing.get_custom_insights_streams(api, config)

    def test_get_custom_insights_action_breakdowns_allow_empty(self, api, config, fb_marketing):
        config["custom_insights"] = [
            {"name": "test", "fields": ["account_id"], "breakdowns": ["ad_format_asset"], "action_breakdowns": []},
        ]

        config["action_breakdowns_allow_empty"] = False
        streams = fb_marketing.get_custom_insights_streams(api, ConnectorConfig.parse_obj(config))
        assert len(streams) == 1
        assert streams[0].breakdowns == ["ad_format_asset"]
        assert streams[0].action_breakdowns == ["action_type", "action_target_id", "action_destination"]

        config["action_breakdowns_allow_empty"] = True
        streams = fb_marketing.get_custom_insights_streams(api, ConnectorConfig.parse_obj(config))
        assert len(streams) == 1
        assert streams[0].breakdowns == ["ad_format_asset"]
        assert streams[0].action_breakdowns == []


def test_check_config(config_gen, requests_mock, fb_marketing):
    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FacebookAdsApi.API_VERSION}/act_123/", {})

    assert command_check(fb_marketing, config_gen()) == AirbyteConnectionStatus(status=Status.SUCCEEDED, message=None)

    status = command_check(fb_marketing, config_gen(start_date="2019-99-10T00:00:00Z"))
    assert status.status == Status.FAILED

    status = command_check(fb_marketing, config_gen(end_date="2019-99-10T00:00:00Z"))
    assert status.status == Status.FAILED

    with pytest.raises(Exception):
        assert command_check(fb_marketing, config_gen(start_date=...))

    assert command_check(fb_marketing, config_gen(end_date=...)) == AirbyteConnectionStatus(status=Status.SUCCEEDED, message=None)
    assert command_check(fb_marketing, config_gen(end_date="")) == AirbyteConnectionStatus(status=Status.SUCCEEDED, message=None)


def test_check_connection_account_type_exception(mocker, fb_marketing, config, logger_mock):
    api_mock = mocker.Mock()
    api_mock.account.api_get.return_value = {"account": 123, "is_personal": 1}
    mocker.patch('source_facebook_marketing.source.API', return_value=api_mock)

    result, error = fb_marketing.check_connection(logger=logger_mock, config=config)

    assert not result
    assert isinstance(error, AccountTypeException)
