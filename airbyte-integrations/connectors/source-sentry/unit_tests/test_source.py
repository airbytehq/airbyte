#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock

from source_sentry.source import SourceSentry


def test_source_wrong_credentials(requests_mock):
    config = {"auth_token": "test_auth_token"}
    source = SourceSentry(config=config, catalog=None, state={})
    status, error = source.check_connection(logger=logging.getLogger("airbyte"), config=config)
    assert not status


def test_check_connection(requests_mock):
    config = {"auth_token": "token", "organization": "test-org", "project": "test-project", "hostname": "sentry.io"}
    source = SourceSentry(config=config, catalog=None, state=None)
    logger_mock = MagicMock()
    requests_mock.get(url="https://sentry.io/api/0/projects/test-org/test-project/", json={"id": "id", "name": "test-project"})
    assert source.check_connection(logger_mock, config) == (True, None)


def test_streams(mocker):
    config_mock = MagicMock()
    config_mock["auth_token"] = "test-token"
    config_mock["organization"] = "test-organization"
    config_mock["project"] = "test-project"

    source = SourceSentry(config=config_mock, catalog=None, state=None)
    streams = source.streams(config_mock)

    expected_streams_number = 5
    assert len(streams) == expected_streams_number
