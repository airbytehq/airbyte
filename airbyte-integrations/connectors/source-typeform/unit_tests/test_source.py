#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import re

from airbyte_cdk import AirbyteLogger
from source_typeform import SourceTypeform
from source_typeform.source import TypeformStream

logger = AirbyteLogger()

TYPEFORM_BASE_URL = TypeformStream.url_base


def test_check_connection_success(requests_mock, config, empty_response_ok):
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "me", empty_response_ok)
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/u6nXL7", empty_response_ok)
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/k9xNV4", empty_response_ok)

    ok, error = SourceTypeform().check_connection(logger, config)

    assert ok and not error


def test_check_connection_bad_request_me(requests_mock, config, empty_response_bad):
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "me", empty_response_bad)

    ok, error = SourceTypeform().check_connection(logger, config)

    assert not ok and error and re.match("Cannot authenticate, please verify token.", error)


def test_check_connection_bad_request_forms(requests_mock, config, empty_response_ok, empty_response_bad):
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "me", empty_response_ok)
    requests_mock.register_uri("GET", TYPEFORM_BASE_URL + "forms/u6nXL7", empty_response_bad)

    ok, error = SourceTypeform().check_connection(logger, config)

    assert not ok and error and re.match("Cannot find forms with ID: u6nXL7", error)


def test_check_connection_empty():
    config = {}

    ok, error = SourceTypeform().check_connection(logger, config)

    assert not ok and error


def test_check_connection_incomplete(config):
    config.pop("token")

    ok, error = SourceTypeform().check_connection(logger, config)

    assert not ok and error


def test_streams(config):
    streams = SourceTypeform().streams(config)

    assert len(streams) == 6
