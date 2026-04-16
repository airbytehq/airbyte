#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import requests
from requests_oauthlib import OAuth1

from airbyte_cdk.sources.streams.http import HttpStream


logger = logging.getLogger("airbyte")


class EtradeStream(HttpStream, ABC):
    """Base stream for E*TRADE API."""

    # E*TRADE API returns JSON
    response_format = "json"

    def __init__(self, auth: OAuth1, base_url: str, **kwargs: Any):
        self._auth = auth
        self._base_url = base_url
        # Pass None as authenticator since we handle auth via OAuth1 on the session
        super().__init__(authenticator=None, **kwargs)
        # Apply OAuth1 to the session
        self._session.auth = self._auth

    @property
    def url_base(self) -> str:
        return f"{self._base_url}/v1/"

    def request_headers(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, str]:
        return {"Accept": "application/json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {}

    def should_retry(self, response: requests.Response) -> bool:
        # Retry on 429 (rate limit) and 5xx errors
        if response.status_code == 429:
            return True
        if response.status_code >= 500:
            return True
        return False


class AccountScopedStream(EtradeStream, ABC):
    """Base stream for endpoints scoped to a specific account."""

    def __init__(self, account_id_keys: List[str], **kwargs: Any):
        self._account_id_keys = account_id_keys
        super().__init__(**kwargs)

    def stream_slices(
        self,
        sync_mode: str = None,
        cursor_field: List[str] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for account_id_key in self._account_id_keys:
            yield {"account_id_key": account_id_key}


class Accounts(EtradeStream):
    """Lists all E*TRADE accounts for the user."""

    primary_key = "accountIdKey"

    def path(self, **kwargs: Any) -> str:
        return "accounts/list"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping[str, Any]]:
        data = response.json()
        accounts = data.get("AccountListResponse", {}).get("Accounts", {}).get("Account", [])
        yield from accounts

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "accountId": {"type": ["null", "string"]},
                "accountIdKey": {"type": ["null", "string"]},
                "accountMode": {"type": ["null", "string"]},
                "accountDesc": {"type": ["null", "string"]},
                "accountName": {"type": ["null", "string"]},
                "accountType": {"type": ["null", "string"]},
                "institutionType": {"type": ["null", "string"]},
                "instNo": {"type": ["null", "integer"]},
                "accountStatus": {"type": ["null", "string"]},
                "closedDate": {"type": ["null", "integer"]},
                "shareWorksAccount": {"type": ["null", "boolean"]},
            },
        }


