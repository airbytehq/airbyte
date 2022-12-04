#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock

from source_recurly.streams import (
    BEGIN_TIME_PARAM,
    DEFAULT_CURSOR,
    DEFAULT_LIMIT,
    END_TIME_PARAM,
    AccountCouponRedemptions,
    AccountNotes,
    Accounts,
    AddOns,
    BaseStream,
    BillingInfos,
    Coupons,
    CreditPayments,
    ExportDates,
    Invoices,
    LineItems,
    MeasuredUnits,
    Plans,
    ShippingAddresses,
    ShippingMethods,
    Subscriptions,
    Transactions,
    UniqueCoupons,
)

METHOD_NAME = "list_resource"


class TestStream(BaseStream):
    name = "test"
    client_method_name = METHOD_NAME


class TestStreams(unittest.TestCase):
    def setUp(self) -> None:
        self.client_mock = Mock()
        getattr(self.client_mock, METHOD_NAME).return_value.items.return_value = iter([None])

        self.sync_mode_mock = Mock()

        self.params = {"order": "asc", "sort": DEFAULT_CURSOR, "limit": DEFAULT_LIMIT}

    def test_read_records(self):
        stream = TestStream(client=self.client_mock)

        next(iter(stream.read_records(self.sync_mode_mock)))

        getattr(self.client_mock, METHOD_NAME).assert_called_once_with(params=self.params)

        getattr(self.client_mock, METHOD_NAME).return_value.items.assert_called_once()

    def test_read_records_with_begin_time(self):
        begin_time_mock = Mock()
        stream = TestStream(client=self.client_mock, begin_time=begin_time_mock)

        next(iter(stream.read_records(self.sync_mode_mock)))

        params = {**self.params, BEGIN_TIME_PARAM: begin_time_mock}

        getattr(self.client_mock, METHOD_NAME).assert_called_once_with(params=params)

    def test_read_records_with_end_time(self):
        end_time_mock = Mock()
        stream = TestStream(client=self.client_mock, end_time=end_time_mock)

        next(iter(stream.read_records(self.sync_mode_mock)))

        params = {**self.params, END_TIME_PARAM: end_time_mock}

        getattr(self.client_mock, METHOD_NAME).assert_called_once_with(params=params)

    def test_get_updated_state(self):
        stream = TestStream(client=self.client_mock)

        cursor_field = stream.cursor_field

        now = datetime.now()
        yesterday = now - timedelta(days=1)

        current_state = {cursor_field: yesterday.isoformat()}
        latest_record = {cursor_field: now}

        expected_date = {cursor_field: now.isoformat()}

        assert stream.get_updated_state(current_state, latest_record) == expected_date

    def test_accounts_methods_client_method_name(self):
        stream = Accounts(client=self.client_mock)

        assert stream.client_method_name == "list_accounts"

    def test_account_coupon_redemptions_read_records(self):
        stream = AccountCouponRedemptions(client=self.client_mock)
        account_id_mock = Mock()
        account_mock = Mock(id=account_id_mock)
        self.client_mock.list_accounts.return_value.items.return_value = iter([account_mock])
        self.client_mock.list_account_coupon_redemptions.return_value.items.return_value = iter([None])

        next(iter(stream.read_records(self.sync_mode_mock)))

        self.client_mock.list_accounts.assert_called_once()
        self.client_mock.list_account_coupon_redemptions.assert_called_once_with(account_id=account_id_mock, params=self.params)

    def test_account_notes_read_records(self):
        stream = AccountNotes(client=self.client_mock)
        account_id_mock = Mock()
        account_mock = Mock(id=account_id_mock)
        self.client_mock.list_accounts.return_value.items.return_value = iter([account_mock])
        self.client_mock.list_account_notes.return_value.items.return_value = iter([None])

        params = {"order": "asc", "sort": "created_at", "limit": DEFAULT_LIMIT}

        next(iter(stream.read_records(self.sync_mode_mock)))

        self.client_mock.list_accounts.assert_called_once()
        self.client_mock.list_account_notes.assert_called_once_with(account_id=account_id_mock, params=params)

    def test_add_ons_client_method_name(self):
        stream = AddOns(client=self.client_mock)

        assert stream.client_method_name == "list_add_ons"

    def test_billing_infos_client_method_name(self):
        stream = BillingInfos(client=self.client_mock)

        assert stream.client_method_name == "list_billing_infos"

    def test_coupons_methods_client_method_name(self):
        stream = Coupons(client=self.client_mock)

        assert stream.client_method_name == "list_coupons"

    def test_credit_payments_read_records(self):
        stream = CreditPayments(client=self.client_mock)

        assert stream.client_method_name == "list_credit_payments"

    def test_export_dates_read_records(self):
        stream = ExportDates(client=self.client_mock)

        next(iter(stream.read_records(self.sync_mode_mock)))

        self.client_mock.get_export_dates.assert_called_once()

    def test_invoices_methods_client_method_name(self):
        stream = Invoices(client=self.client_mock)

        assert stream.client_method_name == "list_invoices"

    def test_line_items_methods_client_method_name(self):
        stream = LineItems(client=self.client_mock)

        assert stream.client_method_name == "list_line_items"

    def test_measured_unit_client_method_name(self):
        stream = MeasuredUnits(client=self.client_mock)

        assert stream.client_method_name == "list_measured_unit"

    def test_plans_client_method_name(self):
        stream = Plans(client=self.client_mock)

        assert stream.client_method_name == "list_plans"

    def test_shipping_addresses_client_method_name(self):
        stream = ShippingAddresses(client=self.client_mock)

        assert stream.client_method_name == "list_shipping_addresses"

    def test_shipping_methods_client_method_name(self):
        stream = ShippingMethods(client=self.client_mock)

        assert stream.client_method_name == "list_shipping_methods"

    def test_subscriptions_client_method_name(self):
        stream = Subscriptions(client=self.client_mock)

        assert stream.client_method_name == "list_subscriptions"

    def test_transactions_client_method_name(self):
        stream = Transactions(client=self.client_mock)

        assert stream.client_method_name == "list_transactions"

    def test_unique_coupons_read_records(self):
        stream = UniqueCoupons(client=self.client_mock)
        coupon_id_mock = Mock()
        coupon_mock = Mock(id=coupon_id_mock)
        self.client_mock.list_coupons.return_value.items.return_value = iter([coupon_mock])
        self.client_mock.list_unique_coupon_codes.return_value.items.return_value = iter([None])

        next(iter(stream.read_records(self.sync_mode_mock)))

        self.client_mock.list_coupons.assert_called_once()
        self.client_mock.list_unique_coupon_codes.assert_called_once_with(coupon_id=coupon_id_mock, params=self.params)
