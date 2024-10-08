#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
from source_surveycto.source import SourceSurveycto, SurveyctoStream


@pytest.fixture(name="config")
def config_fixture():
    return {
        "server_name": "server_name",
        "form_id": ["form_id_1", "form_id_2"],
        "start_date": "Jan 09, 2022 00:00:00 AM",
        "password": "password",
        "username": "username",
    }


@pytest.fixture(name="source")
def source_fixture():
    return SourceSurveycto()


@pytest.fixture(name="mock_survey_cto")
def mock_survey_cto_fixture():
    with patch("source_surveycto.source.Helpers.call_survey_cto", return_value="value") as mock_call_survey_cto, patch(
        "source_surveycto.source.Helpers.get_filter_data", return_value="value"
    ) as mock_filter_data, patch("source_surveycto.source.Helpers.get_json_schema", return_value="value") as mock_json_schema:
        yield mock_call_survey_cto, mock_filter_data, mock_json_schema


def test_check_connection_valid(mock_survey_cto, source, config):
    logger_mock = MagicMock()
    records = iter(["record1", "record2"])

    with patch.object(SurveyctoStream, "read_records", return_value=records):
        assert source.check_connection(logger_mock, config) == (True, None)


def test_check_connection_failure(mock_survey_cto, source, config):
    logger_mock = MagicMock()
    assert not source.check_connection(logger_mock, config)[0]


def test_generate_streams(mock_survey_cto, source, config):
    streams = source.generate_streams(config)
    assert len(streams) == 2


@patch("source_surveycto.source.SourceSurveycto.generate_streams", return_value=["stream_1", "stream2"])
def test_streams(mock_generate_streams, source, config):
    streams = source.streams(config)
    assert len(streams) == 2
