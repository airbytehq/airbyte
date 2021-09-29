#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import csv
import decimal
import pendulum
import requests

from abc import ABC
from datetime import date, datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union, Callable
from operator import add
from pendulum.tz.timezone import Timezone
from pendulum.parsing.exceptions import ParserError
from http import HTTPStatus
from decimal import Decimal

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth

# Simple transformer
def parse_date(date: Any, timezone: Timezone) -> datetime:
    if date and isinstance(date, str):
        return pendulum.parse(date).replace(tzinfo=timezone)
    return date

def transform_datetime_field(record, field_name, timezone):
    value = record.get(field_name, None)
    if value is None:
        return

    record[field_name] = parse_date(record[field_name], timezone)

def transform_empty_strings_to_none(record):
    for key, value in record.items():
        if value == "":
            record[key] = None

def transform_na_to_none(record):
    for key, value in record.items():
        if value == "N/A":
            record[key] = None

def transform_boolean(record, field_name):
    value = record.get(field_name, None)
    if value is None:
        return

    if value.lower() == "TRUE".lower():
        record[field_name] = True
    else:
        record[field_name] = False

def transform_decimal(record, field_name):
    value = record.get(field_name, None)
    if value is None:
        return

    record[field_name] = Decimal(value)

# Basic full refresh stream
class AppsflyerStream(HttpStream, ABC):
    primary_key = None
    main_fields = ()
    additional_fields = ()
    maximum_rows = 1_000_000

    def __init__(
        self,
        app_id: str,
        api_token: str,
        timezone: str,
        start_date: Union[date, str] = None,
        end_date: Union[date, str] = None,
        **kwargs
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
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            "api_token": self.api_token,
            "from": pendulum.yesterday(self.timezone).to_date_string(),
            "to": pendulum.today(self.timezone).to_date_string(),
            "timezone": self.timezone.name,
            "maximum_rows": self.maximum_rows
        }

        if self.additional_fields:
            additional_fields = (",").join(self.additional_fields)
            params["additional_fields"] = additional_fields

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        fields = add(self.main_fields, self.additional_fields) if self.additional_fields else self.main_fields
        csv_data = map(lambda x: x.decode("utf-8"), response.iter_lines())
        reader = csv.DictReader(csv_data, fields)
        next(reader, {})

        yield from map(self.transform, reader)

    def is_aggregate_reports_reached_limit(self, response: requests.Response) -> bool:
        template = "Limit reached for "
        is_forbidden =  response.status_code == HTTPStatus.FORBIDDEN
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

    def transform(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        transform_empty_strings_to_none(record)
        transform_na_to_none(record)
        transform_boolean(record, "wifi")
        transform_boolean(record, "is_retargeting")
        transform_boolean(record, "is_primary_attribution")
        transform_boolean(record, "is_lat")
        transform_boolean(record, "is_receipt_validated")
        transform_boolean(record, "store_reinstall")
        transform_decimal(record, "account_login_event_counter")
        transform_decimal(record, "account_login_sales_in_idr")
        transform_decimal(record, "account_login_unique_users")
        transform_decimal(record, "af_complete_registration_event_counter")
        transform_decimal(record, "af_complete_registration_sales_in_idr")
        transform_decimal(record, "af_complete_registration_unique_users")
        transform_decimal(record, "af_purchase_registration_event_counter")
        transform_decimal(record, "af_purchase_registration_sales_in_idr")
        transform_decimal(record, "af_purchase_registration_unique_users")
        transform_decimal(record, "average_ecpi")
        transform_decimal(record, "average_revenue_per_user")
        transform_decimal(record, "checkout_success_event_counter")
        transform_decimal(record, "checkout_success_sales_in_idr")
        transform_decimal(record, "checkout_success_unique_users")
        transform_decimal(record, "click_through_rate")
        transform_decimal(record, "clicks")
        transform_decimal(record, "conversion_rate")
        transform_decimal(record, "conversions")
        transform_decimal(record, "create_product_complete_event_counter")
        transform_decimal(record, "create_product_complete_sales_in_idr")
        transform_decimal(record, "create_product_complete_unique_users")
        transform_decimal(record, "impressions")
        transform_decimal(record, "init_appsflyer_id_event_counter")
        transform_decimal(record, "init_appsflyer_id_sales_in_idr")
        transform_decimal(record, "init_appsflyer_id_unique_users")
        transform_decimal(record, "installs")
        transform_decimal(record, "loyal_users")
        transform_decimal(record, "loyal_users_rate")
        transform_decimal(record, "pay_premium_pkg_event_counter")
        transform_decimal(record, "pay_premium_pkg_sales_in_idr")
        transform_decimal(record, "pay_premium_pkg_unique_users")
        transform_decimal(record, "return_on_investment")
        transform_decimal(record, "sessions")
        transform_decimal(record, "total_cost")
        transform_decimal(record, "total_revenue")

        return record

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
            raise TypeError(f"Expected {self.cursor_field} type '{type(current_state).__name__}' but returned type '{type(latest_state).__name__}'.") from e

    def stream_slices(
        self,
        sync_mode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None
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
            dates.append({
                self.cursor_field: start_date,
                self.cursor_field + '_end': end_date
            })
            start_date += delta
        return dates

class RawDataMixin:

    main_fields = (
        "attributed_touch_type",
        "attributed_touch_time",
        "install_time",
        "event_time",
        "event_name",
        "event_value",
        "event_revenue",
        "event_revenue_currency",
        "event_revenue_usd",
        "event_source",
        "is_receipt_validated",
        "af_prt",
        "media_source",
        "af_channel",
        "af_keywords",
        "campaign",
        "af_c_id",
        "af_adset",
        "af_adset_id",
        "af_ad",
        "af_ad_id",
        "af_ad_type",
        "af_siteid",
        "af_sub_siteid",
        "af_sub1",
        "af_sub2",
        "af_sub3",
        "af_sub4",
        "af_sub5",
        "af_cost_model",
        "af_cost_value",
        "af_cost_currency",
        "contributor1_af_prt",
        "contributor1_media_source",
        "contributor1_campaign",
        "contributor1_touch_type",
        "contributor1_touch_time",
        "contributor2_af_prt",
        "contributor2_media_source",
        "contributor2_campaign",
        "contributor2_touch_type",
        "contributor2_touch_time",
        "contributor3_af_prt",
        "contributor3_media_source",
        "contributor3_campaign",
        "contributor3_touch_type",
        "contributor3_touch_time",
        "region",
        "country_code",
        "state",
        "city",
        "postal_code",
        "dma",
        "ip",
        "wifi",
        "operator",
        "carrier",
        "language",
        "appsflyer_id",
        "advertising_id",
        "idfa",
        "android_id",
        "customer_user_id",
        "imei",
        "idfv",
        "platform",
        "device_type",
        "os_version",
        "app_version",
        "sdk_version",
        "app_id",
        "app_name",
        "bundle_id",
        "is_retargeting",
        "retargeting_conversion_type",
        "af_attribution_lookback",
        "af_reengagement_window",
        "is_primary_attribution",
        "user_agent",
        "http_referrer",
        "original_url",
    )

    additional_fields = (
        "app_type",
        "custom_data",
        "network_account_id",
        "install_app_store",
        "contributor1_match_type",
        "contributor2_match_type",
        "contributor3_match_type",
        "campaign_type",
        "conversion_type",
        "match_type",
        "gp_referrer",
        "gp_click_time",
        "gp_install_begin",
        "gp_broadcast_referrer",
        "keyword_match_type",
        "keyword_id",
        "att",
        "amazon_aid",
        "device_category",
        "device_model",
        "device_download_time",
        "deeplink_url",
        "oaid",
        "is_lat",
        "store_reinstall",
        "placement",
        "mediation_network",
        "segment",
        "ad_unit",
        "monetization_network",
        "impressions",
        "blocked_reason",
        "blocked_reason_value",
        "blocked_reason_rule",
        "blocked_sub_reason",
        "rejected_reason",
        "rejected_reason_value"
    )

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["from"] = stream_slice.get(self.cursor_field).to_datetime_string()
        params["to"] = stream_slice.get(self.cursor_field + '_end').to_datetime_string()

        return params

class AggregateDataMixin:
    cursor_field = "date"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["from"] = stream_slice.get(self.cursor_field).to_date_string()
        params["to"] = stream_slice.get(self.cursor_field + '_end').to_date_string()

        return params

class RetargetingMixin:

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["reattr"] = True

        return params

class InAppEvents(RawDataMixin, IncrementalAppsflyerStream):
    intervals = 31
    cursor_field = "event_time"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "in_app_events_report/v5"

class UninstallEvents(RawDataMixin, IncrementalAppsflyerStream):
    cursor_field = "event_time"

    additional_fields = (
        "custom_data",
        "network_account_id",
        "install_app_store",
        "contributor1_match_type",
        "contributor2_match_type",
        "contributor3_match_type",
        "match_type",
        "gp_referrer",
        "gp_click_time",
        "gp_install_begin",
        "gp_broadcast_referrer",
        "keyword_match_type",
        "keyword_id",
        "amazon_aid",
        "device_category",
        "device_model",
        "device_download_time",
        "deeplink_url",
        "oaid",
        "is_lat",
        "store_reinstall",
        "placement",
        "mediation_network",
        "segment",
        "ad_unit",
        "monetization_network",
        "impressions",
        "blocked_reason",
        "blocked_reason_value",
        "blocked_reason_rule",
        "blocked_sub_reason",
        "rejected_reason",
        "rejected_reason_value"
    )

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "uninstall_events_report/v5"

class Installs(RawDataMixin, IncrementalAppsflyerStream):
    cursor_field = "install_time"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "installs_report/v5"

class RetargetingInAppEvents(RetargetingMixin,InAppEvents):
    pass

class RetargetingConversions(RetargetingMixin,Installs):
    pass

class PartnersReport(AggregateDataMixin, IncrementalAppsflyerStream):
    # This order matters
    main_fields = (
        "date",
        "af_prt",
        "media_source",
        "campaign",
        "impressions",
        "clicks",
        "click_through_rate",
        "installs",
        "conversion_rate",
        "sessions",
        "loyal_users",
        "loyal_users_rate",
        "total_revenue",
        "total_cost",
        "return_on_investment",
        "average_revenue_per_user",
        "average_ecpi",
        "account_login_unique_users",
        "account_login_event_counter",
        "account_login_sales_in_idr",
        "af_complete_registration_unique_users",
        "af_complete_registration_event_counter",
        "af_complete_registration_sales_in_idr",
        "af_purchase_registration_unique_users",
        "af_purchase_registration_event_counter",
        "af_purchase_registration_sales_in_idr",
        "checkout_success_unique_users",
        "checkout_success_event_counter",
        "checkout_success_sales_in_idr",
        "create_product_complete_unique_users",
        "create_product_complete_event_counter",
        "create_product_complete_sales_in_idr",
        "init_appsflyer_id_unique_users",
        "init_appsflyer_id_event_counter",
        "init_appsflyer_id_sales_in_idr",
        "pay_premium_pkg_unique_users",
        "pay_premium_pkg_event_counter",
        "pay_premium_pkg_sales_in_idr"
    )

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "partners_by_date_report/v5"

class DailyReport(AggregateDataMixin, IncrementalAppsflyerStream):
    # This order matters
    main_fields = (
        "date",
        "af_prt",
        "media_source",
        "campaign",
        "impressions",
        "clicks",
        "click_through_rate",
        "installs",
        "conversion_rate",
        "sessions",
        "loyal_users",
        "loyal_users_rate",
        "total_cost",
        "average_ecpi"
    )

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "daily_report/v5"

class GeoReport(AggregateDataMixin, IncrementalAppsflyerStream):
    # This order matters
    main_fields = (
        "date",
        "country_code",
        "af_prt",
        "media_source",
        "campaign",
        "impressions",
        "clicks",
        "click_through_rate",
        "installs",
        "conversion_rate",
        "sessions",
        "loyal_users",
        "loyal_users_rate",
        "total_revenue",
        "total_cost",
        "return_on_investment",
        "average_revenue_per_user",
        "average_ecpi",
        "account_login_unique_users",
        "account_login_event_counter",
        "account_login_sales_in_idr",
        "af_complete_registration_unique_users",
        "af_complete_registration_event_counter",
        "af_complete_registration_sales_in_idr",
        "af_purchase_registration_unique_users",
        "af_purchase_registration_event_counter",
        "af_purchase_registration_sales_in_idr",
        "checkout_success_unique_users",
        "checkout_success_event_counter",
        "checkout_success_sales_in_idr",
        "create_product_complete_unique_users",
        "create_product_complete_event_counter",
        "create_product_complete_sales_in_idr",
        "init_appsflyer_id_unique_users",
        "init_appsflyer_id_event_counter",
        "init_appsflyer_id_sales_in_idr",
        "pay_premium_pkg_unique_users",
        "pay_premium_pkg_event_counter",
        "pay_premium_pkg_sales_in_idr"
    )

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "geo_by_date_report/v5"

class RetargetingPartnersReport(RetargetingMixin, PartnersReport):
    # This order matters
    main_fields = (
        "date",
        "af_prt",
        "media_source",
        "campaign",
        "clicks",
        "conversions",
        "conversion_type",
        "conversion_rate",
        "sessions",
        "loyal_users",
        "loyal_users_rate",
        "total_revenue",
        "total_cost",
        "return_on_investment",
        "average_revenue_per_user",
        "average_ecpi",
        "account_login_unique_users",
        "account_login_event_counter",
        "account_login_sales_in_idr",
        "af_complete_registration_unique_users",
        "af_complete_registration_event_counter",
        "af_complete_registration_sales_in_idr",
        "checkout_success_unique_users",
        "checkout_success_event_counter",
        "checkout_success_sales_in_idr",
        "create_product_complete_unique_users",
        "create_product_complete_event_counter",
        "create_product_complete_sales_in_idr",
        "init_appsflyer_id_unique_users",
        "init_appsflyer_id_event_counter",
        "init_appsflyer_id_sales_in_idr"
    )

class RetargetingDailyReport(RetargetingMixin, DailyReport):
    # This order matters
    main_fields = (
        "date",
        "af_prt",
        "media_source",
        "campaign",
        "clicks",
        "conversions",
        "conversion_type",
        "conversion_rate",
        "sessions",
        "loyal_users",
        "loyal_users_rate",
        "total_cost",
        "average_ecpi"
    )

class RetargetingGeoReport(RetargetingMixin, GeoReport):
    # This order matters
    main_fields = (
        "date",
        "country_code",
        "af_prt",
        "media_source",
        "campaign",
        "clicks",
        "conversions",
        "conversion_type",
        "conversion_rate",
        "sessions",
        "loyal_users",
        "loyal_users_rate",
        "total_revenue",
        "total_cost",
        "return_on_investment",
        "average_revenue_per_user",
        "average_ecpi",
        "account_login_unique_users",
        "account_login_event_counter",
        "account_login_sales_in_idr",
        "af_complete_registration_unique_users",
        "af_complete_registration_event_counter",
        "af_complete_registration_sales_in_idr",
        "checkout_success_unique_users",
        "checkout_success_event_counter",
        "checkout_success_sales_in_idr",
        "create_product_complete_unique_users",
        "create_product_complete_event_counter",
        "create_product_complete_sales_in_idr",
        "init_appsflyer_id_unique_users",
        "init_appsflyer_id_event_counter",
        "init_appsflyer_id_sales_in_idr"
    )

# Source
class SourceAppsflyer(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            app_id = config["app_id"]
            api_token = config["api_token"]
            dates = pendulum.now("UTC").to_date_string()
            test_url = f"https://hq.appsflyer.com/export/{app_id}/partners_report/v5?api_token={api_token}&from={dates}&to={dates}&timezone=UTC"
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
            RetargetingGeoReport(authenticator=auth, **config)
        ]
