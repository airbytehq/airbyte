# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock

import pytest
from source_gcs import Cursor, SourceGCSStreamReader
from source_gcs.helpers import GCSRemoteFile

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig


@pytest.fixture
def logger():
    return logging.getLogger("airbyte")


def _file_uri() -> str:
    return "http://some.uri/a.csv?query=param"


@pytest.fixture
def remote_file():
    return GCSRemoteFile(uri=_file_uri(), last_modified=datetime.now(), mime_type="csv")


@pytest.fixture
def remote_file_older():
    return GCSRemoteFile(uri=_file_uri(), last_modified=datetime.now() - timedelta(days=1))


@pytest.fixture
def remote_file_future():
    return GCSRemoteFile(uri=_file_uri(), last_modified=datetime.now() + timedelta(days=1))


@pytest.fixture
def remote_file_b():
    return GCSRemoteFile(uri=_file_uri().replace("a.csv", "b.csv"), last_modified=datetime.now())


@pytest.fixture
def stream_config():
    return FileBasedStreamConfig(name="test_stream", format={})


@pytest.fixture
def cursor(stream_config):
    return Cursor(stream_config)


@pytest.fixture
def mocked_reader():
    reader = SourceGCSStreamReader()
    reader._gcs_client = Mock()
    return reader


@pytest.fixture
def zip_file():
    return GCSRemoteFile(
        uri=str(Path(__file__).parent / "resource/files/test.csv.zip"),
        last_modified=datetime.today(),
        mime_type=".zip",
        displayed_uri="resource/files/test.csv.zip",
    )


@pytest.fixture
def mocked_blob():
    blob = Mock()
    with open(Path(__file__).parent / "resource/files/test.csv.zip", "rb") as f:
        blob.download_as_bytes.return_value = f.read()
        blob.size = f.tell()

    return blob
