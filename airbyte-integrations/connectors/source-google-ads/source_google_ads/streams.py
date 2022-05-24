#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v8.services.services.google_ads_service.pagers import SearchPager

from .google_ads import GoogleAds


def parse_dates(stream_slice):
    start_date = pendulum.parse(stream_slice["start_date"])
    end_date = pendulum.parse(stream_slice["end_date"])
    return start_date, end_date


def get_date_params(start_date: str, time_zone=None, range_days: int = None, end_date: pendulum.datetime = None) -> Tuple[str, str]:
    """
    Returns `start_date` and `end_date` for the given stream_slice.
    If (end_date - start_date) is a big date range (>= 1 month), it can take more than 2 hours to process all the records from the given slice.
    After 2 hours next page tokens will be expired, finally resulting in page token expired error
    Currently this method returns `start_date` and `end_date` with 15 days difference.
    """

    end_date = end_date or pendulum.yesterday(tz=time_zone)
    start_date = pendulum.parse(start_date)
    if start_date > pendulum.now():
        return start_date.to_date_string(), start_date.add(days=1).to_date_string()
    end_date = min(end_date, start_date.add(days=range_days))

    # Fix issue #4806, start date should always be lower than end date.
    if start_date.add(days=1).date() >= end_date.date():
        return start_date.add(days=1).to_date_string(), start_date.add(days=2).to_date_string()
    return start_date.add(days=1).to_date_string(), end_date.to_date_string()


def chunk_date_range(
    start_date: str,
    conversion_window: int,
    field: str,
    end_date: str = None,
    days_of_data_storage: int = None,
    range_days: int = None,
    time_zone=None,
) -> Iterable[Optional[Mapping[str, any]]]:
    """
    Passing optional parameter end_date for testing
    Returns a list of the beginning and ending timestamps of each `range_days` between the start date and now.
    The return value is a list of dicts {'date': str} which can be used directly with the Slack API
    """
    intervals = []
    end_date = pendulum.parse(end_date) if end_date else pendulum.now()
    start_date = pendulum.parse(start_date)

    # For some metrics we can only get data not older than N days, it is Google Ads policy
    if days_of_data_storage:
        start_date = max(start_date, pendulum.now().subtract(days=days_of_data_storage - conversion_window))

    # As in to return some state when state in abnormal
    if start_date > end_date:
        return [None]

    # applying conversion window
    start_date = start_date.subtract(days=conversion_window)

    while start_date < end_date:
        start, end = get_date_params(start_date.to_date_string(), time_zone=time_zone, range_days=range_days)
        intervals.append(
            {
                "start_date": start,
                "end_date": end,
            }
        )
        start_date = start_date.add(days=range_days)
    return intervals


