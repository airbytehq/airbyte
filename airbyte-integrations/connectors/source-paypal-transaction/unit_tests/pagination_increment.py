# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
import re

import pytest
import requests
import requests_mock
from airbyte_cdk.sources.declarative.requesters.paginators import DefaultPaginator, PaginationStrategy


class MockPaginationStrategy(PaginationStrategy):
    def __init__(self, page_size):
        self.page_size = page_size
        self.current_page = 1

    @property
    def initial_token(self):
        return self.current_page

    def next_page_token(self, response, last_records):
        self.current_page += 1
        return self.current_page if self.current_page <= 5 else None

    def reset(self):
        self.current_page = 1

    @property
    def get_page_size(self):
        return self.page_size

@pytest.fixture
def mock_pagination_strategy():
    return MockPaginationStrategy(page_size=500)

@pytest.fixture
def paginator():
    pagination_strategy = MockPaginationStrategy(page_size=3)
    return DefaultPaginator(
        pagination_strategy=pagination_strategy,
        config={}, 
        url_base="http://example.com/v1/reporting/transactions",
        parameters={}
    )
    
def load_mock_data(page):
    with open(f"./unit_tests/test_files/page_{page}.json", "r") as file:
        return file.read()

# Test to verify pagination logic transitions from page 1 to page 2
def test_pagination_logic(paginator):
    page_1_data = load_mock_data(1)
    page_2_data = load_mock_data(2)

    paginator_url_1 = f"{paginator.url_base.string}?page=1&page_size={paginator.pagination_strategy.get_page_size}"
    paginator_url_2 = f"{paginator.url_base.string}?page=2&page_size={paginator.pagination_strategy.get_page_size}"
    
    with requests_mock.Mocker() as m:
        m.get(paginator_url_1, text=page_1_data, status_code=200)
        m.get(paginator_url_2, text=page_2_data, status_code=200)

        response_page_1 = requests.get(paginator_url_1)
        response_page_1._content = str.encode(page_1_data)
        response_page_2 = requests.get(paginator_url_2)
        response_page_2._content = str.encode(page_2_data)

    
    # Simulate getting the next page token from page 1's response
    next_page_token_page_1 = paginator.next_page_token(response_page_1, [])
    print("NEXT PAGE TOKEN", next_page_token_page_1)

    # Assert that the next page token indicates moving to page 2
    assert next_page_token_page_1['next_page_token'] == 2, "Failed to transition from page 1 to page 2"

    
    # Check that the correct page size is used in requests and that we have the right number of pages
    assert len(m.request_history) == 2  
    assert "page_size=3" in m.request_history[0].url 
    assert "page_size=3" in m.request_history[1].url 