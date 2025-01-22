# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock

import pytest
import requests

from airbyte_cdk.sources.types import Record


def create_response(current_page: int, total_pages: int) -> requests.Response:
    """Helper function to create mock responses"""
    response = MagicMock(spec=requests.Response)
    response.json.return_value = {"response": {"currentPage": current_page, "pages": total_pages}}
    return response


@pytest.mark.parametrize(
    "current_page,total_pages,expected_next_page,expected_next_next_page",
    [
        (1, 5, 2, 3),  # First page
        (2, 5, 3, 4),  # Middle page
        (4, 5, 5, 6),  # Second to last page
        (5, 5, None, None),  # Last page
        (1, 1, None, None),  # Single page
    ],
    ids=["First page", "Middle page", "Penultimate page", "Last page", "Single page"],
)
def test_page_increment(components_module, current_page, total_pages, expected_next_page, expected_next_next_page):
    """Test the CustomPageIncrement pagination for various page combinations"""

    CustomPageIncrement = components_module.CustomPageIncrement

    config = {}
    page_size = 10
    parameters = {}
    pagination_strategy = CustomPageIncrement(config, page_size, parameters)

    initial_token = pagination_strategy.initial_token
    assert initial_token is None

    mock_response = create_response(current_page, total_pages)
    next_page = pagination_strategy.next_page_token(
        response=mock_response, last_page_size=5, last_record=Record(data={}, stream_name="test"), last_page_token_value=current_page
    )
    assert next_page == expected_next_page, f"Page {current_page} of {total_pages} should get next_page={expected_next_page}"

    if expected_next_next_page:
        next_page = pagination_strategy.next_page_token(
            response=mock_response, last_page_size=7, last_record=Record(data={}, stream_name="test"), last_page_token_value=next_page
        )
        assert next_page == expected_next_next_page, f"Page {current_page} of {total_pages} should get next_page={expected_next_next_page}"


def test_incoming_last_page_token_value_is_none(components_module):
    mock_response = create_response(0, 5)

    CustomPageIncrement = components_module.CustomPageIncrement
    pagination_strategy = CustomPageIncrement({}, 10, {})
    actual_next_page = pagination_strategy.next_page_token(
        response=mock_response, last_page_size=5, last_record=Record(data={}, stream_name="test"), last_page_token_value=None
    )

    assert actual_next_page == 1  # guardian API starts at page 0
