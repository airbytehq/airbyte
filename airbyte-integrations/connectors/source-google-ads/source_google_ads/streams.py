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

import re
from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import pendulum
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader
from google.ads.googleads.v8.services.services.google_ads_service.pagers import SearchPager

from .google_ads import GoogleAds


def chunk_date_range(start_date: str, conversion_window: int, field: str, end_date: str = None) -> Iterable[Mapping[str, any]]:
    """
    Passing optional parameter end_date for testing
    Returns a list of the beginning and ending timetsamps of each month between the start date and now.
    The return value is a list of dicts {'date': str} which can be used directly with the Slack API
    """
    intervals = []
    end_date = pendulum.parse(end_date) if end_date else pendulum.now()
    start_date = pendulum.parse(start_date)

    # As in to return some state when state in abnormal
    if start_date > end_date:
        return [{field: start_date.to_date_string()}]

    # applying conversion window
    start_date = start_date.subtract(days=conversion_window)

    # Each stream_slice contains the beginning and ending timestamp for a 24 hour period
    while start_date < end_date:
        intervals.append({field: start_date.to_date_string()})
        start_date = start_date.add(months=1)

    return intervals


class GoogleAdsStream(Stream, ABC):
    def __init__(self, api: GoogleAds):
        self.google_ads_client = api

    def get_query(self, stream_slice: Mapping[str, Any]) -> str:
        query = GoogleAds.convert_schema_into_query(schema=self.get_json_schema(), report_name=self.name)
        return query

    def parse_response(self, response: SearchPager) -> Iterable[Mapping]:
        for result in response:
            yield self.google_ads_client.parse_single_result(self.get_json_schema(), result)

    def read_records(self, sync_mode, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        response = self.google_ads_client.send_request(self.get_query(stream_slice))
        yield from self.parse_response(response)


class IncrementalGoogleAdsStream(GoogleAdsStream, ABC):
    cursor_field = "segments.date"
    primary_key = None

    def __init__(self, start_date: str, conversion_window_days: int, **kwargs):
        self.conversion_window_days = conversion_window_days
        self._start_date = start_date
        super().__init__(**kwargs)

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        stream_state = stream_state or {}
        start_date = stream_state.get(self.cursor_field) or self._start_date

        return chunk_date_range(start_date=start_date, conversion_window=self.conversion_window_days, field=self.cursor_field)

    @staticmethod
    def get_date_params(stream_slice: Mapping[str, Any], cursor_field: str, end_date: pendulum.datetime = None):
        end_date = end_date or pendulum.yesterday()
        start_date = pendulum.parse(stream_slice.get(cursor_field))
        if start_date > pendulum.now():
            return start_date.to_date_string(), start_date.add(days=1).to_date_string()

        end_date = min(end_date, pendulum.parse(stream_slice.get(cursor_field)).add(months=1))

        # Fix issue #4806, start date should always be lower than end date.
        if start_date.add(days=1).date() >= end_date.date():
            return start_date.add(days=1).to_date_string(), start_date.add(days=2).to_date_string()
        return start_date.add(days=1).to_date_string(), end_date.to_date_string()

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}

        # When state is none return date from latest record
        if current_stream_state.get(self.cursor_field) is None:
            current_stream_state[self.cursor_field] = latest_record[self.cursor_field]

            return current_stream_state

        date_in_current_stream = pendulum.parse(current_stream_state.get(self.cursor_field))
        date_in_latest_record = pendulum.parse(latest_record[self.cursor_field])

        current_stream_state[self.cursor_field] = (max(date_in_current_stream, date_in_latest_record)).to_date_string()

        return current_stream_state

    def get_query(self, stream_slice: Mapping[str, Any] = None) -> str:
        start_date, end_date = self.get_date_params(stream_slice, self.cursor_field)
        query = GoogleAds.convert_schema_into_query(
            schema=self.get_json_schema(), report_name=self.name, from_date=start_date, to_date=end_date, cursor_field=self.cursor_field
        )
        return query


class Accounts(GoogleAdsStream):
    """
    Accounts stream: https://developers.google.com/google-ads/api/fields/v8/customer
    """

    primary_key = "customer.id"


class Campaigns(GoogleAdsStream):
    """
    Campaigns stream: https://developers.google.com/google-ads/api/fields/v8/campaign
    """

    primary_key = "campaign.id"


class AdGroups(GoogleAdsStream):
    """
    AdGroups stream: https://developers.google.com/google-ads/api/fields/v8/ad_group
    """

    primary_key = "ad_group.id"


class AdGroupAds(GoogleAdsStream):
    """
    AdGroups stream: https://developers.google.com/google-ads/api/fields/v8/ad_group_ad
    """

    primary_key = "ad_group_ad.ad.id"


class AccountPerformanceReport(IncrementalGoogleAdsStream):
    """
    AccountPerformanceReport stream: https://developers.google.com/google-ads/api/fields/v8/customer
    Google Ads API field mapping: https://developers.google.com/google-ads/api/docs/migration/mapping#account_performance
    """


