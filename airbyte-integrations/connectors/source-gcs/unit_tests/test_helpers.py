# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import Mock, patch

from source_gcs.helpers import get_stream_name


def test_get_stream_name():
    blob = Mock()
    blob.name = "path/to/stream.csv"

    assert get_stream_name(blob) == "stream"
