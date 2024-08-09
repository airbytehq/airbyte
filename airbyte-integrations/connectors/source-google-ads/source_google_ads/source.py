#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import copy
import datetime
import functools
import logging
import operator
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import CursorField, FinalStateCursor
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import ConfiguredAirbyteCatalog
from pendulum import duration, parse, today
from pendulum.parsing import ParserError

from .custom_query_stream import CustomQuery, IncrementalCustomQuery
from .google_ads import GoogleAds
from .google_cursor import GoogleAdsCursor
from .models import CustomerModel
from .state_converter import GadsStateConverter
from .streams import (
    AccountPerformanceReport,
    AdGroup,
    AdGroupAd,
    AdGroupAdLabel,
    AdGroupAdLegacy,
    AdGroupBiddingStrategy,
    AdGroupCriterion,
    AdGroupCriterionLabel,
    AdGroupLabel,
    AdListingGroupCriterion,
    Audience,
    Campaign,
    CampaignBiddingStrategy,
    CampaignBudget,
    CampaignCriterion,
    CampaignLabel,
    ClickView,
    Customer,
    CustomerClient,
    CustomerLabel,
    DisplayKeywordView,
    GeographicView,
    KeywordView,
    Label,
    ShoppingPerformanceView,
    TopicView,
    UserInterest,
    UserLocationView,
)
from .utils import GAQL, logger, traced_exception

_MAX_CONCURRENCY = 20
_DEFAULT_CONCURRENCY = 10


