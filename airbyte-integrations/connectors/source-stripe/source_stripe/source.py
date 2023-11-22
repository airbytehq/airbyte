#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import os
from datetime import timedelta
from typing import Any, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import stripe
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.entrypoint import logger as entrypoint_logger
from airbyte_cdk.models import ConfiguredAirbyteCatalog, FailureType
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.message.repository import InMemoryMessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.call_rate import AbstractAPIBudget, HttpAPIBudget, HttpRequestMatcher, MovingWindowCallRatePolicy, Rate
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import NoopCursor
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from airbyte_protocol.models import SyncMode
from source_stripe.streams import (
    CreatedCursorIncrementalStripeStream,
    CustomerBalanceTransactions,
    Events,
    IncrementalStripeStream,
    ParentIncrementalStipeSubStream,
    Persons,
    SetupAttempts,
    StripeLazySubStream,
    StripeStream,
    StripeSubStream,
    UpdatedCursorIncrementalStripeLazySubStream,
    UpdatedCursorIncrementalStripeStream,
)

logger = logging.getLogger("airbyte")

_MAX_CONCURRENCY = 20
_CACHE_DISABLED = os.environ.get("CACHE_DISABLED")
USE_CACHE = not _CACHE_DISABLED
STRIPE_TEST_ACCOUNT_PREFIX = "sk_test_"


