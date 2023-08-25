#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re

from source_typeform import SourceTypeform
from source_typeform.source import TypeformStream

from airbyte_cdk import AirbyteLogger

logger = AirbyteLogger()

TYPEFORM_BASE_URL = TypeformStream.url_base


def test_check_connection_success(requests_mock, config, empty_response_ok):
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "me", empty_response_ok)
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/u6nXL7", empty_response_ok)
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/k9xNV4", empty_response_ok)

    ok, error = SourceTypeform().check_connection(logger, config)

    assert ok
    assert not error


def test_check_connection_bad_request_me(requests_mock, config, empty_response_bad):
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "me", empty_response_bad)

    ok, error = SourceTypeform().check_connection(logger, config)

    assert not ok
    assert error
    assert re.match("Cannot authenticate, please verify token.", error)


def test_check_connection_bad_request_forms(requests_mock, config, empty_response_ok, empty_response_bad):
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "me", empty_response_ok)
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/u6nXL7", empty_response_bad)

    ok, error = SourceTypeform().check_connection(logger, config)

    assert not ok
    assert error
    assert re.match("Cannot find forms with ID: u6nXL7", error)


def test_check_connection_empty():
    config = {}

    ok, error = SourceTypeform().check_connection(logger, config)

    assert not ok
    assert error


def test_check_connection_incomplete(config):
    credentials = config["credentials"]
    credentials.pop("access_token")

    ok, error = SourceTypeform().check_connection(logger, config)

    assert not ok
    assert error


def test_streams(config):
    streams = SourceTypeform().streams(config)

    assert len(streams) == 6
