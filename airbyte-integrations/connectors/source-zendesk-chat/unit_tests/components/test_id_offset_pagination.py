#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
import requests
from source_zendesk_chat.components.id_offset_pagination import ZendeskChatIdOffsetIncrementPaginationStrategy


def _get_paginator(config, id_field) -> ZendeskChatIdOffsetIncrementPaginationStrategy:
    return ZendeskChatIdOffsetIncrementPaginationStrategy(
        config=config,
        page_size=1,
        id_field=id_field,
        parameters={},
    )


@pytest.mark.parametrize(
    "id_field, last_records, expected",
    [("id", [{"id": 1}], 2), ("id", [], None)],
)
def test_id_offset_increment_pagination_next_page_token(requests_mock, config, id_field, last_records, expected) -> None:
    paginator = _get_paginator(config, id_field)
    test_url = f"https://{config['subdomain']}.zendesk.com/api/v2/chat/agents"
    requests_mock.get(test_url, json=last_records)
    test_response = requests.get(test_url)
    assert paginator.next_page_token(test_response, last_records) == expected
