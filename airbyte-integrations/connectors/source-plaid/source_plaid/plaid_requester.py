#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import datetime
import json
from typing import Any, Dict, Iterator, Optional

import plaid
from plaid.api import plaid_api
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest

BALANCE_ACCOUNT_KEY = "accounts"
TRANSACTION_KEY = "transactions"
EPOCH_DATE = datetime.date.fromtimestamp(0)
SPEC_ENV_TO_PLAID_ENV = {
    "production": plaid.Environment.Production,
    "development": plaid.Environment.Development,
    "sandbox": plaid.Environment.Sandbox,
}


class PlaidRequester:
    def __init__(self, plaid_env: str, client_id: str, api_key: str, access_token: str):
        plaid_config = plaid.Configuration(host=SPEC_ENV_TO_PLAID_ENV[plaid_env], api_key={"clientId": client_id, "secret": api_key})
        api_client = plaid.ApiClient(plaid_config)
        self.client = plaid_api.PlaidApi(api_client)
        self.access_token = access_token

    def test_connection(self) -> None:
        """
        Test that you can connect to plaid and create a query with the given credentials.
        Raises an error on failure.
        """
        try:
            request = AccountsBalanceGetRequest(access_token=self.access_token)
            self.client.accounts_balance_get(request)
            return True, None
        except plaid.ApiException as e:
            response = json.loads(e.body)
            return False, response

    def transaction_generator(self, date: Optional[str] = None) -> Iterator[Dict[str, Any]]:
        if not date:
            date = EPOCH_DATE
        else:
            date = datetime.date.fromisoformat(date)

        if date >= datetime.datetime.utcnow().date():
            return

        transaction_response = self.client.transactions_get(
            TransactionsGetRequest(access_token=self.access_token, start_date=date, end_date=datetime.datetime.utcnow().date())
        )

        yield from map(lambda x: x.to_dict(), sorted(transaction_response[TRANSACTION_KEY], key=lambda t: t["date"]))

    def balance_generator(self) -> Iterator[Dict[str, Any]]:
        balance_response = self.client.accounts_balance_get(AccountsBalanceGetRequest(access_token=self.access_token))

        for balance in balance_response[BALANCE_ACCOUNT_KEY]:
            message_dict = balance["balances"].to_dict()
            message_dict["account_id"] = balance["account_id"]
            yield message_dict
