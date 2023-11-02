#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, MutableMapping, Optional, Tuple, Union

import pendulum
import stripe
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.entrypoint import logger as entrypoint_logger
from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.declarative.extractors import DpathExtractor, RecordSelector
from airbyte_cdk.sources.declarative.requesters import HttpRequester, RequestOption
from airbyte_cdk.sources.declarative.requesters.paginators import DefaultPaginator
from airbyte_cdk.sources.declarative.requesters.paginators.strategies import CursorPaginationStrategy
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.requesters.request_options import InterpolatedRequestOptionsProvider
from airbyte_cdk.sources.message.repository import InMemoryMessageRepository
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamAvailabilityStrategy, StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import NoopCursor
from airbyte_cdk.sources.streams.concurrent.thread_based_concurrent_stream import ThreadBasedConcurrentStream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from source_stripe.partition import PaginatedRequester, SourcePartitionGenerator
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
_PAGE_SIZE = 100


class StripePaginationStrategy(CursorPaginationStrategy):
    def stop(self, response: Union[Mapping[str, Any], List], headers: Mapping[str, Any], last_records: List[Mapping[str, Any]]) -> bool:
        return "has_more" not in response

    def get_cursor_value(
        self, response: Union[Mapping[str, Any], List], headers: Mapping[str, Any], last_records: List[Mapping[str, Any]]
    ) -> Optional[str]:
        if "has_more" in response and response["has_more"] and response.get("data", []):
            last_object_id = response["data"][-1]["id"]
            return last_object_id
        return None


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

    def _create_concurrent_stream(self, base_stream: HttpStream, concurrency_level: int = _MAX_CONCURRENCY) -> Stream:
        http_requester = HttpRequester(
            url_base=base_stream.url_base,
            request_options_provider=InterpolatedRequestOptionsProvider(
                request_headers={**{"Stripe-Version": "", "Stripe-Account": ""}, **base_stream.authenticator.get_auth_header()},
                parameters={},
            ),
            path=base_stream.path(),
            name=base_stream.name,
            config={},
            parameters={},
            message_repository=self.message_repository,
        )

        paginator = DefaultPaginator(
            StripePaginationStrategy(page_size=_PAGE_SIZE),
            config={},
            url_base="",
            parameters={},
            page_size_option=RequestOption(field_name="limit", inject_into=RequestOptionType.request_parameter, parameters={}),
            page_token_option=RequestOption(field_name="starting_after", inject_into=RequestOptionType.request_parameter, parameters={}),
        )

        record_selector = RecordSelector(DpathExtractor(field_path=["data"], config={}, parameters={}), {}, {})
        paginated_requester = PaginatedRequester(http_requester, record_selector, paginator)

        partition_generator = SourcePartitionGenerator(
            base_stream,
            paginated_requester,
            request_params={
                "created[gte]": lambda _slice: _slice.get("created[gte]") if _slice else None,
                "created[lte]": lambda _slice: _slice.get("created[lte]") if _slice else None,
            },
        )

        primary_key = base_stream.primary_key
        if isinstance(primary_key, str):
            primary_key = [primary_key]

        concurrent_stream = StreamFacade(
            ThreadBasedConcurrentStream(
                partition_generator=partition_generator,
                max_workers=concurrency_level,
                name=base_stream.name,
                json_schema=base_stream.get_json_schema(),
                availability_strategy=StreamAvailabilityStrategy(base_stream, self),
                primary_key=primary_key,
                cursor_field=base_stream.cursor_field,
                slice_logger=self._slice_logger,
                logger=base_stream.logger,
                message_repository=self.message_repository,
            ),
            base_stream,
            NoopCursor(),
        )
        return concurrent_stream

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

        main_streams = [
            StripeStream(name="accounts", path="accounts", use_cache=True, **args),
            application_fees,
            Events(**incremental_args),
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
        ]

        substreams = [
            CheckoutSessionsLineItems(**incremental_args),
            CustomerBalanceTransactions(**args),
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
            main_streams[0].logger.info(f"Using concurrent cdk with concurrency level {concurrency_level}")

            main_streams = [self._create_concurrent_stream(base_stream, concurrency_level) for base_stream in main_streams]
            substreams = [
                StreamFacade.create_from_stream(stream, self, entrypoint_logger, concurrency_level, {}, NoopCursor())
                for stream in substreams
            ]

        return main_streams + substreams
