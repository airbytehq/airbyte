#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

from conftest import TEST_CONFIG, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


ACCOUNTS_URL = "https://api.twilio.com/2010-04-01/Accounts.json"
MAIN_SID = TEST_CONFIG["account_sid"]


def _account(sid: str, owner_account_sid: str) -> dict:
    return {
        "sid": sid,
        "owner_account_sid": owner_account_sid,
        "friendly_name": sid,
        "status": "active",
        "auth_token": f"token-{sid}",
    }


def _mock_accounts(http_mocker: HttpMocker) -> None:
    # Twilio sets a main account's owner_account_sid to its own sid.
    http_mocker.get(
        HttpRequest(url=ACCOUNTS_URL, query_params={"PageSize": "1000"}),
        HttpResponse(
            body=json.dumps(
                {
                    "accounts": [
                        _account(MAIN_SID, MAIN_SID),
                        _account("ACsub1", MAIN_SID),
                        _account("ACsub2", MAIN_SID),
                    ],
                    "next_page_uri": None,
                }
            ),
            status_code=200,
        ),
    )


def _read(stream_name: str):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(TEST_CONFIG), TEST_CONFIG, catalog)


@HttpMocker()
def test_subaccounts_excludes_main_account_and_auth_token(http_mocker: HttpMocker):
    _mock_accounts(http_mocker)

    output = _read("subaccounts")

    assert [record.record.data["sid"] for record in output.records] == ["ACsub1", "ACsub2"]
    assert all("auth_token" not in record.record.data for record in output.records)


@HttpMocker()
def test_accounts_still_returns_main_account_and_subaccounts(http_mocker: HttpMocker):
    _mock_accounts(http_mocker)

    output = _read("accounts")

    assert [record.record.data["sid"] for record in output.records] == [MAIN_SID, "ACsub1", "ACsub2"]
