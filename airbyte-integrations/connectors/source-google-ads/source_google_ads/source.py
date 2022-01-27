#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple, Union, Iterator, MutableMapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import ConfiguredAirbyteStream, SyncMode, AirbyteMessage
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from google.ads.googleads.errors import GoogleAdsException

from pendulum import timezone
from pendulum.tz.timezone import Timezone

from .custom_query_stream import CustomQuery
from .google_ads import GoogleAds
from .streams import (
    AccountPerformanceReport,
    Accounts,
    AdGroupAdReport,
    AdGroupAds,
    AdGroups,
    Campaigns,
    ClickView,
    DisplayKeywordPerformanceReport,
    DisplayTopicsPerformanceReport,
    GeographicReport,
    KeywordReport,
    ShoppingPerformanceReport,
    UserLocationReport,
)


class SourceGoogleAds(AbstractSource):
    @staticmethod
    def get_credentials(config: Mapping[str, Any]) -> Mapping[str, Any]:
        credentials = config["credentials"]

        # https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid
        if "login_customer_id" in config and config["login_customer_id"].strip():
            credentials["login_customer_id"] = config["login_customer_id"]
        return credentials

    @staticmethod
    def get_account_info(google_api) -> dict:
        return next(Accounts(api=google_api).read_records(sync_mode=None), {})

    @staticmethod
    def get_time_zone(account: dict) -> Union[timezone, str]:
        time_zone_name = account.get("customer.time_zone")
        if time_zone_name:
            return Timezone(time_zone_name)
        return "local"

    @staticmethod
    def is_manager_account(account: dict) -> bool:
        return bool(account.get("customer.manager"))

    @staticmethod
    def is_metrics_in_custom_query(query: str) -> bool:
        fields = CustomQuery.get_query_fields(query)
        for field in fields:
            if field.startswith("metrics"):
                return True
        return False

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:
            logger.info("Checking the config")
            google_api = GoogleAds(credentials=self.get_credentials(config), customer_id=config["customer_id"])
            account_info = self.get_account_info(google_api)
            is_manager_account = self.is_manager_account(account_info)

            # Check custom query request validity by sending metric request with non-existant time window
            for query in config.get("custom_queries", []):
                query = query.get("query")

                if is_manager_account and self.is_metrics_in_custom_query(query):
                    raise Exception(f"Metrics are not available for manager account. Check fields in your custom query: {query}")
                if CustomQuery.cursor_field in query:
                    raise Exception(f"Custom query should not contain {CustomQuery.cursor_field}")

                req_q = CustomQuery.insert_segments_date_expr(query, "1980-01-01", "1980-01-01")
                google_api.send_request(req_q)
            return True, None
        except GoogleAdsException as error:
            return False, f"Unable to connect to Google Ads API with the provided credentials - {repr(error.failure)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        google_api = GoogleAds(credentials=self.get_credentials(config), customer_id=config["customer_id"])
        account_info = self.get_account_info(google_api)
        time_zone = self.get_time_zone(account_info)
        end_date = config.get("end_date")
        incremental_stream_config = dict(
            api=google_api,
            conversion_window_days=config["conversion_window_days"],
            start_date=config["start_date"],
            time_zone=time_zone,
            end_date=end_date,
        )

        streams = [
            AdGroupAds(api=google_api),
            AdGroups(api=google_api),
            Accounts(api=google_api),
            Campaigns(api=google_api),
            ClickView(**incremental_stream_config),
        ]

        custom_query_streams = [
            CustomQuery(custom_query_config=single_query_config, **incremental_stream_config)
            for single_query_config in config.get("custom_queries", [])
        ]
        streams.extend(custom_query_streams)

        # Metrics streams cannot be requested for a manager account.
        if not self.is_manager_account(account_info):
            streams.extend(
                [
                    UserLocationReport(**incremental_stream_config),
                    AccountPerformanceReport(**incremental_stream_config),
                    DisplayTopicsPerformanceReport(**incremental_stream_config),
                    DisplayKeywordPerformanceReport(**incremental_stream_config),
                    ShoppingPerformanceReport(**incremental_stream_config),
                    AdGroupAdReport(**incremental_stream_config),
                    GeographicReport(**incremental_stream_config),
                    KeywordReport(**incremental_stream_config),
                ]
            )
        return streams

    def _read_incremental(
        self,
        logger: AirbyteLogger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        connector_state: MutableMapping[str, Any],
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        stream_name = configured_stream.stream.name
        stream_state = connector_state.get(stream_name, {})
        if stream_state:
            logger.info(f"Setting state of {stream_name} stream to {stream_state}")

        for _ in range(4):
            """
            Initial _range_days = 15
            If `page token has expired` reduce date range twice each time, 
            so it tries to use the following date ranges: 15, 7, 3, 1
            """
            slices = stream_instance.stream_slices(
                cursor_field=configured_stream.cursor_field, sync_mode=SyncMode.incremental, stream_state=stream_state
            )
            total_records_counter = 0
            for slice in slices:
                records = stream_instance.read_records(
                    sync_mode=SyncMode.incremental,
                    stream_slice=slice,
                    stream_state=stream_state,
                    cursor_field=configured_stream.cursor_field or None,
                )
                try:
                    for record_counter, record_data in enumerate(records, start=1):
                        yield self._as_airbyte_record(stream_name, record_data)
                        stream_state = stream_instance.get_updated_state(stream_state, record_data)
                        checkpoint_interval = stream_instance.state_checkpoint_interval
                        if checkpoint_interval and record_counter % checkpoint_interval == 0:
                            yield self._checkpoint_state(stream_name, stream_state, connector_state, logger)

                        total_records_counter += 1
                        # This functionality should ideally live outside of this method
                        # but since state is managed inside this method, we keep track
                        # of it here.
                        if self._limit_reached(internal_config, total_records_counter):
                            # Break from slice loop to save state and exit from _read_incremental function.
                            break

                    yield self._checkpoint_state(stream_name, stream_state, connector_state, logger)
                    if self._limit_reached(internal_config, total_records_counter):
                        return
                except GoogleAdsException as e:
                    if e.failure._pb.errors[0].error_code.request_error == 8:
                        # page token has expired, reduce range days twice (EXPIRED_PAGE_TOKEN = 8)
                        if stream_instance.range_days == 1:
                            # If range days is 1, no need in retry, because it's the minimum date range
                            raise e
                        stream_instance.range_days = stream_instance.range_days // 2
                        logger.info(f"Page token has expired. Date range was reduced to {stream_instance.range_days}")
                        break
                    raise e
            else:
                """If exits the internal loop normally return the control"""
                return
