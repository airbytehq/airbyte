#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from source_freshdesk.components import FreshdeskTicketsPaginationStrategy


class TestFreshdeskTicketsPaginationStrategy:

    #  returns None when there are fewer records than the page size
    @pytest.mark.parametrize(
        "response, current_page, last_records, expected",
        [
            (requests.Response(), 1, [], None),  # No records
            (requests.Response(), 1, [1, 2, 3], None),  # Fewer records than page size
            (requests.Response(), 3, [1, 2, 3, 4], 4),  # Page size records
            (
                requests.Response(),
                6,
                [
                    {"updated_at": "2022-01-01"},
                    {"updated_at": "2022-01-02"},
                    {"updated_at": "2022-01-03"},
                    {"updated_at": "2022-01-03"},
                    {"updated_at": "2022-01-05"},
                ],
                "2022-01-05",
            ),  # Page limit is hit
        ],
    )
    def test_returns_none_when_fewer_records_than_page_size(self, response, current_page, last_records, expected, config):
        pagination_strategy = FreshdeskTicketsPaginationStrategy(config=config, page_size=4, parameters={})
        pagination_strategy.PAGE_LIMIT = 5
        pagination_strategy._page = current_page
        assert pagination_strategy.next_page_token(response, last_records) == expected
