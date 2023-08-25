#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, Mock

import pytest
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.streams import Stream
from source_intercom.components import IncrementalSingleSliceCursor, IncrementalSubstreamSlicerCursor, IntercomRateLimiter



def test_slicer():
    date_time_dict = {"updated_at": 1662459010}
    slicer = IncrementalSingleSliceCursor(config={}, parameters={}, cursor_field="updated_at")
    slicer.close_slice(date_time_dict, date_time_dict)
    assert slicer.get_stream_state() == date_time_dict
    assert slicer.get_request_headers() == {}
    assert slicer.get_request_body_data() == {}
    assert slicer.get_request_body_json() == {}