class Portfolio(AccountScopedStream):
    """Returns current holdings/positions for an account."""

    primary_key = None
    page_size = 50

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        account_id_key = stream_slice["account_id_key"]
        return f"accounts/{account_id_key}/portfolio"

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params: MutableMapping[str, Any] = {"count": self.page_size}
        if next_page_token:
            params["pageNumber"] = next_page_token["pageNumber"]
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        portfolio_response = data.get("PortfolioResponse", {})
        totals = portfolio_response.get("Totals", {})
        page_count = totals.get("totalPages", 1)
        current_page = totals.get("pageNumber", 0)
        if current_page < page_count - 1:
            return {"pageNumber": current_page + 1}
        return None

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping[str, Any]]:
        data = response.json()
        account_portfolios = data.get("PortfolioResponse", {}).get("AccountPortfolio", [])
        account_id_key = stream_slice["account_id_key"]
        for account_portfolio in account_portfolios:
            positions = account_portfolio.get("Position", [])
            for position in positions:
                position["accountIdKey"] = account_id_key
                yield position

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "accountIdKey": {"type": ["null", "string"]},
                "positionId": {"type": ["null", "integer"]},
                "symbolDescription": {"type": ["null", "string"]},
                "dateAcquired": {"type": ["null", "integer"]},
                "pricePaid": {"type": ["null", "number"]},
                "commissions": {"type": ["null", "number"]},
                "otherFees": {"type": ["null", "number"]},
                "quantity": {"type": ["null", "number"]},
                "positionIndicator": {"type": ["null", "string"]},
                "positionType": {"type": ["null", "string"]},
                "daysGain": {"type": ["null", "number"]},
                "daysGainPct": {"type": ["null", "number"]},
                "marketValue": {"type": ["null", "number"]},
                "totalCost": {"type": ["null", "number"]},
                "totalGain": {"type": ["null", "number"]},
                "totalGainPct": {"type": ["null", "number"]},
                "pctOfPortfolio": {"type": ["null", "number"]},
                "costPerShare": {"type": ["null", "number"]},
                "todayCommissions": {"type": ["null", "number"]},
                "todayFees": {"type": ["null", "number"]},
                "todayPricePaid": {"type": ["null", "number"]},
                "todayQuantity": {"type": ["null", "number"]},
                "adjPrevClose": {"type": ["null", "number"]},
                "change": {"type": ["null", "number"]},
                "changePct": {"type": ["null", "number"]},
                "lastTrade": {"type": ["null", "number"]},
                "volume": {"type": ["null", "integer"]},
                "lastTradeTime": {"type": ["null", "integer"]},
                "quoteStatus": {"type": ["null", "string"]},
                "lotsDetails": {"type": ["null", "string"]},
                "Product": {
                    "type": ["null", "object"],
                    "properties": {
                        "symbol": {"type": ["null", "string"]},
                        "securityType": {"type": ["null", "string"]},
                        "securitySubType": {"type": ["null", "string"]},
                        "callPut": {"type": ["null", "string"]},
                        "expiryYear": {"type": ["null", "integer"]},
                        "expiryMonth": {"type": ["null", "integer"]},
                        "expiryDay": {"type": ["null", "integer"]},
                        "strikePrice": {"type": ["null", "number"]},
                        "expiryType": {"type": ["null", "string"]},
                        "productId": {
                            "type": ["null", "object"],
                            "properties": {
                                "symbol": {"type": ["null", "string"]},
                                "typeCode": {"type": ["null", "string"]},
                            },
                        },
                    },
                },
                "Quick": {
                    "type": ["null", "object"],
                    "properties": {
                        "change": {"type": ["null", "number"]},
                        "changePct": {"type": ["null", "number"]},
                        "lastTrade": {"type": ["null", "number"]},
                        "lastTradeTime": {"type": ["null", "integer"]},
                        "volume": {"type": ["null", "integer"]},
                        "quoteStatus": {"type": ["null", "string"]},
                        "sevenDayCurrentYield": {"type": ["null", "number"]},
                        "annualTotalReturn": {"type": ["null", "number"]},
                        "weightedAverageMaturity": {"type": ["null", "number"]},
                    },
                },
            },
        }


class Balances(AccountScopedStream):
    """Returns account balances for an account."""

    primary_key = None

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        account_id_key = stream_slice["account_id_key"]
        return f"accounts/{account_id_key}/balance"

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {"instType": "BROKERAGE", "realTimeNAV": "true"}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping[str, Any]]:
        data = response.json()
        balance_response = data.get("BalanceResponse", {})
        if balance_response:
            balance_response["accountIdKey"] = stream_slice["account_id_key"]
            yield balance_response

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "accountIdKey": {"type": ["null", "string"]},
                "accountId": {"type": ["null", "string"]},
                "accountType": {"type": ["null", "string"]},
                "optionLevel": {"type": ["null", "string"]},
                "accountDescription": {"type": ["null", "string"]},
                "quoteMode": {"type": ["null", "integer"]},
                "dayTraderStatus": {"type": ["null", "string"]},
                "accountMode": {"type": ["null", "string"]},
                "Cash": {
                    "type": ["null", "object"],
                    "properties": {
                        "fundsForOpenOrdersCash": {"type": ["null", "number"]},
                        "moneyMktBalance": {"type": ["null", "number"]},
                    },
                },
                "Computed": {
                    "type": ["null", "object"],
                    "properties": {
                        "cashAvailableForInvestment": {"type": ["null", "number"]},
                        "cashAvailableForWithdrawal": {"type": ["null", "number"]},
                        "totalAvailableForWithdrawal": {"type": ["null", "number"]},
                        "netCash": {"type": ["null", "number"]},
                        "cashBalance": {"type": ["null", "number"]},
                        "settledCashForInvestment": {"type": ["null", "number"]},
                        "unSettledCashForInvestment": {"type": ["null", "number"]},
                        "fundsWithheldFromPurchasePower": {"type": ["null", "number"]},
                        "fundsWithheldFromWithdrawal": {"type": ["null", "number"]},
                        "marginBuyingPower": {"type": ["null", "number"]},
                        "cashBuyingPower": {"type": ["null", "number"]},
                        "dtMarginBuyingPower": {"type": ["null", "number"]},
                        "dtCashBuyingPower": {"type": ["null", "number"]},
                        "shortAdjustBalance": {"type": ["null", "number"]},
                        "regtEquity": {"type": ["null", "number"]},
                        "regtEquityPercent": {"type": ["null", "number"]},
                        "accountBalance": {"type": ["null", "number"]},
                        "RealTimeValues": {
                            "type": ["null", "object"],
                            "properties": {
                                "totalAccountValue": {"type": ["null", "number"]},
                                "netMv": {"type": ["null", "number"]},
                                "netMvLong": {"type": ["null", "number"]},
                                "netMvShort": {"type": ["null", "number"]},
                                "totalLongValue": {"type": ["null", "number"]},
                            },
                        },
                    },
                },
            },
        }


