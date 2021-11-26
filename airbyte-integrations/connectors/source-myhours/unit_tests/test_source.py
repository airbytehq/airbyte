#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

from source_myhours.source import SourceMyhours


def test_check_connection(mocker):
    with patch("requests.get"), patch("requests.post") as mock_request:
        source = SourceMyhours()
        mock_request.return_value.text = "{'accessToken':'valid'}"
        logger_mock = MagicMock()
        config = {"email": "john@doe.com", "password": "pwd"}
        assert source.check_connection(logger_mock, config) == (True, None)


def test_streams(mocker):
    with patch("requests.post") as mock_request:
        source = SourceMyhours()
        mock_request.return_value.text = "{'accessToken':'valid'}"
        config = {"email": "john@doe.com", "password": "pwd", "logs_batch_size": 30, "start_date": "2021-01-01"}
        streams = source.streams(config)
        expected_streams_number = 5
        assert len(streams) == expected_streams_number
