from typing import Dict, Any, Optional, Iterator
import datetime

import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest

BALANCE_ACCOUNT_KEY = 'accounts'
TRANSACTION_KEY = 'transactions'
EPOCH_DATE = datetime.date.fromtimestamp(0)
SPEC_ENV_TO_PLAID_ENV = {
    'production': plaid.Environment.Production,
    'development': plaid.Environment.Development,
    'sandbox': plaid.Environment.Sandbox,
}

class PlaidRequester:
    def __init__(self, api: plaid_api.PlaidApi, access_token: str):
        self.api_requester = api
        self.access_token = access_token

    @classmethod
    def from_config(cls, plaid_env, client_id, api_key, access_token):
        plaid_config = plaid.Configuration(
            host=SPEC_ENV_TO_PLAID_ENV[plaid_env],
            api_key={ 'clientId': client_id, 'secret': api_key})
        api_client = plaid.ApiClient(plaid_config)
        api_requester = plaid_api.PlaidApi(api_client)

        return cls(api_requester, access_token)

    def test_connection(self) -> None:
        """
        Test that you can connect to plaid and create a query with the given credentials.
        Raises an error on failure.
        """
        self.api_requester.accounts_balance_get(AccountsBalanceGetRequest(access_token=self.access_token))

    def transaction_generator(self, start_date: Optional[str]=None) -> Iterator[Dict[str, Any]]:
        if not start_date:
            start_date = EPOCH_DATE
        else:
            start_date = datetime.date.fromisoformat(start_date)

        if start_date >= datetime.datetime.utcnow().date():
            return

        transaction_response = self.api_requester.transactions_get(TransactionsGetRequest(
                    access_token=self.access_token,
                    start_date=start_date,
                    end_date=datetime.datetime.utcnow().date()
                ))

        yield from map(lambda x: x.to_dict(), sorted(transaction_response[TRANSACTION_KEY], key=lambda t: t['date']))

    def balance_generator(self) -> Iterator[Dict[str, Any]]:
        balance_response = self.api_requester.accounts_balance_get(
            AccountsBalanceGetRequest(access_token=self.access_token))

        for balance in balance_response[BALANCE_ACCOUNT_KEY]:
            message_dict = balance['balances'].to_dict()
            message_dict['account_id'] = balance['account_id']
            yield message_dict
