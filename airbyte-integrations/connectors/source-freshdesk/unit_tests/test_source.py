#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

from source_freshdesk import SourceFreshdesk

logger = logging.getLogger("test_source")


def test_check_connection_ok(requests_mock, config):
    json_resp = {"primary_language": "en", "supported_languages": [], "portal_languages": []}

    requests_mock.register_uri("GET", "/api/v2/settings/helpdesk", json=json_resp)
    ok, error_msg = SourceFreshdesk().check_connection(logger, config=config)

    assert ok and not error_msg


def test_check_connection_invalid_api_key(requests_mock, config):
    responses = [
        {"json": {"code": "invalid_credentials", "message": "You have to be logged in to perform this action."}, "status_code": 401}
    ]

    requests_mock.register_uri("GET", "/api/v2/settings/helpdesk", responses)
    ok, error_msg = SourceFreshdesk().check_connection(logger, config=config)
    assert not ok
    assert "The endpoint to access stream \'settings\' returned 401: Unauthorized. This is most likely due to wrong credentials. " in error_msg
    assert "You have to be logged in to perform this action." in error_msg


def test_check_connection_empty_config(config):
    config = {}

    ok, error_msg = SourceFreshdesk().check_connection(logger, config=config)

    assert not ok and error_msg


def test_check_connection_invalid_config(config):
    config.pop("api_key")

    ok, error_msg = SourceFreshdesk().check_connection(logger, config=config)

    assert not ok and error_msg


def test_check_connection_exception(requests_mock, config):
    ok, error_msg = SourceFreshdesk().check_connection(logger, config=config)

    assert not ok and error_msg


def test_streams(config):
    streams = SourceFreshdesk().streams(config)

    assert len(streams) == 28
