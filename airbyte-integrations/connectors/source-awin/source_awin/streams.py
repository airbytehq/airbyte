#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream


class AwinStream(HttpStream, ABC):
    url_base = "https://api.awin.com/"

    def __init__(self, accounts: List[str], start_date: str, attribution_window: int, **kargs) -> None:
        super().__init__(**kargs)
        self._accounts = accounts
        self._start_date = start_date
        self._attribution_window = attribution_window

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json()
    
    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        From the documentation:
            To guarantee smooth operation for all our publishers and advertisers, we currently have a throttling in place that
            limits the number of API requests to 20 API calls per minute per user.

        See https://wiki.awin.com/index.php/Advertiser_API
        """
        return 60.0


class Accounts(AwinStream):
    """
    Call GET accounts

    See https://wiki.awin.com/index.php/API_get_accounts
    """
    primary_key = "accountId"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "accounts"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return response.json().get('accounts', [])


class Publishers(AwinStream):
    """
    Call GET publishers

    See https://wiki.awin.com/index.php/API_get_publishers
    """
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"advertisers/{stream_slice['account_id']}/publishers"

    def stream_slices(self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Optional[Mapping[str, Any]]]:
        if self._accounts:
            yield from [{"account_id": id} for id in self._accounts]
        else:
            account_stream = Accounts(accounts=self._accounts, start_date=self._start_date, attribution_window=self._attribution_window, authenticator=self.authenticator)
            for account in account_stream.read_records(sync_mode=SyncMode.full_refresh, stream_state=stream_state):
                if account.get("accountType", None) == "advertiser":
                    yield {"account_id": account["accountId"]}


class IncrementalAwinStream(AwinStream, IncrementalMixin):
    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


class AdvertiserTransactions(IncrementalAwinStream):
    """
    Call GET transactions (list)

    See https://wiki.awin.com/index.php/API_get_transactions_list
    """
    primary_key = "id"

    cursor_field = "transactionDate"
    date_template = "%Y-%m-%dT%H:%M:%S"

    MAX_ATTRIBUTION_DAYS = 31

    _cursor_value = {}
    _current_slice = {}

    @property
    def window_in_days(self) -> int:
        """
        The attribution window used for this stream
        """
        if self._attribution_window:
            if self._attribution_window > self.MAX_ATTRIBUTION_DAYS:
                return self.MAX_ATTRIBUTION_DAYS
            else:
                return self._attribution_window
        else:
            return self.MAX_ATTRIBUTION_DAYS

    def stream_slice_accounts(self, stream_state: Mapping[str, Any] = None) -> Iterable[Optional[Mapping[str, any]]]:
        if self._accounts:
            yield from [{"account_id": id} for id in self._accounts]
        else:
            account_stream = Accounts(accounts=self._accounts, start_date=self._start_date, attribution_window=self._attribution_window, authenticator=self.authenticator)
            for account in account_stream.read_records(sync_mode=SyncMode.full_refresh, stream_state=stream_state):
                if account.get("accountType", None) == "advertiser":
                    yield {"account_id": account["accountId"]}

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for slice in self.stream_slice_accounts(stream_state=stream_state):
            since_value = pendulum.parse(stream_state.get(slice["account_id"])) if stream_state else None

            start = since_value or self._start_date
            end = pendulum.now()

            while start <= end:
                slice_end = start.add(days=self.window_in_days).subtract(seconds=1)
                slice.update({
                    "date_from": start,
                    "date_to": slice_end
                })
                start = start.add(days=self.window_in_days)

                yield slice

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["startDate"] = stream_slice['date_from'].strftime(self.date_template)
        params["endDate"] = stream_slice['date_to'].strftime(self.date_template)
        params["timezone"] = "UTC"
        params["dateType"] = "transaction"
        return params

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self._current_slice['account_id']: self._cursor_value[self._current_slice['account_id']].strftime("%Y-%m-%dT%H:%M:%S")}
        else:
            return {self._current_slice['account_id']: self._start_date.strftime("%Y-%m-%dT%H:%M:%S")}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        for key, dict_value in value.items():
            self._cursor_value[key] = pendulum.parse(dict_value)

    def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"advertisers/{stream_slice['account_id']}/transactions/"

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) -> Iterable[StreamData]:
        self._current_slice = stream_slice
        account_id = stream_slice['account_id']
        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            if self._cursor_value[account_id]:
                latest_record_date = pendulum.parse(record[self.cursor_field])
                self._cursor_value[account_id] = max(self._cursor_value[account_id], latest_record_date)
            yield record

        if account_id in self._cursor_value:
            self._cursor_value[account_id] = max(self._cursor_value[account_id], stream_slice["date_to"])
        else:
            self._cursor_value[account_id] = stream_slice["date_to"]
