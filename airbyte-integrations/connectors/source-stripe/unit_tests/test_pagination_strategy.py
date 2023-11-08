#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Dict, List, Optional, Sequence

import pytest
import requests
from source_stripe.source import StripePaginationStrategy


def records_generator(_range: Sequence[int] = range(10)) -> List[Dict[str, Any]]:
    return [{"id": i, "account_name": f"customer fake account: {i+1}"} for i in _range]


@pytest.mark.parametrize(
    "test_name, last_records, page_size, has_more, expected_token",
    [
        ("test_token_with_all_fields", records_generator(range(100)), 100, {"has_more": True}, "99"),
        ("test_token_without_page_size_and_has_more", records_generator(), None, {"has_more": False}, None),
        ("test_token_with_page_size_and_has_more", records_generator([2, 5, 12]), 3, {"has_more": True}, "12"),
        ("test_token_without_has_more_field", records_generator(), 10, {}, None),
        ("test_token_with_empty_records_list", [], 100, {"has_more": True}, None),
    ],
)
def test_stripe_pagination_strategy(
    test_name: str, last_records: List[Dict[str, Any]], expected_token: Optional[str], page_size: Optional[int], has_more: Dict[str, Any]
):
    strategy = StripePaginationStrategy(page_size=page_size)

    response = requests.Response()
    response_body = {"_metadata": {"content": "content_value"}, "data": last_records, **has_more}
    response._content = json.dumps(response_body).encode("utf-8")

    token = strategy.next_page_token(response, last_records)
    assert expected_token == token
    assert page_size == strategy.get_page_size()
