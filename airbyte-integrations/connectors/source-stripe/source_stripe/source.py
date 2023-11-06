#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import stripe
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.entrypoint import logger as entrypoint_logger
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.message.repository import InMemoryMessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import NoopCursor
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from source_stripe.streams import (
    CheckoutSessionsLineItems,
    CreatedCursorIncrementalStripeStream,
    CustomerBalanceTransactions,
    Events,
    FilteringRecordExtractor,
    IncrementalStripeStream,
    Persons,
    SetupAttempts,
    StripeLazySubStream,
    StripeStream,
    StripeSubStream,
    UpdatedCursorIncrementalStripeLazySubStream,
    UpdatedCursorIncrementalStripeStream,
)

_MAX_CONCURRENCY = 3


class SourceStripe(AbstractSource):
    def __init__(self, catalog_path: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if catalog_path:
            catalog = self.read_catalog(catalog_path)
            # Only use concurrent cdk if all streams are running in full_refresh
            all_sync_mode_are_full_refresh = all(stream.sync_mode == SyncMode.full_refresh for stream in catalog.streams)
            self._use_concurrent_cdk = all_sync_mode_are_full_refresh
        else:
            self._use_concurrent_cdk = False

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

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.validate_and_fill_with_defaults(config)
        authenticator = TokenAuthenticator(config["client_secret"])
        args = {
            "authenticator": authenticator,
            "account_id": config["account_id"],
            "start_date": config["start_date"],
            "slice_range": config["slice_range"],
        }
        incremental_args = {**args, "lookback_window_days": config["lookback_window_days"]}
        subscriptions = IncrementalStripeStream(
            name="subscriptions",
            path="subscriptions",
            use_cache=True,
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
            extra_request_params=lambda self, *args, stream_slice, **kwargs: {"subscription": stream_slice[self.parent_id]},
            parent=subscriptions,
            use_cache=True,
            parent_id="subscription_id",
            sub_items_attr="items",
            **args,
        )
        transfers = IncrementalStripeStream(
            name="transfers",
            path="transfers",
            use_cache=True,
            event_types=["transfer.created", "transfer.reversed", "transfer.updated"],
            **args,
        )
        application_fees = IncrementalStripeStream(
            name="application_fees",
            path="application_fees",
            use_cache=True,
            event_types=["application_fee.created", "application_fee.refunded"],
            **args,
        )
        customers = IncrementalStripeStream(
            name="customers",
            path="customers",
            use_cache=True,
            event_types=["customer.created", "customer.updated", "customer.deleted"],
            **args,
        )
        invoices = IncrementalStripeStream(
            name="invoices",
            path="invoices",
            use_cache=True,
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
        streams = [
            CheckoutSessionsLineItems(**incremental_args),
            CustomerBalanceTransactions(**args),
            Events(**incremental_args),
            UpdatedCursorIncrementalStripeStream(
                name="external_account_cards",
                path=lambda self, *args, **kwargs: f"accounts/{self.account_id}/external_accounts",
                event_types=["account.external_account.created", "account.external_account.updated", "account.external_account.deleted"],
                legacy_cursor_field=None,
                extra_request_params={"object": "card"},
                record_extractor=FilteringRecordExtractor("updated", None, "card"),
                **args,
            ),
            UpdatedCursorIncrementalStripeStream(
                name="external_account_bank_accounts",
                path=lambda self, *args, **kwargs: f"accounts/{self.account_id}/external_accounts",
                event_types=["account.external_account.created", "account.external_account.updated", "account.external_account.deleted"],
                legacy_cursor_field=None,
                extra_request_params={"object": "bank_account"},
                record_extractor=FilteringRecordExtractor("updated", None, "bank_account"),
                **args,
            ),
            Persons(**args),
            SetupAttempts(**incremental_args),
            StripeStream(name="accounts", path="accounts", use_cache=True, **args),
            CreatedCursorIncrementalStripeStream(name="shipping_rates", path="shipping_rates", **incremental_args),
            CreatedCursorIncrementalStripeStream(name="balance_transactions", path="balance_transactions", **incremental_args),
            CreatedCursorIncrementalStripeStream(name="files", path="files", **incremental_args),
            CreatedCursorIncrementalStripeStream(name="file_links", path="file_links", **incremental_args),
            UpdatedCursorIncrementalStripeStream(
                name="checkout_sessions",
                path="checkout/sessions",
                use_cache=True,
                legacy_cursor_field="expires_at",
                event_types=[
                    "checkout.session.async_payment_failed",
                    "checkout.session.async_payment_succeeded",
                    "checkout.session.completed",
                    "checkout.session.expired",
                ],
                **args,
            ),
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
            customers,
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
                name="refunds", path="refunds", use_cache=True, event_types=["refund.created", "refund.updated"], **args
            ),
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
                path=lambda self, stream_slice, *args, **kwargs: f"application_fees/{stream_slice[self.parent_id]}/refunds",
                parent=application_fees,
                event_types=["application_fee.refund.updated"],
                parent_id="refund_id",
                sub_items_attr="refunds",
                add_parent_id=True,
                **args,
            ),
            UpdatedCursorIncrementalStripeLazySubStream(
                name="bank_accounts",
                path=lambda self, stream_slice, *args, **kwargs: f"customers/{stream_slice[self.parent_id]}/sources",
                parent=customers,
                event_types=["customer.source.created", "customer.source.expiring", "customer.source.updated", "customer.source.deleted"],
                legacy_cursor_field=None,
                parent_id="customer_id",
                sub_items_attr="sources",
                response_filter={"attr": "object", "value": "bank_account"},
                extra_request_params={"object": "bank_account"},
                record_extractor=FilteringRecordExtractor("updated", None, "bank_account"),
                **args,
            ),
            StripeLazySubStream(
                name="invoice_line_items",
                path=lambda self, *args, stream_slice, **kwargs: f"invoices/{stream_slice[self.parent_id]}/lines",
                parent=invoices,
                parent_id="invoice_id",
                sub_items_attr="lines",
                add_parent_id=True,
                **args,
            ),
            subscription_items,
            StripeSubStream(
                name="transfer_reversals",
                path=lambda self, stream_slice, *args, **kwargs: f"transfers/{stream_slice.get('parent', {}).get('id')}/reversals",
                parent=transfers,
                **args,
            ),
            StripeSubStream(
                name="usage_records",
                path=lambda self, stream_slice, *args, **kwargs: f"subscription_items/{stream_slice.get('parent', {}).get('id')}/usage_record_summaries",
                parent=subscription_items,
                primary_key=None,
                **args,
            ),
        ]
        if self._use_concurrent_cdk:
            # We cap the number of workers to avoid hitting the Stripe rate limit
            # The limit can be removed or increased once we have proper rate limiting
            concurrency_level = min(config.get("num_workers", 2), _MAX_CONCURRENCY)
            streams[0].logger.info(f"Using concurrent cdk with concurrency level {concurrency_level}")

            # The state is known to be empty because concurrent CDK is currently only used for full refresh
            state = {}
            cursor = NoopCursor()
            return [
                StreamFacade.create_from_stream(stream, self, entrypoint_logger, concurrency_level, state, cursor) for stream in streams
            ]
        else:
            return streams
