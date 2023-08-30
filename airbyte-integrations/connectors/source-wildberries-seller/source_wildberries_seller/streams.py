import time
from abc import ABC
from datetime import date, datetime, timedelta
from typing import Type, Mapping, Any, Dict, List, Literal, Iterable, Optional

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from requests.exceptions import ChunkedEncodingError

from source_wildberries_seller.schemas.nm_report_detail import DetailNmReport, DetailNmReportResponse
from source_wildberries_seller.schemas.nm_report_detail_history import DetailHistoryNmReport, DetailHistoryNmReportResponse
from source_wildberries_seller.schemas.nm_report_grouped import GroupedNmReport, GroupedNmReportResponse
from source_wildberries_seller.schemas.nm_report_grouped_history import GroupedHistoryNmReport, GroupedHistoryNmReportResponse
from source_wildberries_seller.types import SchemaT, WildberriesCredentials, IsSuccess, Message


def check_content_analytics_stream_connection(credentials: WildberriesCredentials) -> tuple[IsSuccess, Optional[Message]]:
    try:
        response = requests.post(
            url="https://suppliers-api.wildberries.ru/content/v1/analytics/nm-report/detail",
            json={
                "period": {
                    "begin": datetime.fromordinal((date.today() - timedelta(days=2)).toordinal()).strftime("%Y-%m-%d %H:%M:%S"),
                    "end": datetime.fromordinal((date.today() - timedelta(days=1)).toordinal()).strftime("%Y-%m-%d %H:%M:%S"),
                },
                "page": 1,
            },
            headers={"Authorization": credentials["api_key"]},
        )
        if response.status_code == 200:
            return True, None
        elif response.status_code == 401:
            return False, f"Invalid content_analytics API key. Response status code: {response.status_code}. Body: {response.text}"
        else:
            return False, f"Response status code: {response.status_code}. Body: {response.text}"
    except Exception as e:
        return False, str(e)


class ContentAnalyticsStream(Stream, ABC):
    SCHEMA: Type[SchemaT] = NotImplemented
    RESPONSE_SCHEMA: Type[SchemaT] = NotImplemented
    URL: str = NotImplemented

    def __init__(self, credentials: WildberriesCredentials, date_from: date, date_to: date):
        self.credentials = credentials
        self.date_from = date_from
        self.date_to = date_to

    @property
    def primary_key(self) -> None:
        return None

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.SCHEMA.schema()

    @property
    def headers(self) -> Dict:
        return {"Authorization": self.credentials["api_key"]}

    @property
    def period_dates(self) -> Dict:
        return {
            "period": {
                "begin": datetime.fromordinal(self.date_from.toordinal()).strftime("%Y-%m-%d %H:%M:%S"),
                "end": datetime.fromordinal(self.date_to.toordinal()).strftime("%Y-%m-%d %H:%M:%S"),
            }
        }


class NmReportStream(ContentAnalyticsStream, ABC):
    def get_request_body(self, page: int) -> Dict:
        raise NotImplementedError

    def _read_records(self, rows_attr: str) -> Iterable[Mapping[str, Any]]:
        page = 1
        while True:
            try:
                response = requests.post(url=self.URL, json=self.get_request_body(page), headers=self.headers)
            except ChunkedEncodingError:
                time.sleep(60)
                continue

            if response.status_code != 200:
                raise Exception(f"Status code: {response.status_code}. Body: {response.text}")

            response_data = self.RESPONSE_SCHEMA(**response.json())
            if response_data.error:
                raise Exception(f"Error: {response_data.errorText}. Additional errors: {response_data.additionalErrors}")

            for row in getattr(response_data.data, rows_attr):
                yield row.dict()

            if response_data.data.isNextPage:
                page += 1
                continue

            return


class DetailNmReportStream(NmReportStream):
    SCHEMA: Type[DetailNmReport] = DetailNmReport
    RESPONSE_SCHEMA: Type[DetailNmReportResponse] = DetailNmReportResponse
    URL: str = "https://suppliers-api.wildberries.ru/content/v1/analytics/nm-report/detail"

    def __init__(
        self,
        credentials: WildberriesCredentials,
        date_from: date,
        date_to: date,
        brand_names: List[str],
        object_ids: List[int],
        tag_ids: List[int],
        nm_ids: List[int],
        timezone: str,
    ):
        super().__init__(credentials, date_from, date_to)
        self.brand_names = brand_names
        self.object_ids = object_ids
        self.tag_ids = tag_ids
        self.nm_ids = nm_ids
        self.timezone = timezone

    def get_request_body(self, page: int) -> Dict:
        body = self.period_dates
        body["page"] = page
        if self.brand_names:
            body["brandNames"] = self.brand_names
        if self.object_ids:
            body["objectIDs"] = self.object_ids
        if self.tag_ids:
            body["tagIDs"] = self.tag_ids
        if self.nm_ids:
            body["nmIDs"] = self.nm_ids
        if self.timezone:
            body["timezone"] = self.timezone
        return body

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        yield from self._read_records(rows_attr="cards")


