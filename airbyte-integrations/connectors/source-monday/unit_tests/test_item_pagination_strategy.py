#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from source_monday.item_pagination_strategy import ItemPaginationStrategy


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
        )
    ]
)
def test_item_pagination_strategy(response_json, last_records, expected):
    strategy = ItemPaginationStrategy(
        page_size=1,
        parameters={"items_per_page": 1},
    )
    response = MagicMock()
    response.json.return_value = response_json

    assert strategy.next_page_token(response, last_records) == expected
