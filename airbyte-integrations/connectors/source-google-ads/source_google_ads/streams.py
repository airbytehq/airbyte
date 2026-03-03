#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from typing import Any, Iterable, Iterator, List, Mapping, MutableMapping, Optional

import backoff
import pendulum
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v20.services.services.google_ads_service.pagers import SearchPager
from google.ads.googleads.v20.services.types.google_ads_service import SearchGoogleAdsResponse
from google.api_core.exceptions import InternalServerError, ServerError, ServiceUnavailable, TooManyRequests, Unauthenticated

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.streams import CheckpointMixin, Stream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.utils import AirbyteTracedException

from .google_ads import GoogleAds, logger
from .models import CustomerModel
from .utils import ExpiredPageTokenError, chunk_date_range, detached, generator_backoff, get_resource_name, parse_dates, traced_exception


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
            yield {"customer_id": customer.id, "login_customer_id": customer.login_customer_id}

    @generator_backoff(
        wait_gen=backoff.constant,
        exception=(TimeoutError),
        max_tries=5,
        on_backoff=lambda details: logger.info(
            f"Caught retryable error {details['exception']} after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        ),
        interval=1,
    )
    @detached(timeout_minutes=5)
    def request_records_job(self, customer_id, login_customer_id, query, stream_slice):
        response_records = self.google_ads_client.send_request(query=query, customer_id=customer_id, login_customer_id=login_customer_id)
        yield from self.parse_records_with_backoff(response_records, stream_slice)

    def read_records(self, sync_mode, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        if stream_slice is None:
            return []

        customer_id = stream_slice["customer_id"]
        login_customer_id = stream_slice["login_customer_id"]

        try:
            yield from self.request_records_job(customer_id, login_customer_id, self.get_query(stream_slice), stream_slice)
        except (GoogleAdsException, Unauthenticated) as exception:
            traced_exception(exception, customer_id, self.CATCH_CUSTOMER_NOT_ENABLED_ERROR)
        except TimeoutError as exception:
            # Prevent sync failure
            logger.warning(f"Timeout: Failed to access {self.name} stream data. {str(exception)}")

    @generator_backoff(
        wait_gen=backoff.expo,
        exception=(InternalServerError, ServerError, ServiceUnavailable, TooManyRequests),
        max_tries=5,
        max_time=600,
        on_backoff=lambda details: logger.info(
            f"Caught retryable error {details['exception']} after {details['tries']} tries. Waiting {details['wait']} seconds then retrying..."
        ),
        factor=5,
    )
    def parse_records_with_backoff(
        self, response_records: Iterator[SearchGoogleAdsResponse], stream_slice: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Mapping[str, Any]]:
        for response in response_records:
            yield from self.parse_response(response, stream_slice)


class IncrementalGoogleAdsStream(GoogleAdsStream, CheckpointMixin, ABC):
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
        if self.state is not None:
            customer = self.state.get(customer_id, {})
            if isinstance(customer, MutableMapping):
                return customer.get(self.cursor_field)
        else:
            return default

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
                    chunk["login_customer_id"] = customer.login_customer_id
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


class CustomerClient(GoogleAdsStream):
    """
    Customer Client stream: https://developers.google.com/google-ads/api/fields/v20/customer_client
    """

    primary_key = ["customer_client.id"]

    def __init__(self, customer_status_filter: List[str], **kwargs):
        self.customer_status_filter = customer_status_filter
        super().__init__(**kwargs)

    def get_query(self, stream_slice: Mapping[str, Any] = None) -> str:
        fields = GoogleAds.get_fields_from_schema(self.get_json_schema())
        table_name = get_resource_name(self.name)

        active_customers_condition = []
        if self.customer_status_filter:
            customer_status_filter = ", ".join([f"'{status}'" for status in self.customer_status_filter])
            active_customers_condition = [f"customer_client.status in ({customer_status_filter})"]

        query = GoogleAds.convert_schema_into_query(fields=fields, table_name=table_name, conditions=active_customers_condition)
        return query

    def read_records(self, sync_mode, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        This method is overridden to avoid using login_customer_id from dummy_customers.

        login_customer_id is used in the stream_slices to pass it to child customers,
        but we don't need it here as this class iterate over customers accessible from user creds.
        """
        if stream_slice is None:
            return []

        customer_id = stream_slice["customer_id"]

        try:
            response_records = self.google_ads_client.send_request(self.get_query(stream_slice), customer_id=customer_id)

            yield from self.parse_records_with_backoff(response_records, stream_slice)
        except GoogleAdsException as exception:
            traced_exception(exception, customer_id, self.CATCH_CUSTOMER_NOT_ENABLED_ERROR)

    def parse_response(self, response: SearchPager, stream_slice: Optional[Mapping[str, Any]] = None) -> Iterable[Mapping]:
        """
        login_cusotmer_id is populated to child customers if they are under managers account
        """
        records = [record for record in super().parse_response(response)]

        # read_records get all customers connected to customer_id from stream_slice
        # if the result is more than one customer, it's a manager, otherwise it is client account for which we don't need login_customer_id
        root_is_manager = len(records) > 1
        for record in records:
            record["login_customer_id"] = stream_slice["login_customer_id"] if root_is_manager else "default"
            yield record


class ServiceAccounts(GoogleAdsStream):
    """
    This stream is intended to be used as a service class, not exposed to a user
    """

    CATCH_CUSTOMER_NOT_ENABLED_ERROR = False
    primary_key = ["customer.id"]
