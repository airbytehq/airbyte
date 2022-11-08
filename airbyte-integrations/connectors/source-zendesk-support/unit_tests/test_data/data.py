#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


TICKET_EVENTS_STREAM_RESPONSE: dict = {
    "ticket_events": [
        {
            "child_events": [
                {
                    "id": 99999,
                    "via": {},
                    "via_reference_id": None,
                    "type": "Comment",
                    "author_id": 10,
                    "body": "test_comment",
                    "html_body": '<div class="zd-comment" dir="auto">test_comment<br/></div>',
                    "plain_body": "test_comment",
                    "public": True,
                    "attachments": [],
                    "audit_id": 123456,
                    "created_at": "2022-03-17T16:03:07Z",
                    "event_type": "Comment",
                }
            ],
            "id": 999999,
            "ticket_id": 3,
            "timestamp": 1647532987,
            "created_at": "2022-03-17T16:03:07Z",
            "updater_id": 9999999,
            "via": "Web form",
            "system": {},
            "metadata": {},
            "event_type": "Audit",
        }
    ],
    "next_page": "https://subdomain.zendesk.com/api/v2/stream.json?&start_time=1122334455&page=2",
    "count": 215,
    "end_of_stream": False,
    "end_time": 1647532987,
}
