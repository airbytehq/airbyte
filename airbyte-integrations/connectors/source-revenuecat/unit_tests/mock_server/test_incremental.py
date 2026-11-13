# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Client-side incremental contract: RevenueCat list endpoints are unsorted and take no date filter."""

from typing import Any, Iterable, Set

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from mock_server.helpers import read_stream, records_data
from mock_server.request_builder import RevenueCatRequestBuilder, next_page_path
from mock_server.streams import INCREMENTAL_STREAMS, STREAMS, list_response, mock_ancestors, record


_T1 = 1735689600000  # 2025-01-01
_T2 = 1738368000000  # 2025-02-01
_OLD = 1736899200000  # 2025-01-15, older than the saved state
_NEW = 1740787200000  # 2025-03-01
_NEWEST = 1743465600000  # 2025-04-01


def _cursor_values(value: Any, cursor_field: str) -> Set[str]:
    found: Set[str] = set()
    items: Iterable[Any] = value.values() if isinstance(value, dict) else value if isinstance(value, list) else []
    if isinstance(value, dict) and cursor_field in value:
        found.add(str(value[cursor_field]))
    for item in items:
        found |= _cursor_values(item, cursor_field)
    return found


def _mock_two_pages(http_mocker: HttpMocker, stream: str, page_one: list, page_two: list):
    spec = STREAMS[stream]
    (partition,) = mock_ancestors(http_mocker, stream, ["parent_a"])
    path = spec.path(partition)
    last_id = page_one[-1][1]
    second = RevenueCatRequestBuilder.endpoint(path).with_starting_after(last_id).build()
    http_mocker.get(
        RevenueCatRequestBuilder.endpoint(path).build(),
        list_response(stream, [record(stream, i, ts) for ts, i in page_one], next_page=next_page_path(path, last_id)),
    )
    http_mocker.get(second, list_response(stream, [record(stream, i, ts) for ts, i in page_two], next_page=None))
    return second


@pytest.mark.parametrize("stream", INCREMENTAL_STREAMS)
def test_second_sync_reads_every_page_and_drops_only_records_older_than_state(stream: str) -> None:
    spec = STREAMS[stream]
    with HttpMocker() as http_mocker:
        _mock_two_pages(http_mocker, stream, [(_T1, "first_1")], [(_T2, "first_2")])
        first = read_stream(stream, SyncMode.incremental)
    assert first.errors == []
    assert {r[spec.pk_field] for r in records_data(first)} == {"first_1", "first_2"}
    first_state = first.most_recent_state.stream_state.__dict__
    assert _cursor_values(first_state, spec.cursor_field) == {str(_T2)}

    state = StateBuilder().with_stream_state(stream, first_state).build()
    with HttpMocker() as http_mocker:
        second_page = _mock_two_pages(http_mocker, stream, [(_NEW, "new_1"), (_OLD, "old_1")], [(_NEWEST, "new_2")])
        second = read_stream(stream, SyncMode.incremental, state=state)

    assert second.errors == []
    assert sorted(r[spec.pk_field] for r in records_data(second)) == ["new_1", "new_2"]
    http_mocker.assert_number_of_calls(second_page, 1)
    assert _cursor_values(second.most_recent_state.stream_state.__dict__, spec.cursor_field) == {str(_NEWEST)}