class Transactions(AccountScopedStream):
    """Lists transactions for an account with incremental support."""

    primary_key = "transactionId"
    cursor_field = "transactionDate"

    def __init__(self, start_date: str, **kwargs: Any):
        self._start_date = start_date
        super().__init__(**kwargs)

    @property
    def supports_incremental(self) -> bool:
        return True

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        account_id_key = stream_slice["account_id_key"]
        return f"accounts/{account_id_key}/transactions"

    def stream_slices(
        self,
        sync_mode: str = None,
        cursor_field: List[str] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for account_id_key in self._account_id_keys:
            yield {
                "account_id_key": account_id_key,
                "start_date": self._get_start_date(stream_state, account_id_key),
            }

    def _get_start_date(self, stream_state: Optional[Mapping[str, Any]], account_id_key: str) -> str:
        if stream_state:
            # State is stored per account
            account_state = stream_state.get(account_id_key, {})
            cursor_value = account_state.get(self.cursor_field)
            if cursor_value:
                return cursor_value
        return self._start_date

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params: MutableMapping[str, Any] = {"sortOrder": "ASC"}

        start_date = stream_slice.get("start_date", self._start_date) if stream_slice else self._start_date
        # E*TRADE expects MMDDYYYY format
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        params["startDate"] = start_dt.strftime("%m%d%Y")

        end_dt = datetime.now()
        params["endDate"] = end_dt.strftime("%m%d%Y")

        if next_page_token:
            params["marker"] = next_page_token["marker"]
        params["count"] = 50

        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        transaction_response = data.get("TransactionListResponse", {})
        marker = transaction_response.get("marker")
        if marker:
            return {"marker": marker}
        return None

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping[str, Any]]:
        data = response.json()
        transactions = data.get("TransactionListResponse", {}).get("Transaction", [])
        account_id_key = stream_slice["account_id_key"]
        for transaction in transactions:
            transaction["accountIdKey"] = account_id_key
            yield transaction

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        account_id_key = latest_record.get("accountIdKey", "")
        record_date = latest_record.get(self.cursor_field, "")
        if record_date:
            # Normalize transaction date to YYYY-MM-DD
            if isinstance(record_date, int):
                # Unix timestamp in milliseconds
                record_date = datetime.fromtimestamp(record_date / 1000).strftime("%Y-%m-%d")

            current_account_state = current_stream_state.get(account_id_key, {})
            current_cursor = current_account_state.get(self.cursor_field, "")
            if record_date > current_cursor:
                current_stream_state[account_id_key] = {self.cursor_field: record_date}
        return current_stream_state

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "accountIdKey": {"type": ["null", "string"]},
                "transactionId": {"type": ["null", "integer"]},
                "transactionDate": {"type": ["null", "integer"]},
                "postDate": {"type": ["null", "integer"]},
                "amount": {"type": ["null", "number"]},
                "description": {"type": ["null", "string"]},
                "description2": {"type": ["null", "string"]},
                "memo": {"type": ["null", "string"]},
                "storeId": {"type": ["null", "integer"]},
                "imageFlag": {"type": ["null", "boolean"]},
                "transactionType": {"type": ["null", "string"]},
                "Category": {
                    "type": ["null", "object"],
                    "properties": {
                        "categoryId": {"type": ["null", "string"]},
                        "parentId": {"type": ["null", "string"]},
                        "categoryName": {"type": ["null", "string"]},
                        "parentName": {"type": ["null", "string"]},
                    },
                },
                "Brokerage": {
                    "type": ["null", "object"],
                    "properties": {
                        "transactionType": {"type": ["null", "string"]},
                        "quantity": {"type": ["null", "number"]},
                        "price": {"type": ["null", "number"]},
                        "settlementCurrency": {"type": ["null", "string"]},
                        "paymentCurrency": {"type": ["null", "string"]},
                        "fee": {"type": ["null", "number"]},
                        "memo": {"type": ["null", "string"]},
                        "checkNo": {"type": ["null", "string"]},
                        "orderNo": {"type": ["null", "string"]},
                        "Product": {
                            "type": ["null", "object"],
                            "properties": {
                                "symbol": {"type": ["null", "string"]},
                                "securityType": {"type": ["null", "string"]},
                                "securitySubType": {"type": ["null", "string"]},
                                "callPut": {"type": ["null", "string"]},
                                "expiryYear": {"type": ["null", "integer"]},
                                "expiryMonth": {"type": ["null", "integer"]},
                                "expiryDay": {"type": ["null", "integer"]},
                                "strikePrice": {"type": ["null", "number"]},
                                "expiryType": {"type": ["null", "string"]},
                            },
                        },
                    },
                },
            },
        }


