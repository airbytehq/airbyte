# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from unittest.mock import MagicMock, patch

import pytest
from source_surveycto.source import SourceSurveycto
from source_surveycto.streams import FormData


@pytest.fixture(name="config")
def config_fixture():
    return {
        "form_id": "wrong_form_id",
        "server_name": "server_name",
        "username": "username",
        "password": "password",
        "start_date": "Jan 01, 2019 12:00:00 AM",
        "key": "key",
        "dataset_id": "test_dataset",
        "media_files": {
            "storage": "LOCAL",
            "file_path": "path_to_mediafiles",
            "file_name": "media_files.csv",
            "url_column": "Url",
            "file_name_column": "file_name",
            "file_type_column": "file_type",
        },
    }


@pytest.fixture(name="source")
def source_fixture():
    return SourceSurveycto()


def test_check_connection_valid(source, config):
    with patch("source_surveycto.source.SourceSurveycto.check_connection") as mock_check_credentials:
        mock_check_credentials.return_value = (True, None)
        assert source.check_connection(config) == (True, None)


def test_check_connection_failure(source, config):
    with patch("source_surveycto.source.SourceSurveycto.check_connection") as mock_check_credentials:
        expected_outcome = "Unable to connect - 400 Client Error: 400 for url: https://server_name.surveycto.com/"
        mock_check_credentials.return_value = (False, expected_outcome)
        assert source.check_connection(config) == (False, expected_outcome)


def test_streams(source, config):
    with open("secrets/config.json") as f:
        config = json.load(f)
    streams = source.streams(config)
    assert len(streams) == 5
