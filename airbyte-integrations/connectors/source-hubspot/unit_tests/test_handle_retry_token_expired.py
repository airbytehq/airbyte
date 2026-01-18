#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest

from airbyte_cdk.sources.streams.http.http_client import MessageRepresentationAirbyteTracedErrors

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
    partitions = list(stream_instance._stream_partition_generator.generate())

    assert len(partitions) == 1
    list(partitions[0].read())
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
    partitions = list(stream_instance._stream_partition_generator.generate())

    assert len(partitions) == 1
    with pytest.raises(MessageRepresentationAirbyteTracedErrors):
        list(partitions[0].read())
    #  5 default retries + first call
    assert rate_limited_mock.call_count == 6
