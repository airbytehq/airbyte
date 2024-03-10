#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_notion.source import SourceNotion

def test_streams(mocker):
    source = SourceNotion()
    config_mock = MagicMock()
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number
