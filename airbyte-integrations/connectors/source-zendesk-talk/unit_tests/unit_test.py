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
from source_zendesk_talk.client import Client


@pytest.fixture(name="zendesk_credentials")
def zendesk_credentials_fixture():
    return {
        "email": "fake-email@email.cm",
        "access_token": "fake_access_token",
        "subdomain": "wrong_subdomain",
        "start_date": "2021-02-12T00:00:00Z",
    }


def test_client_with_wrong_credentials(zendesk_credentials):
    """Test check with wrong credentials"""
    client = Client(**zendesk_credentials)

    alive, error = client.health_check()

    assert not alive
    assert error


def test_client_backoff_on_limit_reached(requests_mock, zendesk_credentials):
    """Error twice, check that we retry and not fail"""
    responses = [
        {"json": {"error": "limit reached"}, "status_code": 429},
        {"json": {"error": "limit reached"}, "status_code": 429},
        {"json": {"phone_numbers": [], "count": 0}, "status_code": 200},
    ]

    requests_mock.get(f"https://{zendesk_credentials['subdomain']}.zendesk.com/api/v2/channels/voice/phone_numbers", responses)
    client = Client(**zendesk_credentials)

    alive, error = client.health_check()

    assert alive
    assert not error
