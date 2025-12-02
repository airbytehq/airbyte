# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from http import HTTPStatus
from typing import List, Optional
from unittest import TestCase

import freezegun

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker

from .config import ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import (
    addon_response,
    attached_item_response,
    configuration_incompatible_response,
    contact_response,
    coupon_response,
    credit_note_response,
    customer_response,
    customer_response_multiple,
    empty_response,
    error_response,
    event_response,
    gift_response,
    invoice_response,
    item_response,
    item_response_multiple,
    plan_response,
    subscription_response,
    transaction_response,
)
from .utils import config, read_output


def _read(
    config_builder: ConfigBuilder,
    stream_name: str,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    return read_output(
        config_builder=config_builder,
        stream_name=stream_name,
        sync_mode=sync_mode,
        state=state,
        expecting_exception=expecting_exception,
    )


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestCustomerStream(TestCase):
    """Tests for the customer stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for customer stream."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            customer_response(customer_id="cust_001"),
        )

        output = _read(config_builder=config(), stream_name="customer")
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "cust_001"
        assert "custom_fields" in output.records[0].record.data

    @HttpMocker()
    def test_pagination_two_pages(self, http_mocker: HttpMocker) -> None:
        """Test pagination with 2 pages for customer stream."""
        next_offset = "offset_page_2"

        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            [
                customer_response(customer_id="cust_001", next_offset=next_offset),
                customer_response(customer_id="cust_002"),
            ],
        )

        output = _read(config_builder=config(), stream_name="customer")
        assert len(output.records) == 2
        record_ids = [r.record.data["id"] for r in output.records]
        assert "cust_001" in record_ids
        assert "cust_002" in record_ids

    @HttpMocker()
    def test_incremental_emits_state(self, http_mocker: HttpMocker) -> None:
        """Test that incremental sync emits state message."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            customer_response(customer_id="cust_001", updated_at=1705312800),
        )

        output = _read(config_builder=config(), stream_name="customer", sync_mode=SyncMode.incremental)
        assert len(output.records) >= 1
        assert len(output.state_messages) >= 1


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestSubscriptionStream(TestCase):
    """Tests for the subscription stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for subscription stream."""
        http_mocker.get(
            RequestBuilder.subscriptions_endpoint().with_any_query_params().build(),
            subscription_response(subscription_id="sub_001"),
        )

        output = _read(config_builder=config(), stream_name="subscription")
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "sub_001"

    @HttpMocker()
    def test_pagination_two_pages(self, http_mocker: HttpMocker) -> None:
        """Test pagination with 2 pages for subscription stream."""
        next_offset = "offset_page_2"

        http_mocker.get(
            RequestBuilder.subscriptions_endpoint().with_any_query_params().build(),
            [
                subscription_response(subscription_id="sub_001", next_offset=next_offset),
                subscription_response(subscription_id="sub_002"),
            ],
        )

        output = _read(config_builder=config(), stream_name="subscription")
        assert len(output.records) == 2


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestInvoiceStream(TestCase):
    """Tests for the invoice stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for invoice stream."""
        http_mocker.get(
            RequestBuilder.invoices_endpoint().with_any_query_params().build(),
            invoice_response(invoice_id="inv_001"),
        )

        output = _read(config_builder=config(), stream_name="invoice")
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "inv_001"

    @HttpMocker()
    def test_incremental_emits_state(self, http_mocker: HttpMocker) -> None:
        """Test that incremental sync emits state message for invoice."""
        http_mocker.get(
            RequestBuilder.invoices_endpoint().with_any_query_params().build(),
            invoice_response(invoice_id="inv_001"),
        )

        output = _read(config_builder=config(), stream_name="invoice", sync_mode=SyncMode.incremental)
        assert len(output.records) >= 1
        assert len(output.state_messages) >= 1


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestEventStream(TestCase):
    """Tests for the event stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for event stream."""
        http_mocker.get(
            RequestBuilder.events_endpoint().with_any_query_params().build(),
            event_response(event_id="ev_001"),
        )

        output = _read(config_builder=config(), stream_name="event")
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "ev_001"

    @HttpMocker()
    def test_pagination_two_pages(self, http_mocker: HttpMocker) -> None:
        """Test pagination with 2 pages for event stream."""
        next_offset = "offset_page_2"

        http_mocker.get(
            RequestBuilder.events_endpoint().with_any_query_params().build(),
            [
                event_response(event_id="ev_001", next_offset=next_offset),
                event_response(event_id="ev_002"),
            ],
        )

        output = _read(config_builder=config(), stream_name="event")
        assert len(output.records) == 2


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestTransactionStream(TestCase):
    """Tests for the transaction stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for transaction stream."""
        http_mocker.get(
            RequestBuilder.transactions_endpoint().with_any_query_params().build(),
            transaction_response(transaction_id="txn_001"),
        )

        output = _read(config_builder=config(), stream_name="transaction")
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "txn_001"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestPlanStream(TestCase):
    """Tests for the plan stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for plan stream."""
        http_mocker.get(
            RequestBuilder.plans_endpoint().with_any_query_params().build(),
            plan_response(plan_id="plan_001"),
        )

        output = _read(config_builder=config(), stream_name="plan")
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "plan_001"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestAddonStream(TestCase):
    """Tests for the addon stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for addon stream."""
        http_mocker.get(
            RequestBuilder.addons_endpoint().with_any_query_params().build(),
            addon_response(addon_id="addon_001"),
        )

        output = _read(config_builder=config(), stream_name="addon")
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "addon_001"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestCouponStream(TestCase):
    """Tests for the coupon stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for coupon stream."""
        http_mocker.get(
            RequestBuilder.coupons_endpoint().with_any_query_params().build(),
            coupon_response(coupon_id="coupon_001"),
        )

        output = _read(config_builder=config(), stream_name="coupon")
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "coupon_001"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestCreditNoteStream(TestCase):
    """Tests for the credit_note stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for credit_note stream."""
        http_mocker.get(
            RequestBuilder.credit_notes_endpoint().with_any_query_params().build(),
            credit_note_response(credit_note_id="cn_001"),
        )

        output = _read(config_builder=config(), stream_name="credit_note")
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "cn_001"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestGiftStream(TestCase):
    """Tests for the gift stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for gift stream."""
        http_mocker.get(
            RequestBuilder.gifts_endpoint().with_any_query_params().build(),
            gift_response(gift_id="gift_001"),
        )

        output = _read(config_builder=config(), stream_name="gift")
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "gift_001"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestItemStream(TestCase):
    """Tests for the item stream."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for item stream."""
        http_mocker.get(
            RequestBuilder.items_endpoint().with_any_query_params().build(),
            item_response(item_id="item_001"),
        )

        output = _read(config_builder=config(), stream_name="item")
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "item_001"


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestContactStream(TestCase):
    """Tests for the contact stream (substream of customer)."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for contact stream (substream of customer)."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            customer_response(customer_id="cust_001"),
        )
        http_mocker.get(
            RequestBuilder.customer_contacts_endpoint("cust_001").with_any_query_params().build(),
            contact_response(contact_id="contact_001", customer_id="cust_001"),
        )

        output = _read(config_builder=config(), stream_name="contact")
        assert len(output.records) >= 1
        assert output.records[0].record.data["id"] == "contact_001"
        assert output.records[0].record.data["customer_id"] == "cust_001"

    @HttpMocker()
    def test_with_multiple_parents(self, http_mocker: HttpMocker) -> None:
        """Test contact substream with multiple parent customers."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            customer_response_multiple(["cust_001", "cust_002"]),
        )
        http_mocker.get(
            RequestBuilder.customer_contacts_endpoint("cust_001").with_any_query_params().build(),
            contact_response(contact_id="contact_001", customer_id="cust_001"),
        )
        http_mocker.get(
            RequestBuilder.customer_contacts_endpoint("cust_002").with_any_query_params().build(),
            contact_response(contact_id="contact_002", customer_id="cust_002"),
        )

        output = _read(config_builder=config(), stream_name="contact")
        assert len(output.records) >= 2
        customer_ids = [r.record.data.get("customer_id") for r in output.records]
        assert "cust_001" in customer_ids
        assert "cust_002" in customer_ids


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestAttachedItemStream(TestCase):
    """Tests for the attached_item stream (substream of item)."""

    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        """Basic read test for attached_item stream (substream of item)."""
        http_mocker.get(
            RequestBuilder.items_endpoint().with_any_query_params().build(),
            item_response(item_id="item_001"),
        )
        http_mocker.get(
            RequestBuilder.item_attached_items_endpoint("item_001").with_any_query_params().build(),
            attached_item_response(attached_item_id="attached_001", item_id="item_001"),
        )

        output = _read(config_builder=config(), stream_name="attached_item")
        assert len(output.records) >= 1
        assert output.records[0].record.data["id"] == "attached_001"

    @HttpMocker()
    def test_with_multiple_parents(self, http_mocker: HttpMocker) -> None:
        """Test attached_item substream with multiple parent items."""
        http_mocker.get(
            RequestBuilder.items_endpoint().with_any_query_params().build(),
            item_response_multiple(["item_001", "item_002"]),
        )
        http_mocker.get(
            RequestBuilder.item_attached_items_endpoint("item_001").with_any_query_params().build(),
            attached_item_response(attached_item_id="attached_001", item_id="item_001"),
        )
        http_mocker.get(
            RequestBuilder.item_attached_items_endpoint("item_002").with_any_query_params().build(),
            attached_item_response(attached_item_id="attached_002", item_id="item_002"),
        )

        output = _read(config_builder=config(), stream_name="attached_item")
        assert len(output.records) >= 2


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestErrorHandling(TestCase):
    """Tests for error handling."""

    @HttpMocker()
    def test_error_401_unauthorized(self, http_mocker: HttpMocker) -> None:
        """Test 401 error handling - should fail."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            error_response(HTTPStatus.UNAUTHORIZED),
        )

        output = _read(config_builder=config(), stream_name="customer", expecting_exception=True)
        assert len(output.records) == 0

    @HttpMocker()
    def test_error_configuration_incompatible_ignored(self, http_mocker: HttpMocker) -> None:
        """Test configuration_incompatible error is ignored as configured in manifest."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            configuration_incompatible_response(),
        )

        output = _read(config_builder=config(), stream_name="customer")
        assert len(output.records) == 0

    @HttpMocker()
    def test_contact_404_ignored(self, http_mocker: HttpMocker) -> None:
        """Test 404 error is ignored for contact stream as configured in manifest."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            customer_response(customer_id="cust_001"),
        )
        http_mocker.get(
            RequestBuilder.customer_contacts_endpoint("cust_001").with_any_query_params().build(),
            error_response(HTTPStatus.NOT_FOUND),
        )

        output = _read(config_builder=config(), stream_name="contact")
        assert len(output.records) == 0


@freezegun.freeze_time("2024-01-15T12:00:00Z")
class TestEmptyResponse(TestCase):
    """Tests for empty response handling."""

    @HttpMocker()
    def test_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test handling of empty response."""
        http_mocker.get(
            RequestBuilder.customers_endpoint().with_any_query_params().build(),
            empty_response(),
        )

        output = _read(config_builder=config(), stream_name="customer")
        assert len(output.records) == 0
