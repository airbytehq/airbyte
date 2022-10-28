#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import datetime
from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class PagarmeStream(HttpStream, ABC):
    page = 1
    page_size_limit = 1000
    primary_key = "id"
    url_base = "https://api.pagar.me/1/"

    def __init__(self, api_key, start_date=None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self._start_date = start_date

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if response.json():
            self.page = self.page + 1
            return self.page
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"count": self.page_size_limit}
        if next_page_token:
            params.update({"page": self.page})
        return params

    def request_body_json(self, **kwargs) -> Optional[Mapping]:
        body = {"api_key": self.api_key}
        return body

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response = response.json()
        yield from response


class IncrementalPagarmeStream(PagarmeStream, ABC):
    filter_field = ""
    state_checkpoint_interval = 1000

    @property
    def cursor_field(self) -> str:
        return "date_created"

    def request_body_json(self, stream_state: Mapping[str, Any], **kwargs) -> Optional[Mapping]:
        start_date = self._string_to_timestampmillis(self._start_date)
        if start_date:
            if stream_state.get(self.cursor_field):
                start_date = max(self._string_to_timestampmillis(stream_state[self.cursor_field]), start_date)
            if self.filter_field == "start_date":
                body = {"api_key": self.api_key, self.filter_field: f"{start_date}"}
            else:
                body = {"api_key": self.api_key, self.filter_field: f">{start_date}"}
        else:
            body = {"api_key": self.api_key}
        return body

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {self.cursor_field: max(latest_benchmark, current_stream_state[self.cursor_field])}
        return {self.cursor_field: latest_benchmark}

    def _string_to_timestampmillis(self, date_string):
        date_as_datetime = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        timestamp = datetime.datetime.timestamp(date_as_datetime)
        return int(timestamp) * 1000


class Balance(IncrementalPagarmeStream):
    filter_field = "start_date"

    def path(self, **kwargs) -> str:
        return "balance/operations"


class BankAccounts(PagarmeStream):
    def path(self, **kwargs) -> str:
        return "bank_Accounts"


class Cards(PagarmeStream):
    def path(self, **kwargs) -> str:
        return "cards"


class Chargebacks(IncrementalPagarmeStream):
    filter_field = "date_updated"

    @property
    def cursor_field(self) -> str:
        return "date_updated"

    def path(self, **kwargs) -> str:
        return "chargebacks"


class Customers(IncrementalPagarmeStream):
    filter_field = "created_at"

    def path(self, **kwargs) -> str:
        return "customers"


class Payables(IncrementalPagarmeStream):
    filter_field = "created_at"

    def path(self, **kwargs) -> str:
        return "payables"


class PaymentLinks(PagarmeStream):
    def path(self, **kwargs) -> str:
        return "payment_links"


class Plans(PagarmeStream):
    def path(self, **kwargs) -> str:
        return "plans"


class Recipients(PagarmeStream):
    def path(self, **kwargs) -> str:
        return "recipients"


class Refunds(IncrementalPagarmeStream):
    filter_field = "date_updated"

    @property
    def cursor_field(self) -> str:
        return "date_updated"

    def path(self, **kwargs) -> str:
        return "refunds"


class SecurityRules(PagarmeStream):
    def path(self, **kwargs) -> str:
        return "security_rules"


class Transactions(IncrementalPagarmeStream):
    filter_field = "date_updated"

    @property
    def cursor_field(self) -> str:
        return "date_updated"

    def path(self, **kwargs) -> str:
        return "transactions"


class Transfers(IncrementalPagarmeStream):
    filter_field = "date_updated"

    @property
    def cursor_field(self) -> str:
        return "date_updated"

    def path(self, **kwargs) -> str:
        return "transfers"
