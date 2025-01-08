#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests
from source_zendesk_chat.components.bans_record_extractor import ZendeskChatBansRecordExtractor


def test_bans_stream_record_extractor(
    config,
    requests_mock,
    bans_stream_record,
    bans_stream_record_extractor_expected_output,
) -> None:
    test_url = f"https://{config['subdomain']}.zendesk.com/api/v2/chat/bans"
    requests_mock.get(test_url, json=bans_stream_record)
    test_response = requests.get(test_url)
    assert ZendeskChatBansRecordExtractor().extract_records(test_response) == bans_stream_record_extractor_expected_output