class TransactionDetails(AccountScopedStream):
    """Returns detailed information for a specific transaction.
    This stream reads from the Transactions stream to get transaction IDs,
    then fetches details for each.
    """

    primary_key = "transactionId"

    def __init__(self, start_date: str, **kwargs: Any):
        self._start_date = start_date
        super().__init__(**kwargs)

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        account_id_key = stream_slice["account_id_key"]
        transaction_id = stream_slice["transaction_id"]
        return f"accounts/{account_id_key}/transactions/{transaction_id}"

    def stream_slices(
        self,
        sync_mode: str = None,
        cursor_field: List[str] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """Generate slices from parent Transactions stream."""
        transactions_stream = Transactions(
            auth=self._auth,
            base_url=self._base_url,
            account_id_keys=self._account_id_keys,
            start_date=self._start_date,
        )
        for parent_slice in transactions_stream.stream_slices(stream_state=stream_state):
            for record in transactions_stream.read_records(
                sync_mode="full_refresh",
                stream_slice=parent_slice,
            ):
                transaction_id = record.get("transactionId")
                if transaction_id:
                    yield {
                        "account_id_key": parent_slice["account_id_key"],
                        "transaction_id": transaction_id,
                    }

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping[str, Any]]:
        data = response.json()
        transaction = data.get("TransactionDetailsResponse", {})
        if transaction:
            transaction["accountIdKey"] = stream_slice["account_id_key"]
            yield transaction

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "accountIdKey": {"type": ["null", "string"]},
                "transactionId": {"type": ["null", "integer"]},
                "transactionDate": {"type": ["null", "integer"]},
                "postDate": {"type": ["null", "integer"]},
                "amount": {"type": ["null", "number"]},
                "description": {"type": ["null", "string"]},
                "description2": {"type": ["null", "string"]},
                "memo": {"type": ["null", "string"]},
                "transactionType": {"type": ["null", "string"]},
                "Category": {
                    "type": ["null", "object"],
                    "properties": {
                        "categoryId": {"type": ["null", "string"]},
                        "parentId": {"type": ["null", "string"]},
                        "categoryName": {"type": ["null", "string"]},
                        "parentName": {"type": ["null", "string"]},
                    },
                },
                "Brokerage": {
                    "type": ["null", "object"],
                    "properties": {
                        "transactionType": {"type": ["null", "string"]},
                        "quantity": {"type": ["null", "number"]},
                        "price": {"type": ["null", "number"]},
                        "settlementCurrency": {"type": ["null", "string"]},
                        "paymentCurrency": {"type": ["null", "string"]},
                        "fee": {"type": ["null", "number"]},
                        "settlementDate": {"type": ["null", "integer"]},
                        "Product": {
                            "type": ["null", "object"],
                            "properties": {
                                "symbol": {"type": ["null", "string"]},
                                "securityType": {"type": ["null", "string"]},
                            },
                        },
                    },
                },
            },
        }


