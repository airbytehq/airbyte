#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock

from source_recurly.streams import (
    BEGIN_TIME_PARAM,
    DEFAULT_CURSOR,
    DEFAULT_LIMIT,
    AccountCouponRedemptions,
    BaseStream,
    ExportDates,
    MeasuredUnits,
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

    def test_get_updated_state(self):
        stream = TestStream(client=self.client_mock)

        cursor_field = stream.cursor_field

        now = datetime.now()
        yesterday = now - timedelta(days=1)

        current_state = {cursor_field: yesterday.isoformat()}
        latest_record = {cursor_field: now}

        expected_date = {cursor_field: now.isoformat()}

        assert stream.get_updated_state(current_state, latest_record) == expected_date

    def test_account_coupon_redemptions_read_records(self):
        stream = AccountCouponRedemptions(client=self.client_mock)
        account_id_mock = Mock()
        account_mock = Mock(id=account_id_mock)
        self.client_mock.list_accounts.return_value.items.return_value = iter([account_mock])
        self.client_mock.list_account_coupon_redemptions.return_value.items.return_value = iter([None])

        next(iter(stream.read_records(self.sync_mode_mock)))

        self.client_mock.list_accounts.assert_called_once()
        self.client_mock.list_account_coupon_redemptions.assert_called_once_with(account_id=account_id_mock, params=self.params)

    def test_export_dates_read_records(self):
        stream = ExportDates(client=self.client_mock)

        next(iter(stream.read_records(self.sync_mode_mock)))

        self.client_mock.get_export_dates.assert_called_once()

    def test_measured_unit_client_method_name(self):
        stream = MeasuredUnits(client=self.client_mock)

        assert stream.client_method_name == "list_measured_unit"