class SourceStripe(AbstractSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], **kwargs):
        super().__init__(**kwargs)
        if catalog:
            self._streams_configured_as_full_refresh = {
                configured_stream.stream.name
                for configured_stream in catalog.streams
                if configured_stream.sync_mode == SyncMode.full_refresh
            }
        else:
            # things will NOT be executed concurrently
            self._streams_configured_as_full_refresh = set()

    message_repository = InMemoryMessageRepository(entrypoint_logger.level)

    @staticmethod
    def validate_and_fill_with_defaults(config: MutableMapping) -> MutableMapping:
        start_date, lookback_window_days, slice_range = (
            config.get("start_date"),
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
        if start_date:
            try:
                start_date = pendulum.parse(start_date).int_timestamp
            except pendulum.parsing.exceptions.ParserError as e:
                message = f"Invalid start date {start_date}. Please use YYYY-MM-DDTHH:MM:SSZ format."
                raise AirbyteTracedException(
                    message=message,
                    internal_message=message,
                    failure_type=FailureType.config_error,
                ) from e
        else:
            start_date = pendulum.datetime(2017, 1, 25).int_timestamp
        config["start_date"] = start_date
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

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        self.validate_and_fill_with_defaults(config)
        stripe.api_key = config["client_secret"]
        try:
            stripe.Account.retrieve(config["account_id"])
        except (stripe.error.AuthenticationError, stripe.error.PermissionError) as e:
            return False, str(e)
        return True, None

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

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.validate_and_fill_with_defaults(config)
        authenticator = TokenAuthenticator(config["client_secret"])
        args = {
            "authenticator": authenticator,
            "account_id": config["account_id"],
            "start_date": config["start_date"],
            "slice_range": config["slice_range"],
            "api_budget": self.get_api_call_budget(config),
        }
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
        subscription_items = StripeLazySubStream(
            name="subscription_items",
            path="subscription_items",
            extra_request_params=lambda self, stream_slice, *args, **kwargs: {"subscription": stream_slice["parent"]["id"]},
            parent=subscriptions,
            use_cache=USE_CACHE,
            sub_items_attr="items",
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
            event_types=[
                "invoice.created",
                "invoice.finalization_failed",
                "invoice.finalized",
                "invoice.marked_uncollectible",
                "invoice.paid",
                "invoice.payment_action_required",
                "invoice.payment_failed",
                "invoice.payment_succeeded",
                "invoice.sent",
                "invoice.updated",
                "invoice.voided",
                "invoice.deleted",
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

        streams = [
            checkout_sessions,
            CustomerBalanceTransactions(**args),
            Events(**incremental_args),
            UpdatedCursorIncrementalStripeStream(
                name="external_account_cards",
                path=lambda self, *args, **kwargs: f"accounts/{self.account_id}/external_accounts",
                event_types=["account.external_account.created", "account.external_account.updated", "account.external_account.deleted"],
                legacy_cursor_field=None,
                extra_request_params={"object": "card"},
                response_filter=lambda record: record["object"] == "card",
                **args,
            ),
            UpdatedCursorIncrementalStripeStream(
                name="external_account_bank_accounts",
                path=lambda self, *args, **kwargs: f"accounts/{self.account_id}/external_accounts",
                event_types=["account.external_account.created", "account.external_account.updated", "account.external_account.deleted"],
                legacy_cursor_field=None,
                extra_request_params={"object": "bank_account"},
                response_filter=lambda record: record["object"] == "bank_account",
                **args,
            ),
            Persons(**args),
            SetupAttempts(**incremental_args),
            StripeStream(name="accounts", path="accounts", use_cache=USE_CACHE, **args),
            CreatedCursorIncrementalStripeStream(name="shipping_rates", path="shipping_rates", **incremental_args),
            CreatedCursorIncrementalStripeStream(name="balance_transactions", path="balance_transactions", **incremental_args),
            CreatedCursorIncrementalStripeStream(name="files", path="files", **incremental_args),
            CreatedCursorIncrementalStripeStream(name="file_links", path="file_links", **incremental_args),
            # The Refunds stream does not utilize the Events API as it created issues with data loss during the incremental syncs.
            # Therefore, we're using the regular API with the `created` cursor field. A bug has been filed with Stripe.
            # See more at https://github.com/airbytehq/oncall/issues/3090, https://github.com/airbytehq/oncall/issues/3428
            CreatedCursorIncrementalStripeStream(name="refunds", path="refunds", **incremental_args),
            UpdatedCursorIncrementalStripeStream(
                name="payment_methods",
                path="payment_methods",
                event_types=[
                    "payment_method.attached",
                    "payment_method.automatically_updated",
                    "payment_method.detached",
                    "payment_method.updated",
                ],
                **args,
            ),
            UpdatedCursorIncrementalStripeStream(
                name="credit_notes",
                path="credit_notes",
                event_types=["credit_note.created", "credit_note.updated", "credit_note.voided"],
                **args,
            ),
            UpdatedCursorIncrementalStripeStream(
                name="early_fraud_warnings",
                path="radar/early_fraud_warnings",
                event_types=["radar.early_fraud_warning.created", "radar.early_fraud_warning.updated"],
                **args,
            ),
            IncrementalStripeStream(
                name="authorizations",
                path="issuing/authorizations",
                event_types=["issuing_authorization.created", "issuing_authorization.request", "issuing_authorization.updated"],
                **args,
            ),
            self.customers(**args),
            IncrementalStripeStream(
                name="cardholders",
                path="issuing/cardholders",
                event_types=["issuing_cardholder.created", "issuing_cardholder.updated"],
                **args,
            ),
            IncrementalStripeStream(
                name="charges",
                path="charges",
                expand_items=["data.refunds"],
                event_types=[
                    "charge.captured",
                    "charge.expired",
                    "charge.failed",
                    "charge.pending",
                    "charge.refunded",
                    "charge.succeeded",
                    "charge.updated",
                ],
                **args,
            ),
            IncrementalStripeStream(
                name="coupons", path="coupons", event_types=["coupon.created", "coupon.updated", "coupon.deleted"], **args
            ),
            IncrementalStripeStream(
                name="disputes",
                path="disputes",
                event_types=[
                    "charge.dispute.closed",
                    "charge.dispute.created",
                    "charge.dispute.funds_reinstated",
                    "charge.dispute.funds_withdrawn",
                    "charge.dispute.updated",
                ],
                **args,
            ),
            application_fees,
            invoices,
            IncrementalStripeStream(
                name="invoice_items",
                path="invoiceitems",
                legacy_cursor_field="date",
                event_types=["invoiceitem.created", "invoiceitem.updated", "invoiceitem.deleted"],
                **args,
            ),
            IncrementalStripeStream(
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
            ),
            IncrementalStripeStream(
                name="plans",
                path="plans",
                expand_items=["data.tiers"],
                event_types=["plan.created", "plan.updated", "plan.deleted"],
                **args,
            ),
            IncrementalStripeStream(name="prices", path="prices", event_types=["price.created", "price.updated", "price.deleted"], **args),
            IncrementalStripeStream(
                name="products", path="products", event_types=["product.created", "product.updated", "product.deleted"], **args
            ),
            IncrementalStripeStream(name="reviews", path="reviews", event_types=["review.closed", "review.opened"], **args),
            subscriptions,
            IncrementalStripeStream(
                name="subscription_schedule",
                path="subscription_schedules",
                event_types=[
                    "subscription_schedule.aborted",
                    "subscription_schedule.canceled",
                    "subscription_schedule.completed",
                    "subscription_schedule.created",
                    "subscription_schedule.expiring",
                    "subscription_schedule.released",
                    "subscription_schedule.updated",
                ],
                **args,
            ),
            transfers,
            IncrementalStripeStream(
                name="payment_intents",
                path="payment_intents",
                event_types=[
                    "payment_intent.amount_capturable_updated",
                    "payment_intent.canceled",
                    "payment_intent.created",
                    "payment_intent.partially_funded",
                    "payment_intent.payment_failed",
                    "payment_intent.processing",
                    "payment_intent.requires_action",
                    "payment_intent.succeeded",
                ],
                **args,
            ),
            IncrementalStripeStream(
                name="promotion_codes",
                path="promotion_codes",
                event_types=["promotion_code.created", "promotion_code.updated"],
                **args,
            ),
            IncrementalStripeStream(
                name="setup_intents",
                path="setup_intents",
                event_types=[
                    "setup_intent.canceled",
                    "setup_intent.created",
                    "setup_intent.requires_action",
                    "setup_intent.setup_failed",
                    "setup_intent.succeeded",
                ],
                **args,
            ),
            IncrementalStripeStream(
                name="cards", path="issuing/cards", event_types=["issuing_card.created", "issuing_card.updated"], **args
            ),
            IncrementalStripeStream(
                name="transactions",
                path="issuing/transactions",
                event_types=["issuing_transaction.created", "issuing_transaction.updated"],
                **args,
            ),
            IncrementalStripeStream(
                name="top_ups",
                path="topups",
                event_types=["topup.canceled", "topup.created", "topup.failed", "topup.reversed", "topup.succeeded"],
                **args,
            ),
            UpdatedCursorIncrementalStripeLazySubStream(
                name="application_fees_refunds",
                path=lambda self, stream_slice, *args, **kwargs: f"application_fees/{stream_slice['parent']['id']}/refunds",
                parent=application_fees,
                event_types=["application_fee.refund.updated"],
                sub_items_attr="refunds",
                **args,
            ),
            UpdatedCursorIncrementalStripeLazySubStream(
                name="bank_accounts",
                path=lambda self, stream_slice, *args, **kwargs: f"customers/{stream_slice['parent']['id']}/sources",
                parent=self.customers(expand_items=["data.sources"], **args),
                event_types=["customer.source.created", "customer.source.expiring", "customer.source.updated", "customer.source.deleted"],
                legacy_cursor_field=None,
                sub_items_attr="sources",
                extra_request_params={"object": "bank_account"},
                response_filter=lambda record: record["object"] == "bank_account",
                **args,
            ),
            ParentIncrementalStipeSubStream(
                name="checkout_sessions_line_items",
                path=lambda self, stream_slice, *args, **kwargs: f"checkout/sessions/{stream_slice['parent']['id']}/line_items",
                parent=checkout_sessions,
                expand_items=["data.discounts", "data.taxes"],
                cursor_field="checkout_session_updated",
                slice_data_retriever=lambda record, stream_slice: {
                    "checkout_session_id": stream_slice["parent"]["id"],
                    "checkout_session_expires_at": stream_slice["parent"]["expires_at"],
                    "checkout_session_created": stream_slice["parent"]["created"],
                    "checkout_session_updated": stream_slice["parent"]["updated"],
                    **record,
                },
                **args,
            ),
            StripeLazySubStream(
                name="invoice_line_items",
                path=lambda self, stream_slice, *args, **kwargs: f"invoices/{stream_slice['parent']['id']}/lines",
                parent=invoices,
                sub_items_attr="lines",
                slice_data_retriever=lambda record, stream_slice: {"invoice_id": stream_slice["parent"]["id"], **record},
                **args,
            ),
            subscription_items,
            StripeSubStream(
                name="transfer_reversals",
                path=lambda self, stream_slice, *args, **kwargs: f"transfers/{stream_slice['parent']['id']}/reversals",
                parent=transfers,
                **args,
            ),
            StripeSubStream(
                name="usage_records",
                path=lambda self, stream_slice, *args, **kwargs: f"subscription_items/{stream_slice['parent']['id']}/usage_record_summaries",
                parent=subscription_items,
                primary_key=None,
                **args,
            ),
        ]

        concurrency_level = min(config.get("num_workers", 10), _MAX_CONCURRENCY)
        streams[0].logger.info(f"Using concurrent cdk with concurrency level {concurrency_level}")

        return [
            StreamFacade.create_from_stream(stream, self, entrypoint_logger, concurrency_level, self._create_empty_state(), NoopCursor())
            if stream.name in self._streams_configured_as_full_refresh
            else stream
            for stream in streams
        ]

    def _create_empty_state(self) -> MutableMapping[str, Any]:
        # The state is known to be empty because concurrent CDK is currently only used for full refresh
        return {}
