#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import datetime
import time
import json
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import plaid
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from plaid.api import plaid_api
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

SPEC_ENV_TO_PLAID_ENV = {
    "production": plaid.Environment.Production,
    "development": plaid.Environment.Development,
    "sandbox": plaid.Environment.Sandbox,
}


class PlaidStream(Stream):
    def __init__(self, config: Mapping[str, Any]):
        plaid_config = plaid.Configuration(
            host=SPEC_ENV_TO_PLAID_ENV[config["plaid_env"]], api_key={"clientId": config["client_id"], "secret": config["api_key"]}
        )
        api_client = plaid.ApiClient(plaid_config)
        self.client = plaid_api.PlaidApi(api_client)
        self.access_token = config["access_token"]


class BalanceStream(PlaidStream):
    @property
    def name(self):
        return "balance"

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "account_id"

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        balance_response = self.client.accounts_balance_get(AccountsBalanceGetRequest(access_token=self.access_token))
        for balance in balance_response["accounts"]:
            message_dict = balance["balances"].to_dict()
            message_dict["account_id"] = balance["account_id"]
            message_dict["name"] = balance["name"]
            message_dict["official_name"] = balance["official_name"]
            message_dict["plaid_item_id"] = balance_response["item"]["item_id"]
            message_dict["plaid_institution_id"] = balance_response["item"]["institution_id"]
            yield message_dict


class IncrementalTransactionStream(PlaidStream):
    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "transaction_id"

    @property
    def name(self):
        return "transaction"

    @property
    def source_defined_cursor(self) -> bool:
        return True

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        return "date"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        return {"date": latest_record.get("date")}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        date = stream_state.get("date")
        if not date:
            date = datetime.date.fromtimestamp(0)
        else:
            date = datetime.date.fromisoformat(date)
        if date >= datetime.datetime.utcnow().date():
            return

        transaction_response = self.client.transactions_get(
            TransactionsGetRequest(access_token=self.access_token, start_date=date, end_date=datetime.datetime.utcnow().date())
        )

        transactions = transaction_response['transactions']

        while len(transactions) < transaction_response['total_transactions']:
            # rate limit is 30 requests per minute per item, so sleep for 2 seconds between requests
            time.sleep(2)
            transaction_response = self.client.transactions_get(
                TransactionsGetRequest(
                    access_token=self.access_token, 
                    start_date=date, 
                    end_date=datetime.datetime.utcnow().date(),
                    options=TransactionsGetRequestOptions(
                        offset=len(transactions)
                        )
                    )
                )
            
            transactions.extend(transaction_response['transactions'])

        yield from map(lambda x: x.to_dict(), sorted(transactions, key=lambda t: t["date"]))


class SourcePlaid(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        try:
            plaid_config = plaid.Configuration(
                host=SPEC_ENV_TO_PLAID_ENV[config["plaid_env"]], api_key={"clientId": config["client_id"], "secret": config["api_key"]}
            )
            api_client = plaid.ApiClient(plaid_config)
            client = plaid_api.PlaidApi(api_client)
            try:
                request = AccountsBalanceGetRequest(access_token=config["access_token"])
                client.accounts_balance_get(request)
                return True, None
            except plaid.ApiException as e:
                response = json.loads(e.body)
                return False, response
        except Exception as error:
            return False, error

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [BalanceStream(config), IncrementalTransactionStream(config)]
