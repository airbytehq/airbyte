#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import csv
from abc import ABC
from datetime import date, datetime, timedelta
from decimal import Decimal
from http import HTTPStatus
from operator import add
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import pendulum
import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from pendulum.tz.timezone import Timezone

from . import fields


# Simple transformer
def parse_date(date: Any, timezone: Timezone) -> datetime:
    if date and isinstance(date, str):
        return pendulum.parse(date).replace(tzinfo=timezone)
    return date


# Basic full refresh stream
class AppsflyerStream(HttpStream, ABC):
    primary_key = None
    main_fields = ()
    additional_fields = ()
    maximum_rows = 1_000_000
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)

    def __init__(
        self, app_id: str, api_token: str, timezone: str, start_date: Union[date, str] = None, end_date: Union[date, str] = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.app_id = app_id
        self.api_token = api_token
        self.start_date = start_date
        self.end_date = end_date
        self.timezone = pendulum.timezone(timezone)

    @property
    def url_base(self) -> str:
        return f"https://hq.appsflyer.com/export/{self.app_id}/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            "api_token": self.api_token,
            "from": pendulum.yesterday(self.timezone).to_date_string(),
            "to": pendulum.today(self.timezone).to_date_string(),
            "timezone": self.timezone.name,
            "maximum_rows": self.maximum_rows,
        }

        if self.additional_fields:
            additional_fields = (",").join(self.additional_fields)
            params["additional_fields"] = additional_fields

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        fields = add(self.main_fields, self.additional_fields) if self.additional_fields else self.main_fields
        csv_data = map(lambda x: x.decode("utf-8"), response.iter_lines())
        reader = csv.DictReader(csv_data, fields)

        # Skip CSV Header
        next(reader, {})

        yield from reader

    def is_aggregate_reports_reached_limit(self, response: requests.Response) -> bool:
        template = "Limit reached for "
        is_forbidden = response.status_code == HTTPStatus.FORBIDDEN
        is_template_match = template in response.text

        return is_forbidden and is_template_match

    def is_raw_data_reports_reached_limit(self, response: requests.Response) -> bool:
        template = "Your API calls limit has been reached for report type"
        is_bad_request = response.status_code == HTTPStatus.BAD_REQUEST
        is_template_match = template in response.text

        return is_bad_request and is_template_match

    def should_retry(self, response: requests.Response) -> bool:
        is_aggregate_reports_reached_limit = self.is_aggregate_reports_reached_limit(response)
        is_raw_data_reports_reached_limit = self.is_raw_data_reports_reached_limit(response)
        is_rejected = is_aggregate_reports_reached_limit or is_raw_data_reports_reached_limit

        return is_rejected or super().should_retry(response)

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        if self.is_raw_data_reports_reached_limit(response):
            now = pendulum.now("UTC")
            midnight = pendulum.tomorrow("UTC")
            wait_time = (midnight - now).seconds
        elif self.is_aggregate_reports_reached_limit(response):
            wait_time = 60
        else:
            return super().backoff_time(response)

        AirbyteLogger().log("INFO", f"Rate limit exceded. Retry in {wait_time} seconds.")
        return wait_time

    @transformer.registerCustomTransform
    def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
        if original_value == "" or original_value == "N/A" or original_value == "NULL":
            return None
        if isinstance(original_value, float):
            return Decimal(original_value)
        return original_value


# Basic incremental stream
class IncrementalAppsflyerStream(AppsflyerStream, ABC):
    intervals = 60

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            latest_state = latest_record.get(self.cursor_field)
            current_state = current_stream_state.get(self.cursor_field) or latest_state

            if current_state:
                return {self.cursor_field: max(latest_state, current_state)}
            return {}
        except TypeError as e:
            raise TypeError(
                f"Expected {self.cursor_field} type '{type(current_state).__name__}' but returned type '{type(latest_state).__name__}'."
            ) from e

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:
        stream_state = stream_state or {}
        cursor_value = stream_state.get(self.cursor_field)
        start_date = self.get_date(parse_date(cursor_value, self.timezone), self.start_date, max)
        if self.start_date_abnormal(start_date):
            self.end_date = start_date
        return self.chunk_date_range(start_date)

    def start_date_abnormal(self, start_date: datetime) -> bool:
        return start_date >= self.end_date

    def get_date(self, cursor_value: Any, default_date: datetime, comparator: Callable[[datetime, datetime], datetime]) -> datetime:
        cursor_value = parse_date(cursor_value or default_date, self.timezone)
        date = comparator(cursor_value, default_date)
        return date

    def chunk_date_range(self, start_date: datetime) -> List[Mapping[str, any]]:
        dates = []
        delta = timedelta(days=self.intervals)
        while start_date <= self.end_date:
            end_date = self.get_date(start_date + delta, self.end_date, min)
            dates.append({self.cursor_field: start_date, self.cursor_field + "_end": end_date})
            start_date += delta
        return dates


