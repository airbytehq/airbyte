"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from pathlib import Path
from typing import Mapping

import json
import pytest
from source_freshdesk.client import Client


HERE = Path(__file__).parent.absolute()


@pytest.fixture(scope="session")
def account_creds() -> Mapping[str, str]:
    config_filename = HERE.parent / "secrets" / "config.json"

    if not config_filename.exists():
        raise RuntimeError(f"Please provide credentials in {config_filename}")

    with open(str(config_filename)) as json_file:
        return json.load(json_file)


@pytest.fixture
def unknown_account() -> str:
    return "unknownaccount.freshdesk.com"


@pytest.fixture
def non_freshdesk_account() -> str:
    return "unknownaccount.somedomain.com"


def test_client_wrong_domain(non_freshdesk_account):
    expected_error = "Freshdesk v2 API works only via Freshdesk domains and not via custom CNAMEs"
    with pytest.raises(AttributeError, match=expected_error):
        Client(domain=non_freshdesk_account, api_key="wrong_key")


def test_client_wrong_account(unknown_account):
    client = Client(domain=unknown_account, api_key="wrong_key")
    alive, error = client.health_check()

    assert not alive
    assert error == "Invalid credentials"


def test_client_wrong_cred(account_creds):
    client = Client(domain=account_creds["domain"], api_key="wrong_key")
    alive, error = client.health_check()

    assert not alive
    assert error == "Invalid credentials"


def test_client_ok(account_creds):
    client = Client(domain=account_creds["domain"], api_key=account_creds["api_key"])
    alive, error = client.health_check()

    assert alive
    assert not error


def test_client_backoff_once(account_creds, requests_mock):
    """Error once, check that we retry and not fail"""
    responses = [
        {"json": {"error": "limit reached"}, "status_code": 429},
        {"json": {"status": "ok"}, "status_code": 200},
    ]
    requests_mock.register_uri("GET", "/api/v2/settings/helpdesk", responses)
    client = Client(domain=account_creds["domain"], api_key=account_creds["api_key"])

    result = client.settings()

    assert result == {"status": "ok"}
