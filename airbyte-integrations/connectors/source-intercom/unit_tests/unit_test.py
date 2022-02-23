#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import pytest
import requests
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_intercom.source import Companies, Contacts, IntercomStream

test_data = [
    (
        IntercomStream,
        {"data": [], "pages": {"next": "https://api.intercom.io/conversations?per_page=1&page=2"}},
        {"per_page": "1", "page": "2"},
    ),
    (
        Companies,
        {"data": [{"type": "company"}], "scroll_param": "25b649f7-4d33-4ef6-88f5-60e5b8244309"},
        {"scroll_param": "25b649f7-4d33-4ef6-88f5-60e5b8244309"},
    ),
    (
        Contacts,
        {
            "data": [],
            "pages": {
                "next": {"starting_after": "1HaSB+xrOyyMXAkS/c1RteCL7BzOzTvYjmjakgTergIH31eoe2v4/sbLsJWP" "\nIncfQLD3ouPkZlCwJ86F\n"}
            },
        },
        {"starting_after": "1HaSB+xrOyyMXAkS/c1RteCL7BzOzTvYjmjakgTergIH31eoe2v4/sbLsJWP\nIncfQLD3ouPkZlCwJ86F\n"},
    ),
]


@pytest.mark.parametrize(
    "intercom_class,response_json,expected_output_token", test_data, ids=["base pagination", "companies pagination", "contacts pagination"]
)
def test_get_next_page_token(intercom_class, response_json, expected_output_token, requests_mock):
    """
    Test shows that next_page parameters are parsed correctly from the response object and could be passed for next request API call,
    """

    requests_mock.get("https://api.intercom.io/conversations", json=response_json)
    response = requests.get("https://api.intercom.io/conversations")
    intercom_class = type("intercom_class", (intercom_class,), {"path": ""})
    test = intercom_class(authenticator=NoAuth).next_page_token(response)

    assert test == expected_output_token