class RawDataMixin:
    main_fields = fields.raw_data.main_fields
    additional_fields = fields.raw_data.additional_fields

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["from"] = stream_slice.get(self.cursor_field).to_datetime_string()
        params["to"] = stream_slice.get(self.cursor_field + "_end").to_datetime_string()
        # use currency set in the app settings to align with aggregate api currency.
        params["currency"] = "preferred"

        return params


class AggregateDataMixin:
    cursor_field = "date"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["from"] = stream_slice.get(self.cursor_field).to_date_string()
        params["to"] = stream_slice.get(self.cursor_field + "_end").to_date_string()

        return params


class RetargetingMixin:
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["reattr"] = True

        return params


class InAppEvents(RawDataMixin, IncrementalAppsflyerStream):
    intervals = 31
    cursor_field = "event_time"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "in_app_events_report/v5"


class UninstallEvents(RawDataMixin, IncrementalAppsflyerStream):
    cursor_field = "event_time"
    additional_fields = fields.uninstall_events.additional_fields

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "uninstall_events_report/v5"


class Installs(RawDataMixin, IncrementalAppsflyerStream):
    cursor_field = "install_time"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "installs_report/v5"


class RetargetingInAppEvents(RetargetingMixin, InAppEvents):
    pass


class RetargetingConversions(RetargetingMixin, Installs):
    pass


class PartnersReport(AggregateDataMixin, IncrementalAppsflyerStream):
    main_fields = fields.partners_report.main_fields

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "partners_by_date_report/v5"


class DailyReport(AggregateDataMixin, IncrementalAppsflyerStream):
    main_fields = fields.daily_report.main_fields

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "daily_report/v5"


class GeoReport(AggregateDataMixin, IncrementalAppsflyerStream):
    main_fields = fields.geo_report.main_fields

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "geo_by_date_report/v5"


class RetargetingPartnersReport(RetargetingMixin, PartnersReport):
    main_fields = fields.retargeting_partners_report.main_fields


class RetargetingDailyReport(RetargetingMixin, DailyReport):
    main_fields = fields.retargeting_daily_report.main_fields


class RetargetingGeoReport(RetargetingMixin, GeoReport):
    main_fields = fields.retargeting_geo_report.main_fields


# Source
class SourceAppsflyer(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            timezone = config.get("timezone", "UTC")
            if timezone not in pendulum.timezones:
                return False, "The supplied timezone is invalid."
            app_id = config["app_id"]
            api_token = config["api_token"]
            dates = pendulum.now("UTC").to_date_string()
            test_url = (
                f"https://hq.appsflyer.com/export/{app_id}/partners_report/v5?api_token={api_token}&from={dates}&to={dates}&timezone=UTC"
            )
            response = requests.request("GET", url=test_url)

            if response.status_code != 200:
                error_message = "The supplied APP ID is invalid" if response.status_code == 404 else response.text.rstrip("\n")
                if error_message:
                    return False, error_message
                response.raise_for_status()
        except Exception as e:
            return False, e

        return True, None

    def is_start_date_before_earliest_date(self, start_date, earliest_date):
        if start_date <= earliest_date:
            AirbyteLogger().log("INFO", f"Start date over 90 days, using start_date: {earliest_date}")
            return earliest_date

        return start_date

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["timezone"] = config.get("timezone", "UTC")
        timezone = pendulum.timezone(config.get("timezone", "UTC"))
        earliest_date = pendulum.today(timezone) - timedelta(days=90)
        start_date = parse_date(config.get("start_date") or pendulum.today(timezone), timezone)
        config["start_date"] = self.is_start_date_before_earliest_date(start_date, earliest_date)
        config["end_date"] = pendulum.now(timezone)
        AirbyteLogger().log("INFO", f"Using start_date: {config['start_date']}, end_date: {config['end_date']}")
        auth = NoAuth()
        return [
            InAppEvents(authenticator=auth, **config),
            Installs(authenticator=auth, **config),
            UninstallEvents(authenticator=auth, **config),
            RetargetingInAppEvents(authenticator=auth, **config),
            RetargetingConversions(authenticator=auth, **config),
            PartnersReport(authenticator=auth, **config),
            DailyReport(authenticator=auth, **config),
            GeoReport(authenticator=auth, **config),
            RetargetingPartnersReport(authenticator=auth, **config),
            RetargetingDailyReport(authenticator=auth, **config),
            RetargetingGeoReport(authenticator=auth, **config),
        ]
