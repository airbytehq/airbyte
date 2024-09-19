# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest
from source_gcs import SourceGCSStreamReader
from source_gcs.helpers import GCSRemoteFile


@pytest.fixture
def logger():
    return logging.getLogger("airbyte")


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
        mime_type=".zip"
    )