class SourceGoogleAds(ConcurrentSourceAdapter):
    message_repository = InMemoryMessageRepository(logger.level)
    # Skip exceptions on missing streams
    raise_exception_on_missing_stream = False

    def __init__(
        self, catalog: Optional[ConfiguredAirbyteCatalog] = None, config: Optional[Mapping[str, Any]] = None, state: TState = None, **kwargs
    ):
        if config:
            concurrency_level = min(config.get("num_workers", _DEFAULT_CONCURRENCY), _MAX_CONCURRENCY)
        else:
            concurrency_level = _DEFAULT_CONCURRENCY
        logger.info(f"Using concurrent cdk with concurrency level {concurrency_level}")
        concurrent_source = ConcurrentSource.create(
            concurrency_level, concurrency_level // 2, logger, self._slice_logger, self.message_repository
        )
        super().__init__(concurrent_source)
        self.catalog = catalog
        self.state = state

    @staticmethod
    def _validate_and_transform(config: MutableMapping[str, Any]):
        config = copy.deepcopy(config)
        if config.get("end_date") == "":
            config.pop("end_date")
        for query in config.get("custom_queries_array", []):
            try:
                query["query"] = GAQL.parse(query["query"])
            except ValueError:
                message = (
                    f"The custom GAQL query {query['table_name']} failed. Validate your GAQL query with the Google Ads query validator. "
                    "https://developers.google.com/google-ads/api/fields/v15/query_validator"
                )
                raise AirbyteTracedException(message=message, failure_type=FailureType.config_error)

        if "customer_id" in config:
            config["customer_ids"] = config["customer_id"].split(",")
            config.pop("customer_id")

        return config

    @staticmethod
    def get_credentials(config: Mapping[str, Any]) -> MutableMapping[str, Any]:
        credentials = config["credentials"]
        # use_proto_plus is set to True, because setting to False returned wrong value types, which breaks the backward compatibility.
        # For more info read the related PR's description: https://github.com/airbytehq/airbyte/pull/9996
        credentials.update(use_proto_plus=True)
        return credentials

    @staticmethod
    def get_incremental_stream_config(google_api: GoogleAds, config: Mapping[str, Any], customers: List[CustomerModel]):
        # date range is mandatory parameter for incremental streams, so default start day is used
        start_date = config.get("start_date", today().subtract(years=2).to_date_string())

        end_date = config.get("end_date")
        # check if end_date is not in the future, set to today if it is
        end_date = min(today(), parse(end_date)) if end_date else today()
        end_date = end_date.to_date_string()

        incremental_stream_config = dict(
            api=google_api,
            customers=customers,
            conversion_window_days=config.get("conversion_window_days", 0),
            start_date=start_date,
            end_date=end_date,
        )
        return incremental_stream_config

    def get_all_accounts(self, google_api: GoogleAds, customers: List[CustomerModel], customer_status_filter: List[str]) -> List[str]:
        customer_clients_stream = CustomerClient(api=google_api, customers=customers, customer_status_filter=customer_status_filter)
        for slice in customer_clients_stream.stream_slices():
            for record in customer_clients_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice):
                yield record

    def _get_all_connected_accounts(
        self, google_api: GoogleAds, customer_status_filter: List[str]
    ) -> Iterable[Iterable[Mapping[str, Any]]]:
        customer_ids = [customer_id for customer_id in google_api.get_accessible_accounts()]
        dummy_customers = [CustomerModel(id=_id, login_customer_id=_id) for _id in customer_ids]

        yield from self.get_all_accounts(google_api, dummy_customers, customer_status_filter)

    def get_customers(self, google_api: GoogleAds, config: Mapping[str, Any]) -> List[CustomerModel]:
        customer_status_filter = config.get("customer_status_filter", [])
        accounts = self._get_all_connected_accounts(google_api, customer_status_filter)
        customers = CustomerModel.from_accounts(accounts)

        # filter duplicates as one customer can be accessible from mutiple connected accounts
        unique_customers = []
        seen_ids = set()
        for customer in customers:
            if customer.id in seen_ids:
                continue
            seen_ids.add(customer.id)
            unique_customers.append(customer)
        customers = unique_customers
        customers_dict = {customer.id: customer for customer in customers}

        # filter only selected accounts
        if config.get("customer_ids"):
            customers = []
            for customer_id in config["customer_ids"]:
                if customer_id not in customers_dict:
                    logging.warning(f"Customer with id {customer_id} is not accessible. Skipping it.")
                else:
                    customers.append(customers_dict[customer_id])
        return customers

    @staticmethod
    def is_metrics_in_custom_query(query: GAQL) -> bool:
        for field in query.fields:
            if field.split(".")[0] == "metrics":
                return True
        return False

    @staticmethod
    def is_custom_query_incremental(query: GAQL) -> bool:
        time_segment_in_select, time_segment_in_where = ["segments.date" in clause for clause in [query.fields, query.where]]
        return time_segment_in_select and not time_segment_in_where

    @staticmethod
    def set_retention_period_and_slice_duration(stream: IncrementalCustomQuery, query: GAQL) -> IncrementalCustomQuery:
        if query.resource_name == "click_view":
            stream.days_of_data_storage = 90
            stream.slice_duration = duration(days=0)
        return stream

    def create_custom_query_stream(
        self,
        google_api: GoogleAds,
        single_query_config: Mapping[str, Any],
        customers: List[CustomerModel],
        non_manager_accounts: List[CustomerModel],
        incremental_config: Mapping[str, Any],
        non_manager_incremental_config: Mapping[str, Any],
    ):
        query = single_query_config["query"]
        is_incremental = self.is_custom_query_incremental(query)
        is_non_manager = self.is_metrics_in_custom_query(query)

        if is_non_manager:
            # Skip query with metrics if there are no non-manager accounts
            if not non_manager_accounts:
                return

            customers = non_manager_accounts
            incremental_config = non_manager_incremental_config

        if is_incremental:
            incremental_query_stream = IncrementalCustomQuery(config=single_query_config, **incremental_config)
            return self.set_retention_period_and_slice_duration(incremental_query_stream, query)
        else:
            return CustomQuery(config=single_query_config, api=google_api, customers=customers)

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        config = self._validate_and_transform(config)

        logger.info("Checking the config")
        google_api = GoogleAds(credentials=self.get_credentials(config))

        customers = self.get_customers(google_api, config)
        logger.info(f"Found {len(customers)} customers: {[customer.id for customer in customers]}")

        # Check custom query request validity by sending metric request with non-existent time window
        for query in config.get("custom_queries_array", []):
            for customer in customers:
                table_name = query["table_name"]
                query = query["query"]
                if customer.is_manager_account and self.is_metrics_in_custom_query(query):
                    logger.warning(
                        f"Metrics are not available for manager account {customer.id}. "
                        f'Skipping the custom query: "{query}" for manager account.'
                    )
                    continue

                # Add segments.date to where clause of incremental custom queries if they are not present.
                # The same will be done during read, but with start and end date from config.
                if self.is_custom_query_incremental(query):
                    # Set default date value 1 month ago, as some tables have a limited lookback time frame.
                    month_back = today().subtract(months=1).to_date_string()
                    start_date = config.get("start_date", month_back)

                    query_date = month_back if start_date > month_back else start_date

                    query = IncrementalCustomQuery.insert_segments_date_expr(query, query_date, query_date)

                query = query.set_limit(1)
                try:
                    logger.info(f"Running the query for account {customer.id}: {query}")
                    response = google_api.send_request(
                        str(query),
                        customer_id=customer.id,
                        login_customer_id=customer.login_customer_id,
                    )
                except AirbyteTracedException as e:
                    raise e from e
                except Exception as exc:
                    traced_exception(exc, customer.id, False, table_name)
                # iterate over the response otherwise exceptions will not be raised!
                for _ in response:
                    pass
                break
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self._validate_and_transform(config)
        google_api = GoogleAds(credentials=self.get_credentials(config))

        customers = self.get_customers(google_api, config)
        logger.info(f"Found {len(customers)} customers: {[customer.id for customer in customers]}")

        non_manager_accounts = [customer for customer in customers if not customer.is_manager_account]
        default_config = dict(api=google_api, customers=customers)
        incremental_config = self.get_incremental_stream_config(google_api, config, customers)
        non_manager_incremental_config = self.get_incremental_stream_config(google_api, config, non_manager_accounts)
        streams = [
            AdGroup(**incremental_config),
            AdGroupAd(**incremental_config),
            AdGroupAdLabel(**default_config),
            AdGroupBiddingStrategy(**incremental_config),
            AdGroupCriterion(**default_config),
            AdGroupCriterionLabel(**default_config),
            AdGroupLabel(**default_config),
            AdListingGroupCriterion(**default_config),
            Audience(**default_config),
            CampaignBiddingStrategy(**incremental_config),
            CampaignCriterion(**default_config),
            CampaignLabel(google_api, customers=customers),
            ClickView(**incremental_config),
            Customer(**incremental_config),
            CustomerLabel(**default_config),
            Label(**default_config),
            UserInterest(**default_config),
        ]
        # Metrics streams cannot be requested for a manager account.
        if non_manager_accounts:
            streams.extend(
                [
                    Campaign(**non_manager_incremental_config),
                    CampaignBudget(**non_manager_incremental_config),
                    UserLocationView(**non_manager_incremental_config),
                    AccountPerformanceReport(**non_manager_incremental_config),
                    TopicView(**non_manager_incremental_config),
                    DisplayKeywordView(**non_manager_incremental_config),
                    ShoppingPerformanceView(**non_manager_incremental_config),
                    AdGroupAdLegacy(**non_manager_incremental_config),
                    GeographicView(**non_manager_incremental_config),
                    KeywordView(**non_manager_incremental_config),
                ]
            )
        concurrent_streams = []
        for single_query_config in config.get("custom_queries_array", []):
            query_stream = self.create_custom_query_stream(
                google_api, single_query_config, customers, non_manager_accounts, incremental_config, non_manager_incremental_config
            )
            if query_stream:
                concurrent_streams.append(query_stream)

        state_manager = ConnectorStateManager(stream_instance_map={s.name: s for s in concurrent_streams}, state=self.state)
        for stream in concurrent_streams:
            streams.append(self._to_concurrent(stream, self._start_date_to_date(config), state_manager, customers))
        return streams

    def _get_sync_mode_from_catalog(self, stream: Stream) -> Optional[SyncMode]:
        if self.catalog:
            for catalog_stream in self.catalog.streams:
                if stream.name == catalog_stream.stream.name:
                    return catalog_stream.sync_mode
        return None

    def _to_concurrent(
        self, stream: Stream, fallback_start, state_manager: ConnectorStateManager, customers: list[CustomerModel]
    ) -> Stream:
        sync_mode = self._get_sync_mode_from_catalog(stream)
        if sync_mode == SyncMode.full_refresh:
            return StreamFacade.create_from_stream(
                stream,
                self,
                logger,
                {},
                FinalStateCursor(stream_name=stream.name, stream_namespace=stream.namespace, message_repository=self.message_repository),
            )
        if len(stream.cursor_field) == 0:
            return stream
        state = state_manager.get_stream_state(stream.name, stream.namespace)

        cursor_field = CursorField(stream.cursor_field) if isinstance(stream.cursor_field, str) else CursorField(stream.cursor_field[0])
        converter = GadsStateConverter(customers=customers)
        cursor = GoogleAdsCursor(
            stream.name,
            stream.namespace,
            state_manager.get_stream_state(stream.name, stream.namespace),
            self.message_repository,
            state_manager,
            converter,
            cursor_field,
            ("start_date", "end_date"),
            fallback_start,
            converter.get_end_provider(),
        )
        return StreamFacade.create_from_stream(stream, self, logger, state, cursor)

    @staticmethod
    def _start_date_to_date(config: Mapping[str, Any]) -> datetime.date:
        if "start_date" not in config:
            return pendulum.datetime(2017, 1, 25).date()  # type: ignore  # pendulum not typed

        start_date = config["start_date"]
        try:
            return parse(start_date).date()  # type: ignore  # pendulum not typed
        except ParserError as e:
            message = f"Invalid start date {start_date}. Please use YYYY-MM-DD format."
            raise AirbyteTracedException(
                message=message,
                internal_message=message,
                failure_type=FailureType.config_error,
            ) from e