class Orders(AccountScopedStream):
    """Lists orders for an account with incremental support."""

    primary_key = "orderId"
    cursor_field = "orderPlacedTime"

    def __init__(self, start_date: str, **kwargs: Any):
        self._start_date = start_date
        super().__init__(**kwargs)

    @property
    def supports_incremental(self) -> bool:
        return True

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        account_id_key = stream_slice["account_id_key"]
        return f"accounts/{account_id_key}/orders"

    def stream_slices(
        self,
        sync_mode: str = None,
        cursor_field: List[str] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for account_id_key in self._account_id_keys:
            yield {
                "account_id_key": account_id_key,
                "start_date": self._get_start_date(stream_state, account_id_key),
            }

    def _get_start_date(self, stream_state: Optional[Mapping[str, Any]], account_id_key: str) -> str:
        if stream_state:
            account_state = stream_state.get(account_id_key, {})
            cursor_value = account_state.get(self.cursor_field)
            if cursor_value:
                return cursor_value
        return self._start_date

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params: MutableMapping[str, Any] = {"count": 100}

        start_date = stream_slice.get("start_date", self._start_date) if stream_slice else self._start_date
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        params["fromDate"] = start_dt.strftime("%m%d%Y")

        end_dt = datetime.now()
        params["toDate"] = end_dt.strftime("%m%d%Y")

        if next_page_token:
            params["marker"] = next_page_token["marker"]

        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        order_response = data.get("OrdersResponse", {})
        marker = order_response.get("marker")
        if marker:
            return {"marker": marker}
        return None

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping[str, Any]]:
        data = response.json()
        orders_response = data.get("OrdersResponse", {})
        orders = orders_response.get("Order", [])
        account_id_key = stream_slice["account_id_key"]
        for order in orders:
            order["accountIdKey"] = account_id_key
            yield order

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        account_id_key = latest_record.get("accountIdKey", "")
        record_value = latest_record.get(self.cursor_field, 0)
        if record_value:
            if isinstance(record_value, int):
                record_date = datetime.fromtimestamp(record_value / 1000).strftime("%Y-%m-%d")
            else:
                record_date = str(record_value)

            current_account_state = current_stream_state.get(account_id_key, {})
            current_cursor = current_account_state.get(self.cursor_field, "")
            if record_date > current_cursor:
                current_stream_state[account_id_key] = {self.cursor_field: record_date}
        return current_stream_state

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "accountIdKey": {"type": ["null", "string"]},
                "orderId": {"type": ["null", "integer"]},
                "orderPlacedTime": {"type": ["null", "integer"]},
                "orderExecutedTime": {"type": ["null", "integer"]},
                "orderValue": {"type": ["null", "number"]},
                "orderStatus": {"type": ["null", "string"]},
                "orderType": {"type": ["null", "string"]},
                "orderTerm": {"type": ["null", "string"]},
                "priceType": {"type": ["null", "string"]},
                "limitPrice": {"type": ["null", "number"]},
                "stopPrice": {"type": ["null", "number"]},
                "marketSession": {"type": ["null", "string"]},
                "allOrNone": {"type": ["null", "boolean"]},
                "netPrice": {"type": ["null", "number"]},
                "netBid": {"type": ["null", "number"]},
                "netAsk": {"type": ["null", "number"]},
                "gcd": {"type": ["null", "integer"]},
                "ratio": {"type": ["null", "string"]},
                "replacedByOrderId": {"type": ["null", "integer"]},
                "replacesOrderId": {"type": ["null", "integer"]},
                "OrderDetail": {
                    "type": ["null", "array"],
                    "items": {
                        "type": ["null", "object"],
                        "properties": {
                            "orderNumber": {"type": ["null", "integer"]},
                            "accountId": {"type": ["null", "string"]},
                            "placedTime": {"type": ["null", "integer"]},
                            "executedTime": {"type": ["null", "integer"]},
                            "orderValue": {"type": ["null", "number"]},
                            "status": {"type": ["null", "string"]},
                            "orderType": {"type": ["null", "string"]},
                            "orderTerm": {"type": ["null", "string"]},
                            "priceType": {"type": ["null", "string"]},
                            "limitPrice": {"type": ["null", "number"]},
                            "stopPrice": {"type": ["null", "number"]},
                            "marketSession": {"type": ["null", "string"]},
                            "allOrNone": {"type": ["null", "boolean"]},
                            "netPrice": {"type": ["null", "number"]},
                            "netBid": {"type": ["null", "number"]},
                            "netAsk": {"type": ["null", "number"]},
                            "Instrument": {
                                "type": ["null", "array"],
                                "items": {
                                    "type": ["null", "object"],
                                    "properties": {
                                        "symbolDescription": {"type": ["null", "string"]},
                                        "orderAction": {"type": ["null", "string"]},
                                        "quantityType": {"type": ["null", "string"]},
                                        "orderedQuantity": {"type": ["null", "number"]},
                                        "filledQuantity": {"type": ["null", "number"]},
                                        "estimatedCommission": {"type": ["null", "number"]},
                                        "estimatedFees": {"type": ["null", "number"]},
                                        "averageExecutionPrice": {"type": ["null", "number"]},
                                        "Product": {
                                            "type": ["null", "object"],
                                            "properties": {
                                                "symbol": {"type": ["null", "string"]},
                                                "securityType": {"type": ["null", "string"]},
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }


class Quotes(EtradeStream):
    """Returns market quotes for symbols found in the user's portfolio."""

    primary_key = None

    def __init__(self, account_id_keys: List[str], **kwargs: Any):
        self._account_id_keys = account_id_keys
        super().__init__(**kwargs)

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        symbols = stream_slice.get("symbols", "") if stream_slice else ""
        return f"market/quote/{symbols}"

    def stream_slices(
        self,
        sync_mode: str = None,
        cursor_field: List[str] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """Collect symbols from all portfolios, then batch into groups of 25."""
        all_symbols = set()
        for account_id_key in self._account_id_keys:
            portfolio_stream = Portfolio(
                auth=self._auth,
                base_url=self._base_url,
                account_id_keys=[account_id_key],
            )
            for portfolio_slice in portfolio_stream.stream_slices():
                for record in portfolio_stream.read_records(
                    sync_mode="full_refresh",
                    stream_slice=portfolio_slice,
                ):
                    product = record.get("Product", {})
                    symbol = product.get("symbol") if product else None
                    if symbol:
                        all_symbols.add(symbol)

        # Batch symbols into groups of 25 (E*TRADE API limit)
        symbols_list = sorted(all_symbols)
        for i in range(0, max(len(symbols_list), 1), 25):
            batch = symbols_list[i : i + 25]
            if batch:
                yield {"symbols": ",".join(batch)}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping[str, Any]]:
        data = response.json()
        quote_response = data.get("QuoteResponse", {})
        quote_data = quote_response.get("QuoteData", [])
        yield from quote_data

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "dateTime": {"type": ["null", "string"]},
                "dateTimeUTC": {"type": ["null", "integer"]},
                "quoteStatus": {"type": ["null", "string"]},
                "ahFlag": {"type": ["null", "string"]},
                "hasMiniOptions": {"type": ["null", "boolean"]},
                "Product": {
                    "type": ["null", "object"],
                    "properties": {
                        "symbol": {"type": ["null", "string"]},
                        "securityType": {"type": ["null", "string"]},
                    },
                },
                "All": {
                    "type": ["null", "object"],
                    "properties": {
                        "adjustedFlag": {"type": ["null", "boolean"]},
                        "annualDividend": {"type": ["null", "number"]},
                        "ask": {"type": ["null", "number"]},
                        "askSize": {"type": ["null", "integer"]},
                        "askTime": {"type": ["null", "string"]},
                        "bid": {"type": ["null", "number"]},
                        "bidExchange": {"type": ["null", "string"]},
                        "bidSize": {"type": ["null", "integer"]},
                        "bidTime": {"type": ["null", "string"]},
                        "changeClose": {"type": ["null", "number"]},
                        "changeClosePercentage": {"type": ["null", "number"]},
                        "companyName": {"type": ["null", "string"]},
                        "daysToExpiration": {"type": ["null", "integer"]},
                        "dirLast": {"type": ["null", "string"]},
                        "dividend": {"type": ["null", "number"]},
                        "eps": {"type": ["null", "number"]},
                        "estEarnings": {"type": ["null", "number"]},
                        "exDividendDate": {"type": ["null", "integer"]},
                        "high": {"type": ["null", "number"]},
                        "high52": {"type": ["null", "number"]},
                        "lastTrade": {"type": ["null", "number"]},
                        "low": {"type": ["null", "number"]},
                        "low52": {"type": ["null", "number"]},
                        "open": {"type": ["null", "number"]},
                        "openInterest": {"type": ["null", "integer"]},
                        "optionStyle": {"type": ["null", "string"]},
                        "optionUnderlier": {"type": ["null", "string"]},
                        "previousClose": {"type": ["null", "number"]},
                        "previousDayVolume": {"type": ["null", "integer"]},
                        "primaryExchange": {"type": ["null", "string"]},
                        "symbolDescription": {"type": ["null", "string"]},
                        "totalVolume": {"type": ["null", "integer"]},
                        "upc": {"type": ["null", "integer"]},
                        "pe": {"type": ["null", "number"]},
                        "week52LowDate": {"type": ["null", "integer"]},
                        "week52HiDate": {"type": ["null", "integer"]},
                        "cashDeliverable": {"type": ["null", "number"]},
                        "marketCap": {"type": ["null", "number"]},
                        "sharesOutstanding": {"type": ["null", "number"]},
                        "nextEarningDate": {"type": ["null", "string"]},
                        "beta": {"type": ["null", "number"]},
                        "yield": {"type": ["null", "number"]},
                        "declaredDividend": {"type": ["null", "number"]},
                        "dividendPayableDate": {"type": ["null", "integer"]},
                        "cusip": {"type": ["null", "string"]},
                    },
                },
            },
        }


class ProductLookup(EtradeStream):
    """Searches securities by company name. Returns a fixed lookup result set."""

    primary_key = None

    def path(self, **kwargs: Any) -> str:
        # Default search for common symbols
        return "market/lookup/A"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping[str, Any]]:
        data = response.json()
        lookup_response = data.get("LookupResponse", {})
        results = lookup_response.get("Data", [])
        yield from results

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "symbol": {"type": ["null", "string"]},
                "description": {"type": ["null", "string"]},
                "type": {"type": ["null", "string"]},
                "exchange": {"type": ["null", "string"]},
            },
        }


class Alerts(EtradeStream):
    """Lists account and stock alerts."""

    primary_key = "id"

    def path(self, **kwargs: Any) -> str:
        return "user/alerts"

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        return {"count": 300, "direction": "DESC"}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping[str, Any]]:
        data = response.json()
        alerts_response = data.get("AlertsResponse", {})
        alerts = alerts_response.get("Alert", [])
        yield from alerts

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["null", "integer"]},
                "createTime": {"type": ["null", "integer"]},
                "subject": {"type": ["null", "string"]},
                "status": {"type": ["null", "string"]},
                "category": {"type": ["null", "string"]},
                "readTime": {"type": ["null", "integer"]},
                "deleteTime": {"type": ["null", "integer"]},
                "symbol": {"type": ["null", "string"]},
            },
        }


