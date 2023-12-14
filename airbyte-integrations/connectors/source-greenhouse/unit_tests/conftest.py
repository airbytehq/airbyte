#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, Mock

import pytest
from airbyte_cdk.sources.streams import Stream
from source_greenhouse.components import GreenHouseSlicer, GreenHouseSubstreamSlicer


@pytest.fixture
def greenhouse_slicer():
    date_time = "2022-09-05T10:10:10.000000Z"
    return GreenHouseSlicer(cursor_field=date_time, parameters={}, request_cursor_field=None)


@pytest.fixture
def greenhouse_substream_slicer():
    parent_stream = MagicMock(spec=Stream)
    return GreenHouseSubstreamSlicer(cursor_field='cursor_field', stream_slice_field='slice_field', parent_stream=parent_stream, parent_key='parent_key', parameters={}, request_cursor_field=None)
