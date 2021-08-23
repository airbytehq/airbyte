#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
            "pages": {"next": {"starting_after": "1HaSB+xrOyyMXAkS/c1RteCL7BzOzTvYjmjakgTergIH31eoe2v4/sbLsJWP"
                                                 "\nIncfQLD3ouPkZlCwJ86F\n"}},
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