class AdGroupAdReport(IncrementalGoogleAdsStream):
    """
    AdGroupAdReport stream: https://developers.google.com/google-ads/api/fields/v8/ad_group_ad
    Google Ads API field mapping: https://developers.google.com/google-ads/api/docs/migration/mapping#ad_performance
    """


class DisplayKeywordPerformanceReport(IncrementalGoogleAdsStream):
    """
    DisplayKeywordPerformanceReport stream: https://developers.google.com/google-ads/api/fields/v8/display_keyword_view
    Google Ads API field mapping: https://developers.google.com/google-ads/api/docs/migration/mapping#display_keyword_performance
    """


class DisplayTopicsPerformanceReport(IncrementalGoogleAdsStream):
    """
    DisplayTopicsPerformanceReport stream: https://developers.google.com/google-ads/api/fields/v8/topic_view
    Google Ads API field mapping: https://developers.google.com/google-ads/api/docs/migration/mapping#display_topics_performance
    """


class ShoppingPerformanceReport(IncrementalGoogleAdsStream):
    """
    ShoppingPerformanceReport stream: https://developers.google.com/google-ads/api/fields/v8/shopping_performance_view
    Google Ads API field mapping: https://developers.google.com/google-ads/api/docs/migration/mapping#shopping_performance
    """


class CustomQuery(IncrementalGoogleAdsStream):
    def __init__(self, custom_query_config, **kwargs):
        self.custom_query_config = custom_query_config
        self.user_defined_query = custom_query_config["query"]
        super().__init__(**kwargs)

    @property
    def primary_key(self) -> str:
        """
        The primary_key option is disabled. Config should not provide the primary key.
        It will be ignored if provided.
        If you need to enable it, uncomment the next line instead of `return None` and modify your config
        """
        # return self.custom_query_config.get("primary_key") or None
        return None

    @property
    def name(self):
        return self.custom_query_config["table_name"]

    @property
    def cursor_field(self) -> str:
        """
        The incremental is disabled. Config / spec should not provide the cursor_field.
        It will be ignored if provided.
        However, this return should be kept for case we wanna support it.
        Disabled cursor_field should be always empty array or string, to keep the internal logic
            (get length of cursor_field).
        Since it is not provided, the stream will be full refresh anyway.
        The inheritance from the Incremental stream is made for supporting both types,
            and need to be kept.
        If you need to enable this option, uncomment the first return and modify your config
        """
        # return self.custom_query_config.get("cursor_field") or []
        return []

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        if not self.cursor_field:
            return [None]
        return super().stream_slices(stream_state=stream_state, **kwargs)

    def get_query(self, stream_slice: Mapping[str, Any] = None) -> str:
        if not self.cursor_field:
            return self.user_defined_query
        start_date, end_date = self.get_date_params(stream_slice, self.cursor_field)
        final_query = (
            self.user_defined_query
            + f"\nWHERE {self.cursor_field} > '{start_date}' AND {self.cursor_field} < '{end_date}' ORDER BY {self.cursor_field} ASC"
        )
        return final_query

    def get_json_schema(self):
        local_json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }
        # full list {'ENUM', 'STRING', 'DATE', 'DOUBLE', 'RESOURCE_NAME', 'INT32', 'INT64', 'BOOLEAN', 'MESSAGE'}
        google_datatype_mapping = {
            "INT64": "integer",
            "INT32": "integer",
            "DOUBLE": "number",
            "STRING": "string",
            "BOOLEAN": "boolean",
            "DATE": "string",
        }
        fields = self.user_defined_query.lower().split("select")[1].split("from")[0].strip()
        google_resource_name = self.user_defined_query.lower().split("from", 1)[1].strip()
        google_resource_name = re.split("\\s+", google_resource_name)[0]

        fields = fields.split(",")
        fields = [i.strip() for i in fields]
        fields = list(dict.fromkeys(fields))

        google_schema = ResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema(f"shared/v8_{google_resource_name}")
        for field in fields:
            node = google_schema.get("fields").get(field).get("field_details")
            google_data_type = node.get("data_type")
            if google_data_type == "ENUM":
                field_value = {"type": "string", "enum": node.get("enum_values")}
            elif google_data_type == "MESSAGE":  # this can be anything (or skip as additionalproperties) ?
                output_type = ["string", "number", "array", "object", "boolean", "null"]
                field_value = {"type": output_type}
            else:
                output_type = [google_datatype_mapping.get(google_data_type, "string"), "null"]
                field_value = {"type": output_type}
            local_json_schema["properties"][field] = field_value

        return local_json_schema


class UserLocationReport(IncrementalGoogleAdsStream):
    """
    UserLocationReport stream: https://developers.google.com/google-ads/api/fields/v8/user_location_view
    Google Ads API field mapping: https://developers.google.com/google-ads/api/docs/migration/mapping#geo_performance
    """
