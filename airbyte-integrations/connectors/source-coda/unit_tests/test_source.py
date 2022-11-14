#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from source_coda.source import SourceCoda


def test_check_connection(mocker):
    source = SourceCoda()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceCoda()
    mocker.patch.object(source, "get_auth", return_value="dummy_token")
    config_mock = {"playground": False, "auth_token": "dummy_authtoken", "doc_id": "dummy_doc_id"}
    streams = source.streams(config_mock)
    expected_streams_number = 7
    assert len(streams) == expected_streams_number