class GroupedNmReportStream(NmReportStream):
    SCHEMA: Type[GroupedNmReport] = GroupedNmReport
    RESPONSE_SCHEMA: Type[GroupedNmReportResponse] = GroupedNmReportResponse
    URL: str = "https://suppliers-api.wildberries.ru/content/v1/analytics/nm-report/grouped"

    def __init__(
        self,
        credentials: WildberriesCredentials,
        date_from: date,
        date_to: date,
        object_ids: List[int],
        brand_names: List[str],
        tag_ids: List[int],
        timezone: str,
    ):
        super().__init__(credentials, date_from, date_to)
        self.brand_names = brand_names
        self.object_ids = object_ids
        self.tag_ids = tag_ids
        self.timezone = timezone

    def get_request_body(self, page: int) -> Dict:
        body = self.period_dates
        body["page"] = page
        if self.object_ids:
            body["objectIDs"] = self.object_ids
        if self.brand_names:
            body["brandNames"] = self.brand_names
        if self.tag_ids:
            body["tagIDs"] = self.tag_ids
        if self.timezone:
            body["timezone"] = self.timezone
        return body

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        yield from self._read_records(rows_attr="groups")


class HistoryNmReportStream(ContentAnalyticsStream, ABC):
    @property
    def period_dates(self) -> Dict:
        return {"period": {"begin": self.date_from.isoformat(), "end": self.date_to.isoformat()}}

    def get_request_body(self) -> Dict:
        raise NotImplementedError

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        while True:
            try:
                response = requests.post(url=self.URL, json=self.get_request_body(), headers=self.headers)
            except ChunkedEncodingError:
                time.sleep(60)
                continue

            if response.status_code != 200:
                raise Exception(f"Status code: {response.status_code}. Body: {response.text}")

            response_data = self.RESPONSE_SCHEMA(**response.json())
            if response_data.error:
                raise Exception(f"Error: {response_data.errorText}. Additional errors: {response_data.additionalErrors}")

            for row in response_data.data:
                yield row.dict()

            return


class DetailHistoryNmReportStream(HistoryNmReportStream):
    SCHEMA: Type[DetailHistoryNmReport] = DetailHistoryNmReport
    RESPONSE_SCHEMA: Type[DetailHistoryNmReportResponse] = DetailHistoryNmReportResponse
    URL: str = "https://suppliers-api.wildberries.ru/content/v1/analytics/nm-report/detail/history"

    def __init__(
        self,
        credentials: WildberriesCredentials,
        date_from: date,
        date_to: date,
        nm_ids: List[int],
        timezone: str,
        aggregation_level: Literal["day", "week", "month"],
    ):
        super().__init__(credentials, date_from, date_to)
        self.nm_ids = nm_ids
        self.timezone = timezone
        self.aggregation_level = aggregation_level

    def get_request_body(self) -> Dict:
        body = self.period_dates
        body["nmIDs"] = self.nm_ids
        if self.timezone:
            body["timezone"] = self.timezone
        if self.aggregation_level:
            body["aggregationLevel"] = self.aggregation_level
        return body


class GroupedHistoryNmReportStream(HistoryNmReportStream):
    SCHEMA: Type[GroupedHistoryNmReport] = GroupedHistoryNmReport
    RESPONSE_SCHEMA: Type[GroupedHistoryNmReportResponse] = GroupedHistoryNmReportResponse
    URL: str = "https://suppliers-api.wildberries.ru/content/v1/analytics/nm-report/grouped/history"

    def __init__(
        self,
        credentials: WildberriesCredentials,
        date_from: date,
        date_to: date,
        object_ids: List[int],
        brand_names: List[str],
        tag_ids: List[int],
        timezone: str,
        aggregation_level: Literal["day", "week", "month"],
    ):
        super().__init__(credentials, date_from, date_to)
        self.brand_names = brand_names
        self.object_ids = object_ids
        self.tag_ids = tag_ids
        self.timezone = timezone
        self.aggregation_level = aggregation_level

    def get_request_body(self) -> Dict:
        body = self.period_dates
        if self.object_ids:
            body["objectIDs"] = self.object_ids
        if self.brand_names:
            body["brandNames"] = self.brand_names
        if self.tag_ids:
            body["tagIDs"] = self.tag_ids
        if self.timezone:
            body["timezone"] = self.timezone
        if self.aggregation_level:
            body["aggregationLevel"] = self.aggregation_level
        return body
