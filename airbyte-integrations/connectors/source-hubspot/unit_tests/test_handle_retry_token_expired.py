#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.exceptions import UserDefinedBackoffException

from .conftest import find_stream


def test_handle_request_with_retry(config, requests_mock):
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    requests_mock.get(
        "https://api.hubapi.com/email/public/v1/campaigns?limit=500",
        json={"campaigns": [{"id": "test_id", "lastUpdatedTime": 1744969160000}]},
        status_code=200,
    )
    requests_mock.get("https://api.hubapi.com/email/public/v1/campaigns/test_id", json={"id": "test_id"}, status_code=200)

    stream_instance = find_stream("campaigns", config)
    stream_slices = list(stream_instance.retriever.stream_slicer.stream_slices())

    assert len(stream_slices) == 1
    list(stream_instance.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slices[0]))
    # one request per each mock
    assert requests_mock.call_count == 3


def test_handle_request_with_retry_token_expired(config, requests_mock):
    requests_mock.get("https://api.hubapi.com/crm/v3/schemas", json={}, status_code=200)
    requests_mock.get(
        "https://api.hubapi.com/email/public/v1/campaigns?limit=500",
        json={"campaigns": [{"id": "test_id", "lastUpdatedTime": 1744969160000}]},
        status_code=200,
    )
    rate_limited_mock = requests_mock.get(
        "https://api.hubapi.com/email/public/v1/campaigns/test_id", json={"message": "rate limited"}, status_code=429
    )

    stream_instance = find_stream("campaigns", config)
    stream_slices = list(stream_instance.retriever.stream_slicer.stream_slices())

    assert len(stream_slices) == 1
    with pytest.raises(UserDefinedBackoffException):
        list(stream_instance.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slices[0]))
    #  5 default retries + first call
    assert rate_limited_mock.call_count == 6
