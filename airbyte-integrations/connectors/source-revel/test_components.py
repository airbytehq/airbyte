#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption, RequestOptionType
from airbyte_cdk.sources.declarative.retrievers import Retriever
from airbyte_cdk.sources.streams import Stream
from source_revel.components import InitialFullRefreshDatetimeIncrementalSync
from airbyte_cdk.sources.declarative.types import StreamSlice


@pytest.mark.parametrize(
    "stream_state, expected",
    [
        (
            {"updated_date": "2024-04-10T00:00:00.000000"},
            {"updated_date": "2024-04-15T10:32:22.000000"},
        ),
        (
            {},
            {},
        ),
    ],
)
def test_get_request_params(stream_state, expected):
    start_datetime = MinMaxDatetime(datetime="2024-01-10T00:00:00.000000", parameters={})
    datetime_format = "%Y-%m-%dT%H:%M:%S.%f"
    stream_slice = StreamSlice(partition={}, cursor_slice={"updated_date": "2024-04-15T10:32:22.000000"})
    start_request_option = RequestOption(inject_into=RequestOptionType.request_parameter, parameters={}, field_name="updated_date")

    slicer = InitialFullRefreshDatetimeIncrementalSync(
        config={},
        parameters={},
        cursor_field="updated_date",
        start_time_option=start_request_option,
        start_datetime=start_datetime,
        partition_field_start=InterpolatedString(string="updated_date", parameters={}),
        datetime_format=datetime_format,
    )
    assert slicer.get_request_params(stream_slice=stream_slice, stream_state=stream_state) == expected
