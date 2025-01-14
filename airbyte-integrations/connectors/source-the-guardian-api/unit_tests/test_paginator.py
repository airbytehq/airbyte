# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock

import pytest
import requests


def create_response(current_page: int, total_pages: int) -> requests.Response:
    """Helper function to create mock responses"""
    response = MagicMock(spec=requests.Response)
    response.json.return_value = {"response": {"currentPage": current_page, "pages": total_pages}}
    return response


@pytest.mark.parametrize(
    "current_page,total_pages,expected_next_page",
    [
        (1, 5, 2),  # First page
        (2, 5, 3),  # Middle page
        (4, 5, 5),  # Second to last page
        (5, 5, None),  # Last page
        (1, 1, None),  # Single page
    ],
    ids=["First page", "Middle page", "Penultimate page", "Last page", "Single page"],
)
def test_page_increment(connector_dir, components_module, current_page, total_pages, expected_next_page):
    """Test the CustomPageIncrement pagination for various page combinations"""

    CustomPageIncrement = components_module.CustomPageIncrement

    config = {}
    page_size = 10
    parameters = {}
    paginator = CustomPageIncrement(config, page_size, parameters)

    # Set internal page counter to match current_page
    paginator._page = current_page

    mock_response = create_response(current_page, total_pages)
    next_page = paginator.next_page_token(mock_response)
    assert next_page == expected_next_page, f"Page {current_page} of {total_pages} should get next_page={expected_next_page}"


def test_reset_functionality(components_module):
    """Test the reset behavior of CustomPageIncrement"""
    CustomPageIncrement = components_module.CustomPageIncrement

    config = {}
    page_size = 10
    parameters = {}
    paginator = CustomPageIncrement(config, page_size, parameters)

    # Advance a few pages
    mock_response = create_response(current_page=1, total_pages=5)
    paginator.next_page_token(mock_response)
    paginator.next_page_token(create_response(current_page=2, total_pages=5))

    # Test reset
    paginator.reset()
    assert paginator._page == 1, "Reset should set page back to 1"

    # Verify pagination works after reset
    next_page = paginator.next_page_token(mock_response)
    assert next_page == 2, "Should increment to page 2 after reset"
