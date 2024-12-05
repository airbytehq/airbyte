#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_monday.item_pagination_strategy import ItemCursorPaginationStrategy, ItemPaginationStrategy


@pytest.mark.parametrize(
    ("response_json", "last_records", "expected"),
    [
        pytest.param(
            {"data": {"boards": [{"items": [{"id": "1"}]}]}},
            [{"id": "1"}],
            (1, 2),
            id="test_next_item_page_for_the_same_board",
        ),
        pytest.param(
            {"data": {"boards": [{"items": []}]}},
            [],
            (2, 1),
            id="test_next_board_page_with_item_page_reset",
        ),
        pytest.param(
            {"data": {"boards": []}},
            [],
            None,
            id="test_end_pagination",
        ),
    ],
)
def test_item_pagination_strategy(response_json, last_records, expected):
    strategy = ItemPaginationStrategy(
        config={},
        page_size=1,
        parameters={"items_per_page": 1},
    )
    response = MagicMock()
    response.json.return_value = response_json

    assert strategy.next_page_token(response, last_records) == expected


@pytest.mark.parametrize(
    ("response_json", "last_records", "expected"),
    [
        pytest.param(
            {"data": {"boards": [{"items_page": {"cursor": "bla", "items": [{"id": "1"}]}}]}},
            [],
            (1, "bla"),
            id="test_cursor_in_first_request",
        ),
        pytest.param(
            {"data": {"next_items_page": {"cursor": "bla2", "items": [{"id": "1"}]}}},
            [],
            (1, "bla2"),
            id="test_cursor_in_next_page",
        ),
        pytest.param(
            {"data": {"next_items_page": {"items": [{"id": "1"}]}}},
            [],
            (2, None),
            id="test_next_board_page",
        ),
        pytest.param(
            {"data": {"boards": []}},
            [],
            None,
            id="test_end_pagination",
        ),
    ],
)
def test_item_cursor_pagination_strategy(response_json, last_records, expected):
    strategy = ItemCursorPaginationStrategy(
        config={},
        page_size=1,
        parameters={"items_per_page": 1},
    )
    response = MagicMock()
    response.json.return_value = response_json

    assert strategy.next_page_token(response, last_records) == expected
