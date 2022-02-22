#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from source_stripe.streams import CheckoutSessionsLineItems


def test_missed_id_child_stream(requests_mock):

    session_id_missed = "cs_test_a165K4wNihuJlp2u3tknuohrvjAxyXFUB7nxZH3lwXRKJsadNEvIEWMUJ9"
    session_id_exists = "cs_test_a1RjRHNyGUQOFVF3OkL8V8J0lZUASyVoCtsnZYG74VrBv3qz4245BLA1BP"

    response_sessions = {
        "data": [{"id": session_id_missed}, {"id": session_id_exists}],
        "has_more": False,
        "object": "list",
        "url": "/v1/checkout/sessions",
    }

    response_sessions_line_items = {
        "data": [{"id": "li_1JpAUUIEn5WyEQxnfGJT5MbL"}],
        "has_more": False,
        "object": "list",
        "url": "/v1/checkout/sessions/{}/line_items".format(session_id_exists),
    }

    response_error = {
        "error": {
            "code": "resource_missing",
            "doc_url": "https://stripe.com/docs/error-codes/resource-missing",
            "message": "No such checkout session: '{}'".format(session_id_missed),
            "param": "session",
            "type": "invalid_request_error",
        }
    }

    requests_mock.get("https://api.stripe.com/v1/checkout/sessions", json=response_sessions)
    requests_mock.get(
        "https://api.stripe.com/v1/checkout/sessions/{}/line_items".format(session_id_exists), json=response_sessions_line_items
    )
    requests_mock.get(
        "https://api.stripe.com/v1/checkout/sessions/{}/line_items".format(session_id_missed), json=response_error, status_code=404
    )

    stream = CheckoutSessionsLineItems(start_date=None, account_id=None)
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh))
    assert len(records) == 1
