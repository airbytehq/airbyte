# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
from source_gcs import Cursor, SourceGCSStreamReader
from source_gcs.helpers import GCSUploadableRemoteFile

from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig


@pytest.fixture
def logger():
    return logging.getLogger("airbyte")


def _file_uri() -> str:
    return "http://some.uri/a.csv?query=param"


@pytest.fixture
def remote_file():
    blob = MagicMock(size=100, id="test/file/id", time_created=datetime.now() - timedelta(hours=1), updated=datetime.now())
    blob.name.return_value = "file.csv"
    return GCSUploadableRemoteFile(uri=_file_uri(), last_modified=datetime.now(), mime_type="csv", blob=blob)


@pytest.fixture
def remote_file_older():
    return GCSUploadableRemoteFile(uri=_file_uri(), last_modified=datetime.now() - timedelta(days=1), blob=MagicMock())


@pytest.fixture
def remote_file_future():
    return GCSUploadableRemoteFile(uri=_file_uri(), last_modified=datetime.now() + timedelta(days=1), blob=MagicMock())


@pytest.fixture
def remote_file_b():
    return GCSUploadableRemoteFile(uri=_file_uri().replace("a.csv", "b.csv"), last_modified=datetime.now(), blob=MagicMock())


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
    return GCSUploadableRemoteFile(
        uri=str(Path(__file__).parent / "resource/files/test.csv.zip"),
        blob=MagicMock(),
        last_modified=datetime.today(),
        displayed_uri="resource/files/test.csv.zip",
    )


@pytest.fixture
def mocked_blob():
    blob = Mock()
    with open(Path(__file__).parent / "resource/files/test.csv.zip", "rb") as f:
        blob.download_as_bytes.return_value = f.read()
        blob.size = f.tell()

    return blob
