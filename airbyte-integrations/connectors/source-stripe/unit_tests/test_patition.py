#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import random
from functools import partial
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.extractors import DpathExtractor, RecordSelector
from airbyte_cdk.sources.declarative.requesters import HttpRequester, RequestOption
from airbyte_cdk.sources.declarative.requesters.paginators import LowCodePaginator
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import LowCodeCursorPaginationStrategy
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from source_stripe.partition import PaginatedRequester, SourcePartitionGenerator

URL_BASE = "http://test_source"
PAGE_SIZE = 10


@pytest.fixture
def paginated_requester(url_base: str = URL_BASE, stream: str = "accounts") -> PaginatedRequester:
    requester = HttpRequester(
        url_base=url_base,
        request_options_provider=MagicMock(),
        path=stream,
        name=stream,
        config={},
        parameters={},
        message_repository=MagicMock(),
    )

    paginator = LowCodePaginator(
        LowCodeCursorPaginationStrategy(
            cursor_value="{{ last_records[-1]['id'] if last_records else None }}",
            config={},
            parameters={},
            page_size=PAGE_SIZE,
            stop_condition="{{ not response.has_more }}",
        ),
        config={},
        url_base="",
        parameters={},
        page_size_option=RequestOption(field_name="limit", inject_into=RequestOptionType.request_parameter, parameters={}),
        page_token_option=RequestOption(field_name="starting_after", inject_into=RequestOptionType.request_parameter, parameters={}),
    )
    record_selector = RecordSelector(DpathExtractor(field_path=["data"], config={}, parameters={}), {}, {})
    paginated_requester = PaginatedRequester(requester, record_selector, paginator)
    return paginated_requester


@pytest.fixture
def generate_stream_data():
    def stream_data(stream_name: str = "account", first_id: int = 0, number_of_records: int = 10, has_more: int = 0):
        return {
            "object": "list",
            "data": [
                {"id": f"{stream_name}_{i}", "object": stream_name, "type": random.choice(["standard", "premium", "top"])}
                for i in range(first_id, first_id + number_of_records, 1)
            ],
            "has_more": has_more,
        }

    return stream_data


def mock_response(request, context, response_data: Mapping[str, Any]):
    return json.dumps(response_data)


def test_paginated_requester(paginated_requester: PaginatedRequester, requests_mock, generate_stream_data):
    path = f"{URL_BASE}/accounts?limit={PAGE_SIZE}"

    stream_data = generate_stream_data(number_of_records=100)

    requests_mock.register_uri("GET", path, text=partial(mock_response, response_data=stream_data))

    response_data = list(paginated_requester.send_requests(path, request_params={}))
    assert len(response_data) == len(stream_data["data"])


def test_paginated_requester_with_next_page(paginated_requester: PaginatedRequester, requests_mock, generate_stream_data):
    path = f"{URL_BASE}/accounts?limit={PAGE_SIZE}"

    stream_data = generate_stream_data(has_more=8)
    nested_stream_data = generate_stream_data(first_id=len(stream_data), number_of_records=8)

    requests_mock.register_uri("GET", path, text=partial(mock_response, response_data=stream_data))
    requests_mock.register_uri(
        "GET", f"{path}&starting_after={stream_data['data'][-1]['id']}", text=partial(mock_response, response_data=nested_stream_data)
    )

    response_data = list(paginated_requester.send_requests(path, request_params={}))
    assert len(response_data) == len(stream_data["data"]) + len(nested_stream_data["data"])


@pytest.mark.parametrize(
    "test_name, stream_slice, request_params, expected_records_len",
    [
        ("test_partition_with_empty_slice", {}, {"created[gte]": lambda _slice: _slice.get("created[gte]") if _slice else None}, 10),
        ("test_partition_with_none_slice", None, {}, 8),
        (
            "test_partition_with_request_parameters",
            {"created[gte]": 1567483742},
            {"created[gte]": lambda _slice: _slice.get("created[gte]") if _slice else None},
            3,
        ),
    ],
)
def test_partition(
    paginated_requester: PaginatedRequester,
    requests_mock,
    generate_stream_data,
    test_name,
    stream_slice,
    request_params,
    expected_records_len,
):
    path = f"{URL_BASE}/accounts?limit={PAGE_SIZE}"

    stream = MagicMock()
    stream.stream_slices.return_value = [stream_slice]

    partition_generator = SourcePartitionGenerator(stream, paginated_requester, request_params=request_params)

    stream_data = generate_stream_data(number_of_records=expected_records_len)

    response_data = []
    for partition in partition_generator.generate():
        partition_parameters = partition._parse_request_arguments(request_params)
        if partition_parameters:
            path = f"{path}&" + "&".join(f"{k}={v}" for k, v in partition_parameters.items())

        requests_mock.register_uri("GET", path, text=partial(mock_response, response_data=stream_data))

        response_data += list(partition.read())

    assert len(response_data) == expected_records_len