class AlertDetails(EtradeStream):
    """Returns detailed information for a specific alert."""

    primary_key = "id"

    def path(
        self,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        alert_id = stream_slice.get("alert_id", "") if stream_slice else ""
        return f"user/alerts/{alert_id}"

    def stream_slices(
        self,
        sync_mode: str = None,
        cursor_field: List[str] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """Generate slices from parent Alerts stream."""
        alerts_stream = Alerts(
            auth=self._auth,
            base_url=self._base_url,
        )
        for record in alerts_stream.read_records(sync_mode="full_refresh"):
            alert_id = record.get("id")
            if alert_id:
                yield {"alert_id": alert_id}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> Iterable[Mapping[str, Any]]:
        data = response.json()
        alert_details = data.get("AlertDetailsResponse", {})
        if alert_details:
            yield alert_details

    def get_json_schema(self) -> Mapping[str, Any]:
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "id": {"type": ["null", "integer"]},
                "createTime": {"type": ["null", "integer"]},
                "subject": {"type": ["null", "string"]},
                "msgText": {"type": ["null", "string"]},
                "readTime": {"type": ["null", "integer"]},
                "deleteTime": {"type": ["null", "integer"]},
                "symbol": {"type": ["null", "string"]},
                "next": {"type": ["null", "string"]},
            },
        }
