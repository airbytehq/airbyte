#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import csv
from abc import ABC
from datetime import datetime, timedelta
from decimal import Decimal
from http import HTTPStatus
import logging
from operator import add
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Tuple,
)

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
    transformer: TypeTransformer = TypeTransformer(
        TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)
    slices_by_date: bool = False

    def __init__(
        self,
        app_id: str,
        api_token_v1: str,
        backward_dates_campatibility_mode: bool,
        timezone: str,
        chunked_reports_config: Mapping[str, Any] = {
            "split_mode_type": "do_not_split_mode"},
        api_token_v2: Optional[str] = None,
        start_date: Optional[pendulum.DateTime] = None,
        end_date: Optional[pendulum.DateTime] = None,
        client_name: Optional[str] = "",
        product_name: Optional[str] = "",
        custom_constants: Optional[Mapping[str, str]] = {},
        *args,
        **kwargs,
    ):
        super().__init__()
        self.app_id = app_id
        self.api_token_v1 = api_token_v1
        self.api_token_v2 = api_token_v2
        self.backward_dates_campatibility_mode = backward_dates_campatibility_mode
        self.start_date = start_date
        self.end_date = end_date
        self.timezone = pendulum.timezone(timezone)
        self.chunked_reports_config = chunked_reports_config
        self.client_name = client_name
        self.product_name = product_name
        self.custom_constants = custom_constants
        self.additional_args = args
        self.additional_kwargs = kwargs

    @property
    def url_base(self) -> str:
        return f"https://hq.appsflyer.com/export/{self.app_id}/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_kwargs(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> Mapping[str, Any]:
        return {"stream": True}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            "api_token": self.api_token_v1,
            "from": pendulum.yesterday(self.timezone).to_datetime_string(),
            "to": pendulum.today(self.timezone).to_datetime_string(),
            "timezone": self.timezone.name,
            "maximum_rows": self.maximum_rows,
        }

        if self.additional_fields:
            additional_fields = (",").join(self.additional_fields)
            params["additional_fields"] = additional_fields
            print("self.name", self.name,
                  "self.additional_fields", self.additional_fields)

        return params

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = super().get_json_schema()
        extra_properties = ["__productName", "__clientName"]
        custom_keys = self.custom_constants.keys()
        extra_properties.extend(custom_keys)
        for key in extra_properties:
            schema["properties"][key] = {"type": ["null", "string"]}
        return schema

    def add_constants_to_record(self, record: Dict[str, Any]):
        constants = {
            "__productName": self.product_name,
            "__clientName": self.client_name,
        }
        constants.update(self.custom_constants)
        record.update(constants)
        return record

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        user_additional_fields = self.additional_kwargs.get(
            self.stream_spec_additional_fields_property_name())
        additional_fields = list(
            self.additional_fields if self.additional_fields else [])
        if isinstance(user_additional_fields, list):
            additional_fields = user_additional_fields
        fields = add(list(self.main_fields), additional_fields)
        csv_data = map(lambda x: x.decode("utf-8"), response.iter_lines())
        reader = csv.DictReader(csv_data, fields)
        next(reader, {})

        # Skip CSV Header
        safed_reader_entries = map(self.safe_none_field, reader)
        for record in safed_reader_entries:
            yield self.add_constants_to_record(record)

    def safe_none_field(self, entry):
        if None in entry.keys():
            entry["additional_fields"] = entry[None]
            del entry[None]
        return entry

    def is_aggregate_reports_reached_limit(self, response: requests.Response) -> bool:
        if response.status_code == HTTPStatus.FORBIDDEN:
            template = "Limit reached for "
            return template in response.text
        return False

    def is_raw_data_reports_reached_limit(self, response: requests.Response) -> bool:
        if response.status_code == HTTPStatus.BAD_REQUEST:
            template = "Your API calls limit has been reached for report type"
            return template in response.text

        return False

    def should_retry(self, response: requests.Response) -> bool:
        is_aggregate_reports_reached_limit = self.is_aggregate_reports_reached_limit(
            response)
        is_raw_data_reports_reached_limit = self.is_raw_data_reports_reached_limit(
            response)
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

        AirbyteLogger().log(
            "INFO", f"Rate limit exceded. Retry in {wait_time} seconds.")
        return wait_time

    @transformer.registerCustomTransform
    def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
        if original_value == "" or original_value == "N/A" or original_value == "NULL":
            return None
        if isinstance(original_value, float):
            return Decimal(original_value)
        return original_value

    def chunk_date_range_by_hours(
        self, start_date: pendulum.DateTime, end_date: pendulum.DateTime, delta_hours: int = 4
    ) -> List[Mapping[str, pendulum.DateTime]]:
        cursor = start_date
        while cursor < end_date:
            chunk_start = cursor
            chunk_end = cursor.add(hours=delta_hours)
            if chunk_end > end_date:
                chunk_end = end_date
            yield {
                self.cursor_field: chunk_start,
                self.cursor_field + "_end": chunk_end,
            }
            cursor = cursor.add(hours=delta_hours)

    def chunk_date_range_by_days(
        self, start_date: pendulum.DateTime, end_date: pendulum.DateTime
    ) -> List[Mapping[str, pendulum.DateTime]]:
        cursor = start_date
        while cursor < end_date:
            yield {self.cursor_field: cursor, self.cursor_field + "_end": cursor}
            cursor = cursor.add(days=1)

    @classmethod
    def stream_spec_additional_fields_property_name(cls) -> str:
        return cls.__name__.lower() + "_additional_fields"

    def stream_slices(self, *args, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        if self.chunked_reports_config['split_mode_type'] == 'do_not_split_mode':
            slices = [{self.cursor_field: self.start_date,
                       f"{self.cursor_field}_end": self.end_date}]
        elif self.chunked_reports_config['split_mode_type'] == 'split_date_mode':
            if self.slices_by_date:
                if self.chunked_reports_config['unit'] == 'Days':
                    delta_hours = 24 * int(
                        self.chunked_reports_config['split_range_units_count']
                    )
                    slices = self.chunk_date_range_by_hours(
                        start_date=self.start_date,
                        end_date=self.end_date,
                        delta_hours=delta_hours
                    )
                else:
                    slices = self.chunk_date_range_by_days(
                        self.start_date,
                        self.end_date
                    )
            else:
                if self.chunked_reports_config['unit'] == 'Hours':
                    delta_hours = int(
                        self.chunked_reports_config['split_range_units_count'])
                elif self.chunked_reports_config['unit'] == 'Days':
                    delta_hours = 24 * \
                        int(self.chunked_reports_config['split_range_units_count'])
                else:
                    raise Exception(
                        f'Invalid split date range unit: \'{self.chunked_reports_config["unit"]}\'')
                slices = self.chunk_date_range_by_hours(
                    start_date=self.start_date,
                    end_date=self.end_date,
                    delta_hours=delta_hours
                )
        else:
            raise Exception(
                'Invalid split date range split_mode_type: '
                f'\'{self.chunked_reports_config["split_mode_type"]}\''
            )

        slices = list(slices)
        print(slices)
        yield from slices


# Basic incremental stream
class IncrementalAppsflyerStream(AppsflyerStream, ABC):
    intervals = 60

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        try:
            latest_state = latest_record.get(self.cursor_field)
            current_state = current_stream_state.get(
                self.cursor_field) or latest_state

            if current_state:
                return {self.cursor_field: max(latest_state, current_state)}
            return {}
        except TypeError as e:
            raise TypeError(
                f"Expected {self.cursor_field} type '{type(current_state).__name__}' but returned type '{type(latest_state).__name__}'."
            ) from e

    def stream_slices(
        self,
        sync_mode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[Mapping[str, any]]]:
        if not self.backward_dates_campatibility_mode:
            yield from super().stream_slices()

        stream_state = stream_state or {}
        cursor_value = stream_state.get(self.cursor_field)
        start_date = self.get_date(parse_date(
            cursor_value, self.timezone), self.start_date, max)
        if self.start_date_abnormal(start_date):
            self.end_date = start_date
        slices = self.chunk_date_range(start_date)
        print('slices', slices)
        return slices

    def start_date_abnormal(self, start_date: datetime) -> bool:
        return start_date >= self.end_date

    def get_date(
        self,
        cursor_value: Any,
        default_date: datetime,
        comparator: Callable[[datetime, datetime], datetime],
    ) -> datetime:
        cursor_value = parse_date(cursor_value or default_date, self.timezone)
        date = comparator(cursor_value, default_date)
        return date

    def chunk_date_range(self, start_date: datetime) -> List[Mapping[str, any]]:
        dates = []
        delta = timedelta(days=self.intervals)
        while start_date <= self.end_date:
            end_date = self.get_date(start_date + delta, self.end_date, min)
            dates.append({self.cursor_field: start_date,
                         self.cursor_field + "_end": end_date})
            start_date += delta
        return dates


class RawDataMixin:
    main_fields = fields.raw_data.main_fields
    additional_fields = fields.raw_data.additional_fields

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["from"] = stream_slice.get(
            self.cursor_field).to_datetime_string()
        params["to"] = stream_slice.get(
            self.cursor_field + "_end").to_datetime_string()
        user_additional_fields = self.additional_kwargs[self.stream_spec_additional_fields_property_name(
        )]
        if user_additional_fields:
            params["additional_fields"] = ",".join(user_additional_fields)
        else:
            try:
                del params["additional_fields"]
            except:
                pass
        # use currency set in the app settings to align with aggregate api currency.
        params["currency"] = "preferred"

        return params

    def get_json_schema(self) -> Mapping[str, Any]:
        schema = super().get_json_schema()
        user_additional_fields = self.additional_kwargs[self.stream_spec_additional_fields_property_name(
        )]
        for default_additional_field in self.additional_fields:
            if default_additional_field not in user_additional_fields:
                del schema["properties"][default_additional_field]
        return schema


class AggregateDataMixin:
    cursor_field = "date"
    slices_by_date = True

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["from"] = stream_slice.get(self.cursor_field).to_date_string()
        params["to"] = stream_slice.get(
            self.cursor_field + "_end").to_date_string()

        return params


class RetargetingMixin:
    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["reattr"] = True

        return params


class InAppEvents(RawDataMixin, IncrementalAppsflyerStream):
    intervals = 31
    cursor_field = "event_time"

    def __init__(self, in_app_events_event_name_filter: Optional[str] = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.in_app_events_event_name_filter = in_app_events_event_name_filter

    def request_params(self, *args, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(*args, **kwargs)
        if self.in_app_events_event_name_filter:
            params["event_name"] = self.in_app_events_event_name_filter
        return params

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "in_app_events_report/v5"


class UninstallEvents(RawDataMixin, IncrementalAppsflyerStream):
    cursor_field = "event_time"
    additional_fields = fields.uninstall_events.additional_fields

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "uninstall_events_report/v5"


class Installs(RawDataMixin, IncrementalAppsflyerStream):
    cursor_field = "install_time"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "installs_report/v5"


class RetargetingInAppEvents(RetargetingMixin, InAppEvents):
    pass


class RetargetingConversions(RetargetingMixin, Installs):
    pass


class PartnersReport(AggregateDataMixin, IncrementalAppsflyerStream):
    main_fields = fields.partners_report.main_fields

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "partners_by_date_report/v5"


class DailyReport(AggregateDataMixin, IncrementalAppsflyerStream):
    main_fields = fields.daily_report.main_fields

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "daily_report/v5"


class GeoReport(AggregateDataMixin, IncrementalAppsflyerStream):
    main_fields = fields.geo_report.main_fields

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "geo_by_date_report/v5"


class RetargetingPartnersReport(RetargetingMixin, PartnersReport):
    main_fields = fields.retargeting_partners_report.main_fields


class RetargetingDailyReport(RetargetingMixin, DailyReport):
    main_fields = fields.retargeting_daily_report.main_fields


class RetargetingGeoReport(RetargetingMixin, GeoReport):
    main_fields = fields.retargeting_geo_report.main_fields


class CohortsReport(AggregateDataMixin, IncrementalAppsflyerStream):
    # cursor_field = "date"

    @property
    def url_base(self) -> str:
        return f"https://hq1.appsflyer.com/api/{self.app_id}"

    def path(self, *args, **kwargs) -> str:
        return f"cohorts/v1/data/app/{self.app_id}"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            "format": "json",
        }
        return params

    def request_body_json(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Optional[Mapping]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update(
            {
                "cohort_type": "user_acquisition",
                "timezone": self.timezone.name,
                "maximum_rows": self.maximum_rows,
                "aggregation_type": "on_day",
                "groupings": [
                    "af_ad",
                    "af_ad_id",
                    "c",
                    "af_c_id",
                    "af_channel",
                    "pid",
                    "date",
                ],
                "kpis": ["event_name"],
            }
        )
        return params

    def request_headers(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_token_v2}",
        }

    @property
    def http_method(self) -> str:
        return "POST"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from map(response.json()["results"], self.add_constants_to_record)


# Source
class SourceAppsflyer(AbstractSource):
    raw_data_streams_classes: list[IncrementalAppsflyerStream] = [
        Installs,
        InAppEvents,
        UninstallEvents,
        RetargetingInAppEvents,
        RetargetingConversions,
    ]

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            timezone = config.get("timezone", "UTC")
            if timezone not in pendulum.timezones:
                return False, "The supplied timezone is invalid."
            app_id = config["app_id"]
            api_token = config["api_token_v1"]
            dates = pendulum.now("UTC").to_date_string()
            test_url = (
                f"https://hq.appsflyer.com/export/{app_id}/partners_report/v5?api_token={api_token}&from={dates}&to={dates}&timezone=UTC"
            )
            response = requests.get(test_url)

            if response.status_code != 200:
                error_message = "The supplied APP ID is invalid" if response.status_code == 404 else response.text.rstrip(
                    "\n")
                if error_message:
                    return False, error_message
                response.raise_for_status()
        except Exception as e:
            return False, e

        return True, None

    def spec(self, logger: logging.Logger):
        spec = super().spec(logger)
        properties: Dict[str, Any] = spec.connectionSpecification["properties"]
        for property_order, raw_data_stream in enumerate(self.raw_data_streams_classes, len(properties)):
            properties.update(
                {
                    raw_data_stream.stream_spec_additional_fields_property_name(): {
                        "title": f"{raw_data_stream.__name__} Additional Fields",
                        "description": f"Comma-separated additional fields names that will be included "
                        f"in {raw_data_stream.__name__} stream schema. Leave empty if you"
                        f" don't want to load additional {raw_data_stream.__name__} fields. Fields order matters!"
                        f" Available additional fields: {', '.join(fields.raw_data.additional_fields)}",
                        "type": "string",
                        "pattern": "^$|^(\\w+,?)+\\w+$",
                        "examples": ["field1,field2,field3"],
                        "default": ",".join(fields.raw_data.additional_fields),
                        "order": property_order,
                    }
                }
            )
        return spec

    def transform_config_dates(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        config["timezone"] = config.get("timezone", "UTC")
        timezone = pendulum.timezone(config["timezone"])
        config["backward_dates_campatibility_mode"] = False
        now_date = pendulum.now().replace(tzinfo=timezone)

        if config.get("start_date") and config.get("end_date"):
            config["start_date"] = pendulum.parse(
                config["start_date"]).replace(tzinfo=timezone)
            config["end_date"] = pendulum.parse(
                config["end_date"]).replace(tzinfo=timezone)
        elif config.get("start_date") and not config.get("end_date"):
            config["backward_dates_campatibility_mode"] = True
            config["start_date"] = pendulum.parse(
                config["start_date"]).replace(tzinfo=timezone)
            config["end_date"] = now_date
        elif config.get("last_days"):
            config["start_date"] = (
                pendulum.now().subtract(days=config["last_days"]).replace(
                    tzinfo=timezone, hour=0, minute=0, second=0, microsecond=0)
            )
            config["end_date"] = now_date.replace(
                hour=0, minute=0, second=0, microsecond=0)
        elif not config.get("start_date") and not config.get("end_date") and not config.get("last_days"):
            config["start_date"] = pendulum.now().subtract(
                days=5).replace(tzinfo=timezone)
            config["end_date"] = now_date
        else:
            raise Exception("Invalid dates format or options")

        return config

    def transform_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        config = self.transform_config_dates(config)
        for raw_data_stream_class in self.raw_data_streams_classes:
            af_property_name = raw_data_stream_class.stream_spec_additional_fields_property_name()
            if config.get(af_property_name):
                config[af_property_name] = config[af_property_name].split(",")
            else:
                config[af_property_name] = []
        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.transform_config(config)
        AirbyteLogger().log(
            "INFO",
            f"Using start_date: {config['start_date']}, end_date: {config['end_date']}",
        )
        streams: Stream = [
            InAppEvents(**config),
            Installs(**config),
            UninstallEvents(**config),
            RetargetingInAppEvents(**config),
            RetargetingConversions(**config),
            PartnersReport(**config),
            DailyReport(**config),
            GeoReport(**config),
            RetargetingPartnersReport(**config),
            RetargetingDailyReport(**config),
            RetargetingGeoReport(**config),
        ]
        if config.get("api_token_v2"):
            streams.append(CohortsReport(**config))

        return streams
