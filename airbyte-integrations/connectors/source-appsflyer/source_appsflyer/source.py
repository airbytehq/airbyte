#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import logging
from abc import ABC
from datetime import date, datetime, timedelta
from decimal import Decimal
from http import HTTPStatus
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple, Union

import pendulum
import requests
from pendulum.tz.timezone import Timezone

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer

from .fields import *


# Simple transformer
def parse_date(date: Any, timezone: Timezone) -> datetime:
    if date and isinstance(date, str):
        return pendulum.parse(date).replace(tzinfo=timezone)
    return date


# Basic full refresh stream
class AppsflyerStream(HttpStream, ABC):
    primary_key = None
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
        return "https://hq1.appsflyer.com/api/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            "from": pendulum.yesterday(self.timezone).to_date_string(),
            "to": pendulum.today(self.timezone).to_date_string(),
            "timezone": self.timezone.name,
            "maximum_rows": self.maximum_rows,
        }

        if self.additional_fields:
            additional_fields = ",".join(self.additional_fields)
            params["additional_fields"] = additional_fields

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        csv_data = map(lambda x: x.decode("utf-8"), response.iter_lines())
        reader = csv.DictReader(csv_data)
        known_keys = mapper.field_map.keys()

        for record in reader:
            yield {mapper.field_map[k]: v for k, v in record.items() if k in known_keys}

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

        logging.getLogger("airbyte").log(logging.INFO, f"Rate limit exceeded. Retry in {wait_time} seconds.")
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
    additional_fields = additional_fields.raw_data

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


class EventsMixin:
    def find_events(self, header: Sequence[str]) -> List[str]:
        return [event.replace(" (Unique users)", "").strip() for event in header if " (Unique users)" in event]

    def get_records(self, row: Dict, events: List[str]) -> List[Dict]:
        identifiers = {
            "Date": "date",
            "Agency/PMD (af_prt)": "af_prt",
            "Media Source (pid)": "media_source",
            "Campaign (c)": "campaign",
            "Country": "country",
        }

        record = {identifiers[k]: v for k, v in row.items() if k in identifiers.keys()}

        for event in events:
            yield {
                **record,
                "event_name": event,
                "event_unique_users": row.get(f"{event} (Unique users)"),
                "event_counter": row.get(f"{event} (Event counter)"),
                "event_sales": row.get(f"{event} (Sales in USD)"),
            }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        csv_data = map(lambda x: x.decode("utf-8"), response.iter_lines())
        reader = csv.DictReader(csv_data)

        header = reader.fieldnames
        events = self.find_events(header)

        for row in reader:
            yield from self.get_records(row, events)


class InAppEvents(RawDataMixin, IncrementalAppsflyerStream):
    intervals = 31
    cursor_field = "event_time"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"raw-data/export/app/{self.app_id}/in_app_events_report/v5"


class OrganicInAppEvents(RawDataMixin, IncrementalAppsflyerStream):
    intervals = 31
    cursor_field = "event_time"
    additional_fields = additional_fields.organic_in_app_events

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"raw-data/export/app/{self.app_id}/organic_in_app_events_report/v5"


class UninstallEvents(RawDataMixin, IncrementalAppsflyerStream):
    cursor_field = "event_time"
    additional_fields = additional_fields.uninstall_events

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"raw-data/export/app/{self.app_id}/uninstall_events_report/v5"


class OrganicUninstallEvents(RawDataMixin, IncrementalAppsflyerStream):
    cursor_field = "event_time"
    additional_fields = additional_fields.uninstall_events

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"raw-data/export/app/{self.app_id}/organic_uninstall_events_report/v5"


class Installs(RawDataMixin, IncrementalAppsflyerStream):
    cursor_field = "install_time"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"raw-data/export/app/{self.app_id}/installs_report/v5"


class OrganicInstalls(RawDataMixin, IncrementalAppsflyerStream):
    cursor_field = "install_time"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"raw-data/export/app/{self.app_id}/organic_installs_report/v5"


class RetargetingInAppEvents(InAppEvents):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"raw-data/export/app/{self.app_id}/in-app-events-retarget/v5"


class RetargetingInstalls(Installs):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"raw-data/export/app/{self.app_id}/installs-retarget/v5"


class PartnersReport(AggregateDataMixin, IncrementalAppsflyerStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"agg-data/export/app/{self.app_id}/partners_by_date_report/v5"


class DailyReport(AggregateDataMixin, IncrementalAppsflyerStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"agg-data/export/app/{self.app_id}/daily_report/v5"


class GeoReport(AggregateDataMixin, IncrementalAppsflyerStream):
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"agg-data/export/app/{self.app_id}/geo_by_date_report/v5"


class GeoEventsReport(EventsMixin, GeoReport):
    pass


class PartnersEventsReport(EventsMixin, PartnersReport):
    pass


class RetargetingPartnersReport(RetargetingMixin, PartnersReport):
    pass


class RetargetingDailyReport(RetargetingMixin, DailyReport):
    pass


class RetargetingGeoReport(RetargetingMixin, GeoReport):
    pass


class RetargetingGeoEventsReport(EventsMixin, RetargetingGeoReport):
    pass


class RetargetingPartnersEventsReport(EventsMixin, RetargetingPartnersReport):
    pass


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
            test_url = f"https://hq1.appsflyer.com/api/agg-data/export/app/{app_id}/partners_report/v5?from={dates}&to={dates}&timezone=UTC"
            headers = {"Authorization": f"Bearer {api_token}"}
            response = requests.request("GET", url=test_url, headers=headers)

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
            logging.getLogger("airbyte").log(logging.INFO, f"Start date over 90 days, using start_date: {earliest_date}")
            return earliest_date

        return start_date

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["timezone"] = config.get("timezone", "UTC")
        timezone = pendulum.timezone(config.get("timezone", "UTC"))
        earliest_date = pendulum.today(timezone) - timedelta(days=90)
        start_date = parse_date(config.get("start_date") or pendulum.today(timezone), timezone)
        config["start_date"] = self.is_start_date_before_earliest_date(start_date, earliest_date)
        config["end_date"] = pendulum.now(timezone)
        logging.getLogger("airbyte").log(logging.INFO, f"Using start_date: {config['start_date']}, end_date: {config['end_date']}")
        auth = TokenAuthenticator(token=config["api_token"])
        return [
            InAppEvents(authenticator=auth, **config),
            OrganicInAppEvents(authenticator=auth, **config),
            RetargetingInAppEvents(authenticator=auth, **config),
            Installs(authenticator=auth, **config),
            OrganicInstalls(authenticator=auth, **config),
            RetargetingInstalls(authenticator=auth, **config),
            UninstallEvents(authenticator=auth, **config),
            OrganicUninstallEvents(authenticator=auth, **config),
            DailyReport(authenticator=auth, **config),
            RetargetingDailyReport(authenticator=auth, **config),
            PartnersReport(authenticator=auth, **config),
            RetargetingPartnersReport(authenticator=auth, **config),
            PartnersEventsReport(authenticator=auth, **config),
            RetargetingPartnersEventsReport(authenticator=auth, **config),
            GeoReport(authenticator=auth, **config),
            RetargetingGeoReport(authenticator=auth, **config),
            GeoEventsReport(authenticator=auth, **config),
            RetargetingGeoEventsReport(authenticator=auth, **config),
        ]
