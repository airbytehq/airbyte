#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from source_tiktok_marketing.api_adapter import get_response_adapter

from .parametrize import api_response_parameters


@api_response_parameters
def test_api_response_adapter(record_before, record_after, stream_name, endpoint_path):
    adapter = get_response_adapter(current_version="v1.3", target_version="v1.2", stream_name=stream_name, api_endpoint=endpoint_path)
    adapter(record_before)
    assert record_before == record_after
