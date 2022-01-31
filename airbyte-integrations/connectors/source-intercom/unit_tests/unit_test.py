#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import pytest
import requests
from airbyte_cdk.models import SyncMode
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


def test_switch_to_standard_endpoint_if_scroll_expired(requests_mock):
    """
    Test shows that if scroll param expired we try sync with standard API.
    """

    url = "https://api.intercom.io/companies/scroll"
    requests_mock.get(
        url,
        json={"type": "company.list", "data": [{"type": "company", "id": "530370b477ad7120001d"}], "scroll_param": "expired_scroll_param"},
    )

    url = "https://api.intercom.io/companies/scroll?scroll_param=expired_scroll_param"
    requests_mock.get(url, json={"errors": [{"code": "not_found", "message": "scroll parameter not found"}]}, status_code=404)

    url = "https://api.intercom.io/companies"
    requests_mock.get(url, json={"type": "company.list", "data": [{"type": "company", "id": "530370b477ad7120001d"}]})

    stream1 = Companies(authenticator=NoAuth())

    records = []

    assert stream1._endpoint_type == Companies.EndpointType.scroll

    for slice in stream1.stream_slices(sync_mode=SyncMode.full_refresh):
        records += list(stream1.read_records(sync_mode=SyncMode, stream_slice=slice))

    assert stream1._endpoint_type == Companies.EndpointType.standard
