# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Pagination and partitioning contracts for every list stream."""

import pytest

from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.helpers import read_stream, records_data
from mock_server.request_builder import RevenueCatRequestBuilder, next_page_path
from mock_server.streams import LIST_STREAMS, STREAMS, list_response, mock_ancestors, record


@pytest.mark.parametrize("stream", LIST_STREAMS)
def test_reads_100_records_per_page_and_follows_next_page_for_each_partition(stream: str) -> None:
    spec = STREAMS[stream]
    with HttpMocker() as http_mocker:
        partitions = mock_ancestors(http_mocker, stream, ["parent_a", "parent_b"])
        expected = {}
        page_two_requests = []
        for index, partition in enumerate(partitions):
            path = spec.path(partition)
            first_id, second_id = f"{stream}_{index}_1", f"{stream}_{index}_2"
            page_two = RevenueCatRequestBuilder.endpoint(path).with_starting_after(first_id).build()
            http_mocker.get(
                RevenueCatRequestBuilder.endpoint(path).build(),
                list_response(stream, [record(stream, first_id)], next_page=next_page_path(path, first_id)),
            )
            http_mocker.get(page_two, list_response(stream, [record(stream, second_id)], next_page=None))
            page_two_requests.append(page_two)
            expected[first_id] = partition
            expected[second_id] = partition

        output = read_stream(stream)

    assert output.errors == []
    emitted = records_data(output)
    assert len(emitted) == len(expected)
    assert {r[spec.pk_field] for r in emitted} == set(expected)
    for r in emitted:
        partition = expected[r[spec.pk_field]]
        for field in spec.added_fields:
            assert r[field] == partition[field]
    for page_two in page_two_requests:
        http_mocker.assert_number_of_calls(page_two, 1)
