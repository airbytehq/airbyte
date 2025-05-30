# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from datetime import datetime, timedelta

import pytest
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from airbyte_cdk.sources.file_based.remote_file import RemoteFile
from source_gcs import Cursor


@pytest.fixture
def logger():
    return logging.getLogger("airbyte")


def _file_uri() -> str:
    return "http://some.uri/a.csv?query=param"


@pytest.fixture
def remote_file():
    return RemoteFile(uri=_file_uri(), last_modified=datetime.now(), mime_type="csv")

@pytest.fixture
def remote_file_older():
    return RemoteFile(uri=_file_uri(), last_modified=datetime.now() - timedelta(days=1))


@pytest.fixture
def remote_file_future():
    return RemoteFile(uri=_file_uri(), last_modified=datetime.now() + timedelta(days=1))


@pytest.fixture
def remote_file_b():
    return RemoteFile(uri=_file_uri().replace("a.csv", "b.csv"), last_modified=datetime.now())


@pytest.fixture
def stream_config():
    return FileBasedStreamConfig(name="test_stream", format={})


@pytest.fixture
def cursor(stream_config):
    return Cursor(stream_config)
