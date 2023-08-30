import time
from abc import ABC
from datetime import date
from typing import Mapping, Any, Iterable, Type, Optional, List, Dict

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from requests.exceptions import ChunkedEncodingError

from source_wildberries_statistics.schemas import Income, Stock, Order, Sale, ReportDetailByPeriod
from source_wildberries_statistics.types import WildberriesCredentials, IsSuccess, Message, SchemaT


def check_statistics_stream_connection(credentials: WildberriesCredentials) -> tuple[IsSuccess, Optional[Message]]:
    url = "https://statistics-api-sandbox.wildberries.ru/api/v1/supplier/incomes" + f"?dateFrom={date.today().isoformat()}"
    headers = {"Authorization": credentials["api_key"]}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return True, None
        elif response.status_code == 401:
            return False, f"Invalid statistics API key. Response status code: {response.status_code}. Body: {response.text}"
        else:
            return False, f"Response status code: {response.status_code}. Body: {response.text}"
    except Exception as e:
        return False, str(e)


class StatisticsStream(Stream, ABC):
    SCHEMA: Type[SchemaT] = NotImplemented
    URL: str = NotImplemented

    def __init__(self, credentials: WildberriesCredentials, date_from: date):
        self.credentials = credentials
        self.date_from = date_from

    @property
    def primary_key(self) -> None:
        return None

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.SCHEMA.schema()

    @property
    def url(self) -> str:
        return self.URL + f"?dateFrom={self.date_from.isoformat()}"

    @property
    def headers(self) -> Dict:
        return {"Authorization": self.credentials["api_key"]}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        attempts_count = 0
        while attempts_count < 3:
            try:
                response = requests.get(self.url, headers=self.headers)
            except ChunkedEncodingError:
                time.sleep(60)
                continue
            if response.status_code == 200:
                if records := response.json():
                    for record in records:
                        yield self.SCHEMA(**record).dict()
                return
            elif response.status_code == 408:
                attempts_count += 1
                if attempts_count < 3:
                    time.sleep(60)  # Wildberries allows 1 request per minute
                else:
                    raise Exception(f"Failed to load data from Wildberries API after 3 attempts due 408 error")
            else:
                raise Exception(f"Status code: {response.status_code}. Body: {response.text}")


class IncomeStream(StatisticsStream):
    SCHEMA: Type[Income] = Income
    URL: str = "https://statistics-api.wildberries.ru/api/v1/supplier/incomes"


class StockStream(StatisticsStream):
    SCHEMA: Type[Stock] = Stock
    URL: str = "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"


class OrderStream(StatisticsStream):
    SCHEMA: Type[Order] = Order
    URL: str = "https://statistics-api.wildberries.ru/api/v1/supplier/orders"

    def __init__(self, credentials: WildberriesCredentials, date_from: date, strict_date_from: bool):
        super().__init__(credentials, date_from)
        self.strict_date_from = strict_date_from

    @property
    def url(self) -> str:
        url = super().url
        if self.strict_date_from:
            url += "&flag=1"
        return url


class SaleStream(OrderStream):
    SCHEMA: Type[Sale] = Sale
    URL: str = "https://statistics-api.wildberries.ru/api/v1/supplier/sales"


class ReportDetailByPeriodStream(StatisticsStream):
    SCHEMA: Type[ReportDetailByPeriod] = ReportDetailByPeriod
    URL: str = "https://statistics-api.wildberries.ru/api/v1/supplier/reportDetailByPeriod"

    def __init__(self, credentials: WildberriesCredentials, date_from: date, date_to: date):
        super().__init__(credentials, date_from)
        self.date_to = date_to

    @property
    def url(self) -> str:
        url = super().url
        url += f"&dateTo={self.date_to}"
        return url

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        rrdid = 0
        while True:
            url = self.url + f"&rrdid={rrdid}"
            try:
                response = requests.get(url, headers=self.headers)
            except ChunkedEncodingError:
                time.sleep(60)
                continue
            if response.status_code == 200:
                if records := response.json():
                    for record in records:
                        row = self.SCHEMA(**record)
                        rrdid = row.rrd_id
                        yield row.dict()
                else:
                    return
            elif response.status_code == 408:
                time.sleep(60)  # Wildberries allows 1 request per minute
            else:
                raise Exception(f"Status code: {response.status_code}. Body: {response.text}")
