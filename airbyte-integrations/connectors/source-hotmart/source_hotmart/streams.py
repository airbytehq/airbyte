import pendulum
from abc import ABC, abstractmethod
import requests

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from typing import Optional, Mapping, Any, MutableMapping, Iterable, Tuple, List
from pendulum import DateTime

from .utils import parse_single_record

HOTMART_ERROR_MAPPING: Mapping[int, str] = {
    400: "The request sent has something invalid",
    401: "Missing authorization permissions or expired token",
    403: "You don't have enough permissions to consume this stream",
    404: "The object specified by the request does not exist",
}

HOTMART_TRANSACTION_STATUS = [
    "APPROVED",
    "BLOCKED",
    "CANCELLED",
    "CHARGEBACK",
    "COMPLETE",
    "EXPIRED",
    "NO_FUNDS",
    "OVERDUE",
    "PARTIALLY_REFUNDED",
    "PRE_ORDER",
    "PRINTED_BILLET",
    "PROCESSING_TRANSACTION",
    "PROTESTED",
    "REFUNDED",
    "STARTED",
    "UNDER_ANALISYS",
    "WAITING_PAYMENT",
]


class HotmartStream(HttpStream, ABC):
    url_base = "https://developers.hotmart.com/payments/api/v1/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get("items", [])

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code in HOTMART_ERROR_MAPPING.keys():
            self.logger.error(
                f"Skipping stream {self.name}. {HOTMART_ERROR_MAPPING.get(response.status_code)}. Full error message: {response.text}"
            )
            return False
        return super().should_retry(response)

    def backoff_time(self, response: requests.Response) -> Optional[int]:
        delay_time = response.headers.get("RateLimit-Reset", 30)
        return int(delay_time)

class HotmartStreamPaginated(HotmartStream, ABC):
    DEFAULT_PAGE_SIZE = 500

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()

        if not "page_info" in decoded_response or not "next_page_token" in decoded_response["page_info"]:
            return None

        return {"page_token": decoded_response["page_info"]["next_page_token"]}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["max_results"] = self.DEFAULT_PAGE_SIZE

        return {**params, **next_page_token} if next_page_token else params


class SalesRelatedStream(HotmartStreamPaginated, ABC):
    DEFAULT_SLICE_RANGE = 30

    def __init__(self, start_date: int, slice_range: int = DEFAULT_SLICE_RANGE, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.slice_range = slice_range
        self.schema = self.get_json_schema()

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)

        if stream_slice:
            params["transaction_status"] = stream_slice["transaction_status"]
            params["start_date"] = stream_slice["start_date"] * 1000  # start_date must be in milliseconds
            params["end_date"] = stream_slice["end_date"] * 1000  # end_date must be in milliseconds

        return {**params, **next_page_token} if next_page_token else params

    def _chunk_dates(self, start_date: int) -> Iterable[Tuple[int, int]]:
        now = pendulum.now().int_timestamp
        step = int(pendulum.duration(days=self.slice_range).total_seconds())
        start_point = start_date
        since_date = start_point
        while since_date < now:
            until_date = min(now, since_date + step)
            yield since_date, until_date
            since_date = until_date + 1

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        for status in HOTMART_TRANSACTION_STATUS:
            for since_date, until_date in self._chunk_dates(self.start_date):
                yield {
                    "transaction_status": status,
                    "start_date": since_date,
                    "end_date": until_date
                }


class IncrementalSalesRelatedStream(SalesRelatedStream, IncrementalMixin, ABC):
    _cursor_value = 0

    @property
    def state(self) -> Mapping[str, Any]:
        return {self.cursor_field: int(self._cursor_value)}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = int(value[self.cursor_field])

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        pass

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        if sync_mode == SyncMode.full_refresh:
            yield from super().stream_slices(sync_mode=sync_mode, cursor_field=None, stream_state=None)
        else:
            stream_state = stream_state or {}

            start_date = stream_state.get(self.cursor_field, self.start_date)

            if start_date >= pendulum.now().int_timestamp:
                yield None
            else:
                for status in HOTMART_TRANSACTION_STATUS:
                    for since_date, until_date in self._chunk_dates(start_date):
                        yield {
                            "transaction_status": status,
                            "start_date": since_date,
                            "end_date": until_date
                        }

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: MutableMapping[str, Any] = None,
        **kwargs,
    ) -> Iterable[Mapping[str, Any]]:
        if sync_mode == SyncMode.incremental and not stream_slice:
            pass

        else:
            records = super().read_records(sync_mode, stream_slice=stream_slice)

            for record in records:
                yield record

                if sync_mode == SyncMode.incremental:
                    self._cursor_value = max(
                        int(record[self.cursor_field]),
                        int(self._cursor_value)
                    )

class SalesHistory(IncrementalSalesRelatedStream):
    """
    Docs: https://developers.hotmart.com/docs/en/v1/sales/sales-history/
    """
    primary_key = ["purchase.transaction", "purchase.status"]
    cursor_field = "purchase.order_date"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json.get("items", [])
        for record in records:
            record["purchase"]["order_date"] = int(int(record["purchase"]["order_date"]) / 1000)
            yield parse_single_record(self.schema, record)

    def path(self, **kwargs) -> str:
        return "sales/history"


class SalesCommissions(SalesRelatedStream):
    """
    Docs: https://developers.hotmart.com/docs/en/v1/sales/sales-commissions/
    """
    primary_key = ["transaction", "user.ucode"]

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json.get("items", [])

        for record in records:
            common_fields = ["transaction", "product", "exchange_rate_currency_payout"]
            common = {field: record[field] for field in common_fields}

            for item in record["commissions"]:
                yield parse_single_record(self.schema, {**common, **item})

    def path(self, **kwargs) -> str:
        return "sales/commissions"


class SalesPriceDetails(SalesRelatedStream):
    """
    Docs: https://developers.hotmart.com/docs/en/v1/sales/sales-price-details/
    """
    primary_key = "transaction"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json.get("items", [])

        for record in records:
            yield parse_single_record(self.schema, record)

    def path(self, **kwargs) -> str:
        return "sales/price/details"


class SalesUsers(SalesRelatedStream):
    """
    Docs: https://developers.hotmart.com/docs/en/v1/sales/sales-users/
    """
    primary_key = ["transaction", "user.ucode", "role"]

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json.get("items", [])

        common_fields = ["transaction", "product"]
        for record in records:
            common = {field: record[field] for field in common_fields}

            for item in record["users"]:
                del item["user"]["documents"]
                yield parse_single_record(self.schema, {**common, **item})

    def path(self, **kwargs) -> str:
        return "sales/users"