class GoogleAdsStream(Stream, ABC):
    def __init__(self, api: GoogleAds):
        self.google_ads_client = api
        self._customer_id = None

    def get_query(self, stream_slice: Mapping[str, Any]) -> str:
        query = GoogleAds.convert_schema_into_query(schema=self.get_json_schema(), report_name=self.name)
        return query

    def parse_response(self, response: SearchPager) -> Iterable[Mapping]:
        for result in response:
            yield self.google_ads_client.parse_single_result(self.get_json_schema(), result)

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for customer_id in self.google_ads_client.customer_ids:
            self._customer_id = customer_id
            yield {}

    def read_records(self, sync_mode, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        if not stream_slice:
            return []
        account_responses = self.google_ads_client.send_request(self.get_query(stream_slice), customer_id=self._customer_id)
        for response in account_responses:
            yield from self.parse_response(response)


class IncrementalGoogleAdsStream(GoogleAdsStream, ABC):
    days_of_data_storage = None
    cursor_field = "segments.date"
    primary_key = None
    range_days = 15  # date range is set to 15 days, because for conversion_window_days default value is 14. Range less than 15 days will break the integration tests.

    def __init__(
        self, start_date: str, conversion_window_days: int, time_zone: Union[pendulum.timezone, str], end_date: str = None, **kwargs
    ):
        self.conversion_window_days = conversion_window_days
        self._start_date = start_date
        self.time_zone = time_zone
        self._end_date = end_date
        super().__init__(**kwargs)

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for customer_id in self.google_ads_client.customer_ids:
            self._customer_id = customer_id
            stream_state = stream_state or {}
            if stream_state.get(customer_id):
                start_date = stream_state[customer_id].get(self.cursor_field) or self._start_date

            # We should keep backward compatibility with the previous version
            elif stream_state.get(self.cursor_field) and len(self.google_ads_client.customer_ids) == 1:
                start_date = stream_state.get(self.cursor_field) or self._start_date
            else:
                start_date = self._start_date

            end_date = self._end_date

            for chunk in chunk_date_range(
                start_date=start_date,
                end_date=end_date,
                conversion_window=self.conversion_window_days,
                field=self.cursor_field,
                days_of_data_storage=self.days_of_data_storage,
                range_days=self.range_days,
                time_zone=self.time_zone,
            ):
                yield chunk

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        This method is overridden to handle GoogleAdsException with EXPIRED_PAGE_TOKEN error code,
        and update `start_date` key in the `stream_slice` with the latest read record's cursor value, then retry the sync.
        """
        state = stream_state or {}
        while True:
            try:
                records = super().read_records(sync_mode, stream_slice=stream_slice)
                for record in records:
                    state = self.get_updated_state(state, record)
                    yield record
            except GoogleAdsException as exception:
                if exception.failure._pb.errors[0].error_code.request_error == 8:
                    # page token has expired (EXPIRED_PAGE_TOKEN = 8)
                    start_date, end_date = parse_dates(stream_slice)
                    if (end_date - start_date).days == 1:
                        # If range days is 1, no need in retry, because it's the minimum date range
                        self.logger.error("Page token has expired.")
                        raise exception
                    elif state.get(self._customer_id, {}).get(self.cursor_field) == stream_slice["start_date"]:
                        # It couldn't read all the records within one day, it will enter an infinite loop,
                        # so raise the error
                        self.logger.error("Page token has expired.")
                        raise exception
                    # Retry reading records from where it crushed
                    stream_slice["start_date"] = state.get(self._customer_id, {}).get(self.cursor_field, stream_slice["start_date"])
                else:
                    # raise caught error for other error statuses
                    raise exception
            else:
                # return the control if no exception is raised
                return

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}

        if current_stream_state.get(self.cursor_field):
            stream_state = current_stream_state.pop(self.cursor_field)
        elif current_stream_state.get(self._customer_id) and current_stream_state[self._customer_id].get(self.cursor_field):
            stream_state = current_stream_state[self._customer_id][self.cursor_field]
        else:
            current_stream_state.update({self._customer_id: {self.cursor_field: latest_record[self.cursor_field]}})
            return current_stream_state

        date_in_current_stream = pendulum.parse(stream_state)
        date_in_latest_record = pendulum.parse(latest_record[self.cursor_field])

        current_stream_state.update(
            {self._customer_id: {self.cursor_field: (max(date_in_current_stream, date_in_latest_record)).to_date_string()}}
        )

        return current_stream_state

    def get_query(self, stream_slice: Mapping[str, Any] = None) -> str:
        query = GoogleAds.convert_schema_into_query(
            schema=self.get_json_schema(),
            report_name=self.name,
            from_date=stream_slice.get("start_date"),
            to_date=stream_slice.get("end_date"),
            cursor_field=self.cursor_field,
        )
        return query


class Accounts(IncrementalGoogleAdsStream):
    """
    Accounts stream: https://developers.google.com/google-ads/api/fields/v8/customer
    """

    primary_key = ["customer.id", "segments.date"]


class Campaigns(IncrementalGoogleAdsStream):
    """
    Campaigns stream: https://developers.google.com/google-ads/api/fields/v8/campaign
    """

    primary_key = ["campaign.id", "segments.date"]


class CampaignLabels(GoogleAdsStream):
    """
    Campaign labels stream: https://developers.google.com/google-ads/api/fields/v8/campaign_label
    """

    # Note that this is a string type. Google doesn't return a more convenient identifier.
    primary_key = ["campaign_label.resource_name"]


class AdGroups(IncrementalGoogleAdsStream):
    """
    AdGroups stream: https://developers.google.com/google-ads/api/fields/v8/ad_group
    """

    primary_key = ["ad_group.id", "segments.date"]


class AdGroupLabels(GoogleAdsStream):
    """
    Ad Group Labels stream: https://developers.google.com/google-ads/api/fields/v8/ad_group_label
    """

    # Note that this is a string type. Google doesn't return a more convenient identifier.
    primary_key = ["ad_group_label.resource_name"]


class AdGroupAds(IncrementalGoogleAdsStream):
    """
    AdGroups stream: https://developers.google.com/google-ads/api/fields/v8/ad_group_ad
    """

    primary_key = ["ad_group_ad.ad.id", "segments.date"]


class AdGroupAdLabels(GoogleAdsStream):
    """
    Ad Group Ad Labels stream: https://developers.google.com/google-ads/api/fields/v8/ad_group_ad_label
    """

    # Note that this is a string type. Google doesn't return a more convenient identifier.
    primary_key = ["ad_group_ad_label.resource_name"]


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


class UserLocationReport(IncrementalGoogleAdsStream):
    """
    UserLocationReport stream: https://developers.google.com/google-ads/api/fields/v8/user_location_view
    Google Ads API field mapping: https://developers.google.com/google-ads/api/docs/migration/mapping#geo_performance
    """


class GeographicReport(IncrementalGoogleAdsStream):
    """
    UserLocationReport stream: https://developers.google.com/google-ads/api/fields/v8/geographic_view
    """


class KeywordReport(IncrementalGoogleAdsStream):
    """
    UserLocationReport stream: https://developers.google.com/google-ads/api/fields/v8/keyword_view
    """


class ClickView(IncrementalGoogleAdsStream):
    """
    ClickView stream: https://developers.google.com/google-ads/api/reference/rpc/v8/ClickView
    """

    primary_key = ["click_view.gclid", "segments.date", "segments.ad_network_type"]
    days_of_data_storage = 90
    range_days = 1
