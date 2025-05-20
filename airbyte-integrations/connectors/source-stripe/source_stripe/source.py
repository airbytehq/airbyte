#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, List, Mapping, MutableMapping, Optional, Tuple

import pendulum

from airbyte_cdk.entrypoint import logger as entrypoint_logger
from airbyte_cdk.models import ConfiguredAirbyteCatalog, FailureType, SyncMode
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.message.repository import InMemoryMessageRepository
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.call_rate import AbstractAPIBudget, HttpAPIBudget, HttpRequestMatcher, MovingWindowCallRatePolicy, Rate
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor, CursorField, FinalStateCursor
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import EpochValueConcurrentStreamStateConverter
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from source_stripe.streams import (
    CreatedCursorIncrementalStripeStream,
    IncrementalStripeStream,
    ParentIncrementalStripeSubStream,
    SetupAttempts,
    StripeLazySubStream,
    StripeStream,
    StripeSubStream,
    UpdatedCursorIncrementalStripeLazySubStream,
    UpdatedCursorIncrementalStripeStream,
    UpdatedCursorIncrementalStripeSubStream,
)


logger = logging.getLogger("airbyte")

_MAX_CONCURRENCY = 20
_DEFAULT_CONCURRENCY = 10
_CACHE_DISABLED = os.environ.get("CACHE_DISABLED")
USE_CACHE = not _CACHE_DISABLED
STRIPE_TEST_ACCOUNT_PREFIX = "sk_test_"


