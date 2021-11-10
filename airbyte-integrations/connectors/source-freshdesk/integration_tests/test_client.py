#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from pathlib import Path
from typing import Mapping

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
