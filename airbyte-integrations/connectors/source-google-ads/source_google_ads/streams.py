#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import FailureType
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v11.services.services.google_ads_service.pagers import SearchPager

from .google_ads import GoogleAds
from .models import CustomerModel
from .utils import ExpiredPageTokenError, get_resource_name, traced_exception


def parse_dates(stream_slice):
    start_date = pendulum.parse(stream_slice["start_date"])
    end_date = pendulum.parse(stream_slice["end_date"])
    return start_date, end_date


def chunk_date_range(
    start_date: str,
    end_date: str = None,
    conversion_window: int = 0,
    days_of_data_storage: int = None,
    time_zone=None,
    time_format="YYYY-MM-DD",
    slice_duration: pendulum.Duration = pendulum.duration(days=14),
    slice_step: pendulum.Duration = pendulum.duration(days=1),
) -> Iterable[Optional[MutableMapping[str, any]]]:
    """
    Splits a date range into smaller chunks based on the provided parameters.

    Args:
        start_date (str): The beginning date of the range.
        end_date (str, optional): The ending date of the range. Defaults to today's date.
        conversion_window (int): Number of days to subtract from the start date. Defaults to 0.
        days_of_data_storage (int, optional): Maximum age of data that can be retrieved. Used to adjust the start date.
        time_zone: Time zone to be used for date parsing and today's date calculation. If not provided, the default time zone is used.
        time_format (str): Format to be used when returning dates. Defaults to 'YYYY-MM-DD'.
        slice_duration (pendulum.Duration): Duration of each chunk. Defaults to 14 days.
        slice_step (pendulum.Duration): Step size to move to the next chunk. Defaults to 1 day.

    Returns:
        Iterable[Optional[MutableMapping[str, any]]]: An iterable of dictionaries containing start and end dates for each chunk.
        If the adjusted start date is greater than the end date, returns a list with a None value.

    Notes:
        - If the difference between `end_date` and `start_date` is large (e.g., >= 1 month), processing all records might take a long time.
        - Tokens for fetching subsequent pages of data might expire after 2 hours, leading to potential errors.
        - The function adjusts the start date based on `days_of_data_storage` and `conversion_window` to adhere to certain data retrieval policies, such as Google Ads' policy of only retrieving data not older than a certain number of days.
        - The method returns `start_date` and `end_date` with a difference typically spanning 15 days to avoid token expiration issues.
    """
    start_date = pendulum.parse(start_date, tz=time_zone)
    today = pendulum.today(tz=time_zone)
    end_date = pendulum.parse(end_date, tz=time_zone) if end_date else today

    # For some metrics we can only get data not older than N days, it is Google Ads policy
    if days_of_data_storage:
        start_date = max(start_date, pendulum.now(tz=time_zone).subtract(days=days_of_data_storage - conversion_window))

    # As in to return some state when state in abnormal
    if start_date > end_date:
        return [None]

    # applying conversion window
    start_date = start_date.subtract(days=conversion_window)
    slice_start = start_date

    while slice_start <= end_date:
        slice_end = min(end_date, slice_start + slice_duration)
        yield {
            "start_date": slice_start.format(time_format),
            "end_date": slice_end.format(time_format),
        }
        slice_start = slice_end + slice_step