class SourceStripe(YamlDeclarativeSource):
    _SLICE_BOUNDARY_FIELDS_BY_IMPLEMENTATION = {
        CreatedCursorIncrementalStripeStream: ("created[gte]", "created[lte]"),
    }

    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})
        self._state = state
        if catalog:
            self._streams_configured_as_full_refresh = {
                configured_stream.stream.name
                for configured_stream in catalog.streams
                if configured_stream.sync_mode == SyncMode.full_refresh
            }
        else:
            # things will NOT be executed concurrently
            self._streams_configured_as_full_refresh = set()

    # TODO: Remove this. This property is necessary to safely migrate Stripe during the transition state.
    @property
    def is_partially_declarative(self) -> bool:
        return True

    @staticmethod
    def validate_and_fill_with_defaults(config: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        lookback_window_days, slice_range = (
            config.get("lookback_window_days"),
            config.get("slice_range"),
        )
        if lookback_window_days is None:
            config["lookback_window_days"] = 0
        elif not isinstance(lookback_window_days, int) or lookback_window_days < 0:
            message = f"Invalid lookback window {lookback_window_days}. Please use only positive integer values or 0."
            raise AirbyteTracedException(
                message=message,
                internal_message=message,
                failure_type=FailureType.config_error,
            )

        # verifies the start_date in the config is valid
        SourceStripe._start_date_to_timestamp(config)
        if slice_range is None:
            config["slice_range"] = 365
        elif not isinstance(slice_range, int) or slice_range < 1:
            message = f"Invalid slice range value {slice_range}. Please use positive integer values only."
            raise AirbyteTracedException(
                message=message,
                internal_message=message,
                failure_type=FailureType.config_error,
            )
        return config

    def check_connection(self, logger: logging.Logger, config: MutableMapping[str, Any]) -> Tuple[bool, Any]:
        args = self._get_stream_base_args(config)
        account_stream = StripeStream(name="accounts", path="accounts", use_cache=USE_CACHE, **args)
        try:
            next(account_stream.read_records(sync_mode=SyncMode.full_refresh), None)
        except AirbyteTracedException as error:
            if error.failure_type == FailureType.config_error:
                return False, error.message
            raise error
        return True, None

    def _get_stream_base_args(self, config: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        config = self.validate_and_fill_with_defaults(config)
        authenticator = TokenAuthenticator(config["client_secret"])
        start_timestamp = self._start_date_to_timestamp(config)
        args = {
            "authenticator": authenticator,
            "account_id": config["account_id"],
            "start_date": start_timestamp,
            "slice_range": config["slice_range"],
            "api_budget": self.get_api_call_budget(config),
        }
        return args

    @staticmethod
    def customers(**args):
        # The Customers stream is instantiated in a dedicated method to allow parametrization and avoid duplicated code.
        # It can be used with and without expanded items (as an independent stream or as a parent stream for other streams).
        return IncrementalStripeStream(
            name="customers",
            path="customers",
            use_cache=USE_CACHE,
            event_types=["customer.created", "customer.updated", "customer.deleted"],
            **args,
        )

    @staticmethod
    def is_test_account(config: Mapping[str, Any]) -> bool:
        """Check if configuration uses Stripe test account (https://stripe.com/docs/keys#obtain-api-keys)

        :param config:
        :return: True if configured to use a test account, False - otherwise
        """

        return str(config["client_secret"]).startswith(STRIPE_TEST_ACCOUNT_PREFIX)

    def get_api_call_budget(self, config: Mapping[str, Any]) -> AbstractAPIBudget:
        """Get API call budget which connector is allowed to use.

        :param config:
        :return:
        """

        max_call_rate = 25 if self.is_test_account(config) else 100
        if config.get("call_rate_limit"):
            call_limit = config["call_rate_limit"]
            if call_limit > max_call_rate:
                logger.warning(
                    "call_rate_limit is larger than maximum allowed %s, fallback to default %s.",
                    max_call_rate,
                    max_call_rate,
                )
                call_limit = max_call_rate
        else:
            call_limit = max_call_rate

        policies = [
            MovingWindowCallRatePolicy(
                rates=[Rate(limit=20, interval=timedelta(seconds=1))],
                matchers=[
                    HttpRequestMatcher(url="https://api.stripe.com/v1/files"),
                    HttpRequestMatcher(url="https://api.stripe.com/v1/file_links"),
                ],
            ),
            MovingWindowCallRatePolicy(
                rates=[Rate(limit=call_limit, interval=timedelta(seconds=1))],
                matchers=[],
            ),
        ]

        return HttpAPIBudget(policies=policies)

    def streams(self, config: MutableMapping[str, Any]) -> List[Stream]:
        args = self._get_stream_base_args(config)
        incremental_args = {**args, "lookback_window_days": config["lookback_window_days"]}
        subscriptions = IncrementalStripeStream(
            name="subscriptions",
            path="subscriptions",
            use_cache=USE_CACHE,
            extra_request_params={"status": "all"},
            event_types=[
                "customer.subscription.created",
                "customer.subscription.paused",
                "customer.subscription.pending_update_applied",
                "customer.subscription.pending_update_expired",
                "customer.subscription.resumed",
                "customer.subscription.trial_will_end",
                "customer.subscription.updated",
                "customer.subscription.deleted",
            ],
            **args,
        )
        subscription_items = UpdatedCursorIncrementalStripeLazySubStream(
            name="subscription_items",
            path="subscription_items",
            parent=subscriptions,
            extra_request_params=lambda self, stream_slice, *args, **kwargs: {"subscription": stream_slice["parent"]["id"]},
            slice_data_retriever=lambda record, stream_slice: {
                **record,
                "subscription_updated": stream_slice["parent"]["updated"],
            },
            cursor_field="subscription_updated",
            use_cache=USE_CACHE,
            sub_items_attr="items",
            event_types=["customer.subscription.created", "customer.subscription.updated"],
            **args,
        )
        transfers = IncrementalStripeStream(
            name="transfers",
            path="transfers",
            use_cache=USE_CACHE,
            event_types=["transfer.created", "transfer.reversed", "transfer.updated"],
            **args,
        )
        application_fees = IncrementalStripeStream(
            name="application_fees",
            path="application_fees",
            use_cache=USE_CACHE,
            event_types=["application_fee.created", "application_fee.refunded"],
            **args,
        )
        invoices = IncrementalStripeStream(
            name="invoices",
            path="invoices",
            use_cache=USE_CACHE,
            expand_items=["data.discounts", "data.total_tax_amounts.tax_rate"],
            event_types=[
                "invoice.created",
                "invoice.deleted",
                "invoice.finalization_failed",
                "invoice.finalized",
                "invoice.marked_uncollectible",
                "invoice.overdue",
                "invoice.paid",
                "invoice.payment_action_required",
                "invoice.payment_failed",
                "invoice.payment_succeeded",
                "invoice.sent",
                "invoice.updated",
                "invoice.voided",
                "invoice.will_be_due",
                # the event type = "invoice.upcoming" doesn't contain the `primary_key = `id` field,
                # thus isn't used, see the doc: https://docs.stripe.com/api/invoices/object#invoice_object-id
                # reference issue: https://github.com/airbytehq/oncall/issues/5560
            ],
            **args,
        )
        checkout_sessions = UpdatedCursorIncrementalStripeStream(
            name="checkout_sessions",
            path="checkout/sessions",
            use_cache=USE_CACHE,
            legacy_cursor_field="created",
            event_types=[
                "checkout.session.async_payment_failed",
                "checkout.session.async_payment_succeeded",
                "checkout.session.completed",
                "checkout.session.expired",
            ],
            **args,
        )

        payouts = IncrementalStripeStream(
            name="payouts",
            path="payouts",
            event_types=[
                "payout.canceled",
                "payout.created",
                "payout.failed",
                "payout.paid",
                "payout.reconciliation_completed",
                "payout.updated",
            ],
            **args,
        )

        # TODO: Remove all Python connector-related implementations once this issue is resolved –
        #  https://github.com/airbytehq/oncall/issues/7876

        streams = [
            UpdatedCursorIncrementalStripeLazySubStream(
                name="invoice_line_items",
                path=lambda self, stream_slice, *args, **kwargs: f"invoices/{stream_slice['parent']['id']}/lines",
                parent=invoices,
                cursor_field="invoice_updated",
                event_types=[
                    "invoice.created",
                    "invoice.deleted",
                    "invoice.updated",
                    # the event type = "invoice.upcoming" doesn't contain the `primary_key = `id` field,
                    # thus isn't used, see the doc: https://docs.stripe.com/api/invoices/object#invoice_object-id
                    # reference issue: https://github.com/airbytehq/oncall/issues/5560
                ],
                sub_items_attr="lines",
                slice_data_retriever=lambda record, stream_slice: {
                    "invoice_id": stream_slice["parent"]["id"],
                    "invoice_created": stream_slice["parent"]["created"],
                    "invoice_updated": stream_slice["parent"]["updated"],
                    **record,
                },
                **args,
            )
        ]

        state_manager = ConnectorStateManager(state=self._state)
        return super().streams(config=config) + [
            self._to_concurrent(
                stream,
                datetime.fromtimestamp(self._start_date_to_timestamp(config), timezone.utc),
                timedelta(days=config["slice_range"]),
                state_manager,
            )
            for stream in streams
        ]

    def _to_concurrent(
        self, stream: Stream, fallback_start: datetime, slice_range: timedelta, state_manager: ConnectorStateManager
    ) -> Stream:
        if stream.name in self._streams_configured_as_full_refresh:
            return StreamFacade.create_from_stream(
                stream,
                self,
                entrypoint_logger,
                self._create_empty_state(),
                FinalStateCursor(stream_name=stream.name, stream_namespace=stream.namespace, message_repository=self.message_repository),
            )

        state = state_manager.get_stream_state(stream.name, stream.namespace)
        slice_boundary_fields = self._SLICE_BOUNDARY_FIELDS_BY_IMPLEMENTATION.get(type(stream))
        if slice_boundary_fields:
            cursor_field = CursorField(stream.cursor_field) if isinstance(stream.cursor_field, str) else CursorField(stream.cursor_field[0])
            converter = EpochValueConcurrentStreamStateConverter()
            cursor = ConcurrentCursor(
                stream.name,
                stream.namespace,
                state_manager.get_stream_state(stream.name, stream.namespace),
                self.message_repository,
                state_manager,
                converter,
                cursor_field,
                slice_boundary_fields,
                fallback_start,
                converter.get_end_provider(),
                timedelta(seconds=0),
                slice_range,
            )
            return StreamFacade.create_from_stream(stream, self, entrypoint_logger, state, cursor)

        return stream

    def _create_empty_state(self) -> MutableMapping[str, Any]:
        return {}

    @staticmethod
    def _start_date_to_timestamp(config: Mapping[str, Any]) -> int:
        if "start_date" not in config:
            return pendulum.datetime(2017, 1, 25).int_timestamp  # type: ignore  # pendulum not typed

        start_date = config["start_date"]
        try:
            return pendulum.parse(start_date).int_timestamp  # type: ignore  # pendulum not typed
        except pendulum.parsing.exceptions.ParserError as e:
            message = f"Invalid start date {start_date}. Please use YYYY-MM-DDTHH:MM:SSZ format."
            raise AirbyteTracedException(
                message=message,
                internal_message=message,
                failure_type=FailureType.config_error,
            ) from e
