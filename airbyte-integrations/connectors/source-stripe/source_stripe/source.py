#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import pendulum
import stripe
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
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


class SourceStripe(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            stripe.api_key = config["client_secret"]
            stripe.Account.retrieve(config["account_id"])
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(config["client_secret"])
        start_date = pendulum.parse(config["start_date"]).int_timestamp
        args = {
            "authenticator": authenticator,
            "account_id": config["account_id"],
            "start_date": start_date,
            "slice_range": config.get("slice_range"),
        }
        incremental_args = {**args, "lookback_window_days": config.get("lookback_window_days", 0)}
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
            ],
            **incremental_args,
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
            **incremental_args,
        )
        application_fees = IncrementalStripeStream(
            name="application_fees",
            path="application_fees",
            use_cache=True,
            event_types=["application_fee.created", "application_fee.refunded"],
            **incremental_args,
        )
        customers = IncrementalStripeStream(
            name="customers",
            path="customers",
            use_cache=True,
            event_types=["customer.created", "customer.updated"],
            **incremental_args,
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
                "invoice.upcoming",
                "invoice.updated",
                "invoice.voided",
            ],
            **args,
        )
        return [
            CheckoutSessionsLineItems(**incremental_args),
            CustomerBalanceTransactions(**args),
            Events(**incremental_args),
            UpdatedCursorIncrementalStripeStream(
                name="external_account_cards",
                path=lambda self, *args, **kwargs: f"accounts/{self.account_id}/external_accounts",
                event_types=["account.external_account.created", "account.external_account.updated"],
                legacy_cursor_field=None,
                extra_request_params={"object": "card"},
                record_extractor=FilteringRecordExtractor("updated", None, "card"),
                **incremental_args,
            ),
            UpdatedCursorIncrementalStripeStream(
                name="external_account_bank_accounts",
                path=lambda self, *args, **kwargs: f"accounts/{self.account_id}/external_accounts",
                event_types=["account.external_account.created", "account.external_account.updated"],
                legacy_cursor_field=None,
                extra_request_params={"object": "bank_account"},
                record_extractor=FilteringRecordExtractor("updated", None, "bank_account"),
                **incremental_args,
            ),
            Persons(**incremental_args),
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
                lookback_window_days=config.get("lookback_window_days", 0) + 1,
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
                **incremental_args,
            ),
            UpdatedCursorIncrementalStripeStream(
                name="credit_notes",
                path="credit_notes",
                event_types=["credit_note.created", "credit_note.updated", "credit_note.voided"],
                **incremental_args,
            ),
            UpdatedCursorIncrementalStripeStream(
                name="early_fraud_warnings",
                path="radar/early_fraud_warnings",
                event_types=["radar.early_fraud_warning.created", "radar.early_fraud_warning.updated"],
                **incremental_args,
            ),
            IncrementalStripeStream(
                name="authorizations",
                path="issuing/authorizations",
                event_types=["issuing_authorization.created", "issuing_authorization.request", "issuing_authorization.updated"],
                **incremental_args,
            ),
            customers,
            IncrementalStripeStream(
                name="cardholders",
                path="issuing/cardholders",
                event_types=["issuing_cardholder.created", "issuing_cardholder.updated"],
                **incremental_args,
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
                **incremental_args,
            ),
            IncrementalStripeStream(name="coupons", path="coupons", event_types=["coupon.created", "coupon.updated"], **incremental_args),
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
                **incremental_args,
            ),
            application_fees,
            invoices,
            IncrementalStripeStream(
                name="invoice_items",
                path="invoiceitems",
                legacy_cursor_field="date",
                event_types=["invoiceitem.created", "invoiceitem.updated"],
                **incremental_args,
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
                **incremental_args,
            ),
            IncrementalStripeStream(
                name="plans",
                path="plans",
                expand_items=["data.tiers"],
                event_types=["plan.created", "plan.updated"],
                **incremental_args,
            ),
            IncrementalStripeStream(name="prices", path="prices", event_types=["price.created", "price.updated"], **incremental_args),
            IncrementalStripeStream(
                name="products", path="products", event_types=["product.created", "product.updated"], **incremental_args
            ),
            IncrementalStripeStream(name="reviews", path="reviews", event_types=["review.closed", "review.opened"], **incremental_args),
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
                **incremental_args,
            ),
            transfers,
            IncrementalStripeStream(
                name="refunds", path="refunds", use_cache=True, event_types=["refund.created", "refund.updated"], **incremental_args
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
                **incremental_args,
            ),
            IncrementalStripeStream(
                name="promotion_codes",
                path="promotion_codes",
                event_types=["promotion_code.created", "promotion_code.updated"],
                **incremental_args,
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
                **incremental_args,
            ),
            IncrementalStripeStream(
                name="cards", path="issuing/cards", event_types=["issuing_card.created", "issuing_card.updated"], **incremental_args
            ),
            IncrementalStripeStream(
                name="transactions",
                path="issuing/transactions",
                event_types=["issuing_transaction.created", "issuing_transaction.updated"],
                **incremental_args,
            ),
            IncrementalStripeStream(
                name="top_ups",
                path="topups",
                event_types=["topup.canceled", "topup.created", "topup.failed", "topup.reversed", "topup.succeeded"],
                **incremental_args,
            ),
            UpdatedCursorIncrementalStripeLazySubStream(
                name="application_fees_refunds",
                path=lambda self, stream_slice, *args, **kwargs: f"application_fees/{stream_slice[self.parent_id]}/refunds",
                parent=application_fees,
                event_types=["application_fee.refund.updated"],
                parent_id="refund_id",
                sub_items_attr="refunds",
                add_parent_id=True,
                **incremental_args,
            ),
            UpdatedCursorIncrementalStripeLazySubStream(
                name="bank_accounts",
                path=lambda self, stream_slice, *args, **kwargs: f"customers/{stream_slice[self.parent_id]}/sources",
                parent=customers,
                event_types=["customer.source.created", "customer.source.expiring", "customer.source.updated"],
                legacy_cursor_field=None,
                parent_id="customer_id",
                sub_items_attr="sources",
                response_filter={"attr": "object", "value": "bank_account"},
                extra_request_params={"object": "bank_account"},
                record_extractor=FilteringRecordExtractor("updated", None, "bank_account"),
                **incremental_args,
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
