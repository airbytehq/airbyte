#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json

import requests
from airbyte_cdk.sources.declarative.decoders import JsonDecoder
from source_mailchimp.components import MailChimpRecordExtractorEmailActivity


def test_email_activity_extractor():
    decoder = JsonDecoder(parameters={})
    field_path = ["emails"]
    config = {"response_override": "stop_if_you_see_me"}
    extractor = MailChimpRecordExtractorEmailActivity(field_path=field_path, decoder=decoder, config=config, parameters={})

    body = {
        "emails": [
            {
                "campaign_id": "string",
                "list_id": "string",
                "list_is_active": True,
                "email_id": "string",
                "email_address": "AirbyteMailchimpUser@gmail.com",
                "activity": [
                    {"action": "close", "type": "string", "timestamp": "2019-08-24T14:15:22Z", "url": "string", "ip": "string"},
                    {"action": "open", "type": "string", "timestamp": "2019-08-24T14:15:22Z", "url": "string", "ip": "string"},
                ],
            }
        ],
        "campaign_id": "string",
        "total_items": 0,
    }
    response = requests.Response()
    response._content = json.dumps(body).encode("utf-8")

    expected_records = [
        {
            "action": "close",
            "campaign_id": "string",
            "email_address": "AirbyteMailchimpUser@gmail.com",
            "email_id": "string",
            "ip": "string",
            "list_id": "string",
            "list_is_active": True,
            "timestamp": "2019-08-24T14:15:22Z",
            "type": "string",
            "url": "string",
        },
        {
            "action": "open",
            "campaign_id": "string",
            "email_address": "AirbyteMailchimpUser@gmail.com",
            "email_id": "string",
            "ip": "string",
            "list_id": "string",
            "list_is_active": True,
            "timestamp": "2019-08-24T14:15:22Z",
            "type": "string",
            "url": "string",
        },
    ]

    assert list(extractor.extract_records(response=response)) == expected_records
