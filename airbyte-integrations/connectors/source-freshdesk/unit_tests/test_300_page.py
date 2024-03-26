#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.models import SyncMode
from conftest import find_stream


@pytest.fixture(name="responses")
def responses_fixtures():
    return [
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&updated_since=2002-02-10T22%3A21%3A44Z",
            "json": [{"id": 1, "updated_at": "2018-01-02T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2002-02-10T22%3A21%3A44Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2002-02-10T22%3A21%3A44Z",
            "json": [{"id": 2, "updated_at": "2018-02-02T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/v2/tickets?per_page=1&page=3&updated_since=2002-02-10T22%3A21%3A44Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&updated_since=2018-02-02T00%3A00%3A00Z",
            "json": [{"id": 2, "updated_at": "2018-02-02T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2018-02-02T00%3A00%3A00Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2018-02-02T00%3A00%3A00Z",
            "json": [{"id": 3, "updated_at": "2018-03-02T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/v2/tickets?per_page=1&page=3&updated_since=2018-02-02T00%3A00%3A00Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&updated_since=2018-03-02T00%3A00%3A00Z",
            "json": [{"id": 3, "updated_at": "2018-03-02T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2018-03-02T00%3A00%3A00Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2018-03-02T00%3A00%3A00Z",
            "json": [{"id": 4, "updated_at": "2019-01-03T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/v2/tickets?per_page=1&page=3&updated_since=2018-03-02T00%3A00%3A00Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&updated_since=2019-01-03T00%3A00%3A00Z",
            "json": [{"id": 4, "updated_at": "2019-01-03T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/tickets?per_page=1&page=2&updated_since=2019-01-03T00%3A00%3A00Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2019-01-03T00%3A00%3A00Z",
            "json": [{"id": 5, "updated_at": "2019-02-03T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/tickets?per_page=1&page=3&updated_since=2019-01-03T00%3A00%3A00Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&updated_since=2019-02-03T00%3A00%3A00Z",
            "json": [{"id": 5, "updated_at": "2019-02-03T00:00:00Z"}],
            "headers": {
                "Link": '<https://test.freshdesk.com/api/tickets?per_page=1&page=2&updated_since=2019-02-03T00%3A00%3A00Z>; rel="next"'
            },
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&page=2&updated_since=2019-02-03T00%3A00%3A00Z",
            "json": [{"id": 6, "updated_at": "2019-03-03T00:00:00Z"}],
        },
        {
            "url": "https://test.freshdesk.com/api/v2/tickets?per_page=1&updated_since=2019-03-03T00%3A00%3A00Z",
            "json": [],
        },
    ]


class Test300PageLimit:
    def test_not_all_records(self, requests_mock, authenticator, config, responses):
        """
        TEST 1 - not all records are retrieved

        During test1 the tickets_stream changes the state of parameters on page: 2,
        by updating the params:
        `params["order_by"] = "updated_at"`
        `params["updated_since"] = last_record`
        continues to fetch records from the source, using new cycle, and so on.

        NOTE:
        After switch of the state on ticket_paginate_limit = 2, is this example, we will experience the
        records duplication, because of the last_record state, starting at the point
        where we stoped causes the duplication of the output. The solution for this is to add at least 1 second to the
        last_record state. The DBT normalization should handle this for the end user, so the duplication issue is not a
        blocker in such cases.
        Main pricipal here is: airbyte is at-least-once delivery, but skipping records is data loss.
        """

        expected_output = [
            {"id": 1, "updated_at": "2018-01-02T00:00:00Z"},
            {"id": 2, "updated_at": "2018-02-02T00:00:00Z"},
            {"id": 2, "updated_at": "2018-02-02T00:00:00Z"},  # duplicate
            {"id": 3, "updated_at": "2018-03-02T00:00:00Z"},
            {"id": 3, "updated_at": "2018-03-02T00:00:00Z"},  # duplicate
            {"id": 4, "updated_at": "2019-01-03T00:00:00Z"},
            {"id": 4, "updated_at": "2019-01-03T00:00:00Z"},  # duplicate
            {"id": 5, "updated_at": "2019-02-03T00:00:00Z"},
            {"id": 5, "updated_at": "2019-02-03T00:00:00Z"},  # duplicate
            {"id": 6, "updated_at": "2019-03-03T00:00:00Z"},
        ]

        # Create test_stream instance.
        test_stream = find_stream("tickets", config)

        # INT value of page number where the switch state should be triggered.
        # in this test case values from: 1 - 4, assuming we want to switch state on this page.
        test_stream.retriever.paginator.pagination_strategy.PAGE_LIMIT = 2
        # This parameter mocks the "per_page" parameter in the API Call
        test_stream.retriever.paginator.pagination_strategy._page_size = 1

        # Mocking Request
        for response in responses:
            requests_mock.register_uri(
                "GET",
                response["url"],
                json=response["json"],
                headers=response.get("headers", {}),
            )

        records = []
        for slice in test_stream.stream_slices(sync_mode=SyncMode.full_refresh):
            records_generator = test_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice)
            records.extend([dict(record) for record in records_generator])

        # We're expecting 6 records to return from the tickets_stream
        assert records == expected_output
