#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
import requests
from source_zendesk_chat.components.time_offset_pagination import ZendeskChatTimeOffsetIncrementPaginationStrategy


def _get_paginator(config, time_field_name) -> ZendeskChatTimeOffsetIncrementPaginationStrategy:
    return ZendeskChatTimeOffsetIncrementPaginationStrategy(
        config=config,
        page_size=1,
        time_field_name=time_field_name,
        parameters={},
    )


@pytest.mark.parametrize(
    "time_field_name, response, last_records, expected",
    [
        ("end_time", {"chats": [{"update_timestamp": 1}], "end_time": 2}, [{"update_timestamp": 1}], 2),
        ("end_time", {"chats": [], "end_time": 3}, [], None),
    ],
)
def test_time_offset_increment_pagination_next_page_token(requests_mock, config, time_field_name, response, last_records, expected) -> None:
    paginator = _get_paginator(config, time_field_name)
    test_url = f"https://{config['subdomain']}.zendesk.com/api/v2/chat/chats"
    requests_mock.get(test_url, json=response)
    test_response = requests.get(test_url)
    assert paginator.next_page_token(test_response, last_records) == expected