class GoogleAdsStream(Stream, ABC):
    CATCH_CUSTOMER_NOT_ENABLED_ERROR = True

    def __init__(self, api: GoogleAds, customers: List[CustomerModel]):
        self.google_ads_client = api
        self.customers = customers

    def get_query(self, stream_slice: Mapping[str, Any]) -> str:
        fields = GoogleAds.get_fields_from_schema(self.get_json_schema())
        table_name = get_resource_name(self.name)
        query = GoogleAds.convert_schema_into_query(fields=fields, table_name=table_name)
        return query

    def parse_response(self, response: SearchPager, stream_slice: Optional[Mapping[str, Any]] = None) -> Iterable[Mapping]:
        for result in response:
            yield self.google_ads_client.parse_single_result(self.get_json_schema(), result)

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for customer in self.customers:
            yield {"customer_id": customer.id}

    def read_records(self, sync_mode, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        if stream_slice is None:
            return []

        customer_id = stream_slice["customer_id"]
        try:
            response_records = self.google_ads_client.send_request(self.get_query(stream_slice), customer_id=customer_id)
            for response in response_records:
                yield from self.parse_response(response, stream_slice)
        except GoogleAdsException as exception:
            traced_exception(exception, customer_id, self.CATCH_CUSTOMER_NOT_ENABLED_ERROR)


class IncrementalGoogleAdsStream(GoogleAdsStream, IncrementalMixin, ABC):
    primary_key = None
    days_of_data_storage = None
    cursor_field = "segments.date"
    cursor_time_format = "YYYY-MM-DD"
    # Slice duration is set to 14 days, because for conversion_window_days default value is 14.
    # Range less than 14 days will break the integration tests.
    slice_duration = pendulum.duration(days=14)
    # slice step is difference from one slice end_date and next slice start_date
    slice_step = pendulum.duration(days=1)

    def __init__(self, start_date: str, conversion_window_days: int, end_date: str = None, **kwargs):
        self.conversion_window_days = conversion_window_days
        self._start_date = start_date
        self._end_date = end_date
        self._state = {}
        super().__init__(**kwargs)

    @property
    def state_checkpoint_interval(self) -> int:
        # default page size is 10000, so set to 10% of it
        return 1000

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state.update(value)

    def get_current_state(self, customer_id, default=None):
        default = default or self.state.get(self.cursor_field)
        return self.state.get(customer_id, {}).get(self.cursor_field) or default

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[MutableMapping[str, any]]]:
        for customer in self.customers:
            stream_state = stream_state or {}
            if stream_state.get(customer.id):
                start_date = stream_state[customer.id].get(self.cursor_field) or self._start_date

            # We should keep backward compatibility with the previous version
            elif stream_state.get(self.cursor_field) and len(self.customers) == 1:
                start_date = stream_state.get(self.cursor_field) or self._start_date
            else:
                start_date = self._start_date

            end_date = self._end_date

            for chunk in chunk_date_range(
                start_date=start_date,
                end_date=end_date,
                conversion_window=self.conversion_window_days,
                days_of_data_storage=self.days_of_data_storage,
                time_zone=customer.time_zone,
                time_format=self.cursor_time_format,
                slice_duration=self.slice_duration,
                slice_step=self.slice_step,
            ):
                if chunk:
                    chunk["customer_id"] = customer.id
                yield chunk

    def _update_state(self, customer_id: str, record: MutableMapping[str, Any]):
        """Update the state based on the latest record's cursor value."""
        current_state = self.get_current_state(customer_id)
        if current_state:
            date_in_current_stream = pendulum.parse(current_state)
            date_in_latest_record = pendulum.parse(record[self.cursor_field])
            cursor_value = (max(date_in_current_stream, date_in_latest_record)).format(self.cursor_time_format)
            self.state = {customer_id: {self.cursor_field: cursor_value}}
        else:
            self.state = {customer_id: {self.cursor_field: record[self.cursor_field]}}

    def _handle_expired_page_exception(self, exception: ExpiredPageTokenError, stream_slice: MutableMapping[str, Any], customer_id: str):
        """
        Handle Google Ads EXPIRED_PAGE_TOKEN error by updating the stream slice.
        """
        start_date, end_date = parse_dates(stream_slice)
        current_state = self.get_current_state(customer_id)

        if end_date - start_date <= self.slice_step:
            # If range days less than slice_step, no need in retry, because it's the minimum date range
            raise exception
        elif current_state == stream_slice["start_date"]:
            # It couldn't read all the records within one day, it will enter an infinite loop,
            # so raise the error
            raise exception
        # Retry reading records from where it crushed
        stream_slice["start_date"] = self.get_current_state(customer_id, default=stream_slice["start_date"])

    def read_records(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: MutableMapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        """
        This method is overridden to handle GoogleAdsException with EXPIRED_PAGE_TOKEN error code,
        and update `start_date` key in the `stream_slice` with the latest read record's cursor value, then retry the sync.
        """
        while True:
            customer_id = stream_slice and stream_slice["customer_id"]

            try:
                # count records to update slice date range with latest record time when limit is hit
                records = super().read_records(sync_mode, stream_slice=stream_slice)
                for record in records:
                    self._update_state(customer_id, record)
                    yield record
            except ExpiredPageTokenError as exception:
                # handle expired page error that was caught in parent class by updating stream_slice
                self._handle_expired_page_exception(exception, stream_slice, customer_id)
            else:
                return

    def get_query(self, stream_slice: Mapping[str, Any] = None) -> str:
        fields = GoogleAds.get_fields_from_schema(self.get_json_schema())
        table_name = get_resource_name(self.name)

        start_date, end_date = stream_slice.get("start_date"), stream_slice.get("end_date")
        cursor_condition = [f"{self.cursor_field} >= '{start_date}' AND {self.cursor_field} <= '{end_date}'"]

        query = GoogleAds.convert_schema_into_query(
            fields=fields, table_name=table_name, conditions=cursor_condition, order_field=self.cursor_field
        )
        return query


class Customer(IncrementalGoogleAdsStream):
    """
    Customer stream: https://developers.google.com/google-ads/api/fields/v11/customer
    """

    primary_key = ["customer.id", "segments.date"]

    def parse_response(self, response: SearchPager, stream_slice: Optional[Mapping[str, Any]] = None) -> Iterable[Mapping]:
        for record in super().parse_response(response):
            if isinstance(record.get("customer.optimization_score_weight"), int):
                record["customer.optimization_score_weight"] = float(record["customer.optimization_score_weight"])
            yield record


class CustomerLabel(GoogleAdsStream):
    """
    Customer Label stream: https://developers.google.com/google-ads/api/fields/v14/customer_label
    """

    primary_key = ["customer_label.resource_name"]


class ServiceAccounts(GoogleAdsStream):
    """
    This stream is intended to be used as a service class, not exposed to a user
    """

    CATCH_CUSTOMER_NOT_ENABLED_ERROR = False
    primary_key = ["customer.id"]


class Campaign(IncrementalGoogleAdsStream):
    """
    Campaign stream: https://developers.google.com/google-ads/api/fields/v11/campaign
    """

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    primary_key = ["campaign.id", "segments.date", "segments.hour", "segments.ad_network_type"]


class CampaignBudget(IncrementalGoogleAdsStream):
    """
    Campaigns stream: https://developers.google.com/google-ads/api/fields/v13/campaign_budget
    """

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    primary_key = [
        "customer.id",
        "campaign_budget.id",
        "segments.date",
        "segments.budget_campaign_association_status.campaign",
        "segments.budget_campaign_association_status.status",
    ]


class CampaignBiddingStrategy(IncrementalGoogleAdsStream):
    """
    Campaign Bidding Strategy stream: https://developers.google.com/google-ads/api/fields/v14/campaign
    """

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    primary_key = ["campaign.id", "bidding_strategy.id", "segments.date"]


class CampaignLabel(GoogleAdsStream):
    """
    Campaign labels stream: https://developers.google.com/google-ads/api/fields/v11/campaign_label
    """

    # Note that this is a string type. Google doesn't return a more convenient identifier.
    primary_key = ["campaign.id", "label.id"]


class AdGroup(IncrementalGoogleAdsStream):
    """
    AdGroup stream: https://developers.google.com/google-ads/api/fields/v11/ad_group
    """

    primary_key = ["ad_group.id", "segments.date"]


class AdGroupLabel(GoogleAdsStream):
    """
    Ad Group Labels stream: https://developers.google.com/google-ads/api/fields/v11/ad_group_label
    """

    # Note that this is a string type. Google doesn't return a more convenient identifier.
    primary_key = ["ad_group.id", "label.id"]


class AdGroupBiddingStrategy(IncrementalGoogleAdsStream):
    """
    Ad Group Bidding Strategies stream: https://developers.google.com/google-ads/api/fields/v14/ad_group
    """

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    primary_key = ["ad_group.id", "bidding_strategy.id", "segments.date"]


class AdGroupCriterionLabel(GoogleAdsStream):
    """
    Ad Group Criterion Label stream: https://developers.google.com/google-ads/api/fields/v14/ad_group_criterion_label
    """

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    primary_key = ["ad_group_criterion_label.resource_name"]


class AdGroupAd(IncrementalGoogleAdsStream):
    """
    Ad Group Ad stream: https://developers.google.com/google-ads/api/fields/v11/ad_group_ad
    """

    primary_key = ["ad_group.id", "ad_group_ad.ad.id", "segments.date"]


class AdGroupAdLabel(GoogleAdsStream):
    """
    Ad Group Ad Labels stream: https://developers.google.com/google-ads/api/fields/v11/ad_group_ad_label
    """

    primary_key = ["ad_group.id", "ad_group_ad.ad.id", "label.id"]


class AccountPerformanceReport(IncrementalGoogleAdsStream):
    """
    AccountPerformanceReport stream: https://developers.google.com/google-ads/api/fields/v11/customer
    Google Ads API field mapping: https://developers.google.com/google-ads/api/docs/migration/mapping#account_performance
    """

    primary_key = ["customer.id", "segments.date", "segments.ad_network_type", "segments.device"]


class AdGroupAdLegacy(IncrementalGoogleAdsStream):
    """
    AdGroupAdReport stream: https://developers.google.com/google-ads/api/fields/v11/ad_group_ad
    Google Ads API field mapping: https://developers.google.com/google-ads/api/docs/migration/mapping#ad_performance
    """

    primary_key = ["ad_group.id", "ad_group_ad.ad.id", "segments.date", "segments.ad_network_type"]


class DisplayKeywordView(IncrementalGoogleAdsStream):
    """
    DisplayKeywordView stream: https://developers.google.com/google-ads/api/fields/v11/display_keyword_view
    Google Ads API field mapping: https://developers.google.com/google-ads/api/docs/migration/mapping#display_keyword_performance
    """

    primary_key = [
        "ad_group.id",
        "ad_group_criterion.criterion_id",
        "segments.date",
        "segments.ad_network_type",
        "segments.device",
    ]


class TopicView(IncrementalGoogleAdsStream):
    """
    DisplayTopicsPerformanceReport stream: https://developers.google.com/google-ads/api/fields/v11/topic_view
    Google Ads API field mapping: https://developers.google.com/google-ads/api/docs/migration/mapping#display_topics_performance
    """

    primary_key = [
        "ad_group.id",
        "ad_group_criterion.criterion_id",
        "segments.date",
        "segments.ad_network_type",
        "segments.device",
    ]


class ShoppingPerformanceView(IncrementalGoogleAdsStream):
    """
    ShoppingPerformanceView stream: https://developers.google.com/google-ads/api/fields/v11/shopping_performance_view
    Google Ads API field mapping: https://developers.google.com/google-ads/api/docs/migration/mapping#shopping_performance
    """


class UserLocationView(IncrementalGoogleAdsStream):
    """
    UserLocationView stream: https://developers.google.com/google-ads/api/fields/v11/user_location_view
    Google Ads API field mapping: https://developers.google.com/google-ads/api/docs/migration/mapping#geo_performance
    """

    primary_key = [
        "customer.id",
        "user_location_view.country_criterion_id",
        "user_location_view.targeting_location",
        "segments.date",
        "segments.ad_network_type",
    ]


class GeographicView(IncrementalGoogleAdsStream):
    """
    UserLocationReport stream: https://developers.google.com/google-ads/api/fields/v11/geographic_view
    """

    primary_key = ["customer.id", "geographic_view.country_criterion_id", "geographic_view.location_type", "segments.date"]


class KeywordView(IncrementalGoogleAdsStream):
    """
    UserLocationReport stream: https://developers.google.com/google-ads/api/fields/v11/keyword_view
    """

    primary_key = ["ad_group.id", "ad_group_criterion.criterion_id", "segments.date"]


class ClickView(IncrementalGoogleAdsStream):
    """
    ClickView stream: https://developers.google.com/google-ads/api/reference/rpc/v11/ClickView
    """

    primary_key = ["click_view.gclid", "segments.date", "segments.ad_network_type"]
    days_of_data_storage = 90
    # where clause for cursor is inclusive from both sides, duration 0 will result in - '"2022-01-01" <= cursor AND "2022-01-01" >= cursor'
    # Queries including ClickView must have a filter limiting the results to one day
    slice_duration = pendulum.duration(days=0)


class UserInterest(GoogleAdsStream):
    """
    Ad Group Ad Labels stream: https://developers.google.com/google-ads/api/fields/v11/ad_group_ad_label
    """

    primary_key = ["user_interest.user_interest_id"]


class Audience(GoogleAdsStream):
    """
    Ad Group Ad Labels stream: https://developers.google.com/google-ads/api/fields/v11/ad_group_ad_label
    """

    primary_key = ["customer.id", "audience.id"]


class Label(GoogleAdsStream):
    """
    Label stream: https://developers.google.com/google-ads/api/fields/v14/label
    """

    primary_key = ["label.id"]


class ChangeStatus(IncrementalGoogleAdsStream):
    """
    Change status stream: https://developers.google.com/google-ads/api/fields/v14/change_status
    Stream is only used internally to implement incremental updates for child streams of IncrementalEventsStream
    """

    cursor_field = "change_status.last_change_date_time"
    slice_step = pendulum.duration(microseconds=1)
    days_of_data_storage = 90
    cursor_time_format = "YYYY-MM-DD HH:mm:ss.SSSSSS"

    def __init__(self, **kwargs):
        # date range is not used for these streams, only state is used to sync recent records, otherwise full refresh
        for key in ["start_date", "conversion_window_days", "end_date"]:
            kwargs.pop(key, None)
        super().__init__(start_date=None, conversion_window_days=0, end_date=None, **kwargs)

    @property
    def query_limit(self) -> Optional[int]:
        "Queries for ChangeStatus resource have to include limit in it"
        return 10000

    def read_records(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: MutableMapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        """
        This method is overridden to handle GoogleAdsException with EXPIRED_PAGE_TOKEN error code,
        and update `start_date` key in the `stream_slice` with the latest read record's cursor value, then retry the sync.
        """
        while True:
            records_count = 0
            customer_id = stream_slice and stream_slice["customer_id"]

            try:
                # count records to update slice date range with latest record time when limit is hit
                records = super().read_records(sync_mode, stream_slice=stream_slice)
                for records_count, record in enumerate(records, start=1):
                    self._update_state(customer_id, record)
                    yield record
            except ExpiredPageTokenError as exception:
                # handle expired page error that was caught in parent class by updating stream_slice
                self._handle_expired_page_exception(exception, stream_slice, customer_id)
            else:
                # if records limit is hit - update slice with new start_date to continue reading
                if self.query_limit and records_count == self.query_limit:
                    # if state was not updated before hitting limit - raise error to avoid infinite loop
                    if stream_slice["start_date"] == self.get_current_state(customer_id):
                        raise AirbyteTracedException(
                            message=f"More then limit {self.query_limit} records with same cursor field. Incremental sync is not possible for this stream.",
                            failure_type=FailureType.system_error,
                        )

                    current_state = self.get_current_state(customer_id, default=stream_slice["start_date"])
                    stream_slice["start_date"] = current_state
                else:
                    return

    def get_query(self, stream_slice: Mapping[str, Any] = None) -> str:
        fields = GoogleAds.get_fields_from_schema(self.get_json_schema())
        table_name = get_resource_name(self.name)

        start_date, end_date = stream_slice.get("start_date"), stream_slice.get("end_date")
        conditions = [f"{self.cursor_field} >= '{start_date}' AND {self.cursor_field} <= '{end_date}'"]

        resource_type = stream_slice.get("resource_type")
        conditions.append(f"change_status.resource_type = '{resource_type}'")

        query = GoogleAds.convert_schema_into_query(
            fields=fields, table_name=table_name, conditions=conditions, order_field=self.cursor_field, limit=self.query_limit
        )
        return query


class IncrementalEventsStream(GoogleAdsStream, IncrementalMixin, ABC):
    """
    Abstract class used for getting incremental updates based on events returned from ChangeStatus stream.
    Only Ad Group Criterion and Campaign Criterion streams are fetched using this class, for other resources
    like Campaigns, Ad Groups, Ad Group Ads, and Campaign Budget we already fetch incremental updates based on date.
    Also, these resources, unlike criterions, can't be deleted, only marked as "Removed".
    """

    def __init__(self, **kwargs):
        self.parent_stream = ChangeStatus(api=kwargs.get("api"), customers=kwargs.get("customers"))
        self.parent_stream_name: str = self.parent_stream.name
        self.parent_cursor_field: str = self.parent_stream.cursor_field

        super().__init__(**kwargs)

        self._state = {self.parent_stream_name: {customer.id: None for customer in self.customers}}

    @property
    @abstractmethod
    def id_field(self) -> str:
        "Name of field used for getting records by id"
        pass

    @property
    @abstractmethod
    def parent_id_field(self) -> str:
        "Field name of id from parent record"
        pass

    @property
    @abstractmethod
    def resource_type(self) -> str:
        "Resource type used for filtering parent records"
        pass

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state.update(value)
        self.parent_stream.state = self._state.get(self.parent_stream_name, {})

    def get_current_state(self, customer_id, default=None):
        return self.parent_stream.get_current_state(customer_id, default)

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[MutableMapping[str, any]]]:
        """
        If state exists read updates from parent stream otherwise return slices with only customer id to sync all records for stream
        """
        if stream_state:
            slices_generator = self.read_parent_stream(SyncMode.incremental, self.parent_cursor_field, stream_state)
            yield from slices_generator
        else:
            for customer in self.customers:
                yield {"customer_id": customer.id, "updated_ids": set(), "deleted_ids": set(), "record_changed_time_map": dict()}

    def _process_parent_record(self, parent_record: MutableMapping[str, Any], child_slice: MutableMapping[str, Any]) -> bool:
        """Process a single parent_record and update the child_slice."""
        substream_id = parent_record.get(self.parent_id_field)
        if not substream_id:
            return False

        # Save time of change
        child_slice["record_changed_time_map"][substream_id] = parent_record[self.parent_cursor_field]

        # Add record id to list of changed or deleted items depending on status
        slice_id_list = "deleted_ids" if parent_record.get("change_status.resource_status") == "REMOVED" else "updated_ids"
        child_slice[slice_id_list].add(substream_id)

        return True

    def read_parent_stream(
        self, sync_mode: SyncMode, cursor_field: Optional[str], stream_state: Mapping[str, Any]
    ) -> Iterable[Mapping[str, Any]]:
        for parent_slice in self.parent_stream.stream_slices(
            sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state.get(self.parent_stream_name)
        ):
            customer_id = parent_slice.get("customer_id")
            child_slice = {"customer_id": customer_id, "updated_ids": set(), "deleted_ids": set(), "record_changed_time_map": dict()}
            if not self.get_current_state(customer_id):
                yield child_slice
                continue

            parent_slice["resource_type"] = self.resource_type
            for parent_record in self.parent_stream.read_records(sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=parent_slice):
                self._process_parent_record(parent_record, child_slice)

            # yield child slice if any records where read
            if child_slice["record_changed_time_map"]:
                yield child_slice

    def parse_response(self, response: SearchPager, stream_slice: MutableMapping[str, Any] = None) -> Iterable[Mapping]:
        # update records with time obtained from parent stream
        for record in super().parse_response(response):
            primary_key_value = record[self.primary_key[0]]

            # cursor value obtained from parent stream
            cursor_value = stream_slice.get("record_changed_time_map", dict()).get(primary_key_value)

            record[self.cursor_field] = cursor_value
            yield record

    def _update_state(self, stream_slice: MutableMapping[str, Any]):
        customer_id = stream_slice.get("customer_id")

        # if parent stream was used - copy state from it, otherwise set default state
        if isinstance(self.parent_stream.state, dict) and self.parent_stream.state.get(customer_id):
            self._state[self.parent_stream_name][customer_id] = self.parent_stream.state[customer_id]
        else:
            parent_state = {self.parent_cursor_field: pendulum.today().start_of("day").format(self.parent_stream.cursor_time_format)}
            # full refresh sync without parent stream
            self._state[self.parent_stream_name].update({customer_id: parent_state})

    def _read_deleted_records(self, stream_slice: MutableMapping[str, Any] = None):
        # yield deleted records with id and time when record was deleted
        for deleted_record_id in stream_slice.get("deleted_ids", []):
            yield {self.id_field: deleted_record_id, "deleted_at": stream_slice["record_changed_time_map"].get(deleted_record_id)}

    def _split_slice(self, child_slice: MutableMapping[str, Any], chunk_size: int = 10000) -> Iterable[Mapping[str, Any]]:
        """
        Splits a child slice into smaller chunks based on the chunk_size.

        Parameters:
        - child_slice (MutableMapping[str, Any]): The input dictionary to split.
        - chunk_size (int, optional): The maximum number of ids per chunk. Defaults to 10000,
            because it is the maximum number of ids that can be present in a query filter.

        Yields:
        - Mapping[str, Any]: A dictionary with a similar structure to child_slice.
        """
        updated_ids = list(child_slice["updated_ids"])
        if not updated_ids:
            yield child_slice
            return

        record_changed_time_map = child_slice["record_changed_time_map"]
        customer_id = child_slice["customer_id"]

        # Split the updated_ids into chunks and yield them
        for i in range(0, len(updated_ids), chunk_size):
            chunk_ids = set(updated_ids[i : i + chunk_size])
            chunk_time_map = {k: record_changed_time_map[k] for k in chunk_ids}

            yield {"updated_ids": chunk_ids, "record_changed_time_map": chunk_time_map, "customer_id": customer_id, "deleted_ids": set()}

    def read_records(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: MutableMapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping[str, Any]]:
        """
        This method is overridden to read records using parent stream
        """
        # if state is present read records by ids from slice otherwise full refresh sync
        for stream_slice_part in self._split_slice(stream_slice):
            yield from super().read_records(sync_mode, stream_slice=stream_slice_part)

        # yield deleted items
        yield from self._read_deleted_records(stream_slice)

        self._update_state(stream_slice)

    def get_query(self, stream_slice: Mapping[str, Any] = None) -> str:
        table_name = get_resource_name(self.name)

        fields = GoogleAds.get_fields_from_schema(self.get_json_schema())
        # delete fields that are obtained from parent stream and should not be requested from API
        delete_fields = ["change_status.last_change_date_time", "deleted_at"]
        fields = [field_name for field_name in fields if field_name not in delete_fields]

        conditions = []
        # filter by ids obtained from parent stream
        updated_ids = stream_slice.get("updated_ids")
        if updated_ids:
            id_list_str = ", ".join(f"'{str(id_)}'" for id_ in updated_ids)
            conditions.append(f"{self.id_field} IN ({id_list_str})")

        query = GoogleAds.convert_schema_into_query(fields=fields, table_name=table_name, conditions=conditions)
        return query


class AdGroupCriterion(IncrementalEventsStream):
    """
    Ad Group Criterion stream: https://developers.google.com/google-ads/api/fields/v14/ad_group_criterion
    """

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    primary_key = ["ad_group_criterion.resource_name"]
    parent_id_field = "change_status.ad_group_criterion"
    id_field = "ad_group_criterion.resource_name"
    resource_type = "AD_GROUP_CRITERION"
    cursor_field = "change_status.last_change_date_time"


class AdListingGroupCriterion(AdGroupCriterion):
    """
    Ad Listing Group Criterion stream: https://developers.google.com/google-ads/api/fields/v14/ad_group_criterion
    While this stream utilizes the same resource as the AdGroupCriterions,
    it specifically targets the listing group and has distinct schemas.
    """


class CampaignCriterion(IncrementalEventsStream):
    """
    Campaign Criterion stream: https://developers.google.com/google-ads/api/fields/v14/campaign_criterion
    """

    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    primary_key = ["campaign_criterion.resource_name"]
    parent_id_field = "change_status.campaign_criterion"
    id_field = "campaign_criterion.resource_name"
    resource_type = "CAMPAIGN_CRITERION"
    cursor_field = "change_status.last_change_date_time"
