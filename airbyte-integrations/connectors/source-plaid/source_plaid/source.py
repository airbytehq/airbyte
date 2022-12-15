#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
import json
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import plaid
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from plaid.api import plaid_api
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.accounts_balance_get_request_options import AccountsBalanceGetRequestOptions
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
        self.start_date = datetime.datetime.strptime(config.get("start_date"), "%Y-%m-%d").date() if config.get("start_date") else None


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
        min_last_updated_datetime = datetime.datetime.strptime(
            datetime.datetime.strftime(self.start_date, "%y-%m-%dT%H:%M:%SZ"),
            "%y-%m-%dT%H:%M:%S%z",
        )
        options = AccountsBalanceGetRequestOptions(min_last_updated_datetime=min_last_updated_datetime)
        getRequest = AccountsBalanceGetRequest(access_token=self.access_token, options=options)
        balance_response = self.client.accounts_balance_get(getRequest)
        for balance in balance_response["accounts"]:
            message_dict = balance["balances"].to_dict()
            message_dict["account_id"] = balance["account_id"]
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

    def _get_transactions_response(self, start_date, end_date=datetime.datetime.utcnow().date(), offset=0):
        options = TransactionsGetRequestOptions()
        options.offset = offset

        return self.client.transactions_get(
            TransactionsGetRequest(access_token=self.access_token, start_date=start_date, end_date=end_date, options=options)
        )

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        date = stream_state.get("date")
        all_transactions = []

        if not date:
            date = datetime.date.fromtimestamp(0)
        else:
            date = datetime.date.fromisoformat(date)
        if date >= datetime.datetime.utcnow().date():
            return

        if self.start_date:
            date = max(self.start_date, date)

        response = self._get_transactions_response(date)
        all_transactions.extend(response.transactions)
        num_total_transactions = response.total_transactions

        while len(all_transactions) < num_total_transactions:
            response = self._get_transactions_response(date, offset=len(all_transactions))
            all_transactions.extend(response.transactions)

        yield from map(lambda x: x.to_dict(), sorted(all_transactions, key=lambda t: t["date"]))


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
