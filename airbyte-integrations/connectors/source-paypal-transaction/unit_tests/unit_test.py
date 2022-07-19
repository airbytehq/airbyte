#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
import pathlib
from datetime import datetime, timedelta

from airbyte_cdk.sources.streams.http.auth import NoAuth
from dateutil.parser import isoparse
from pytest import fixture, raises
from source_paypal_transaction.source import Balances, PaypalTransactionStream, Transactions


@fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock


@fixture(autouse=True)
def transactions(request):
    file = pathlib.Path(request.node.fspath.strpath)
    transaction = file.with_name("transaction.json")
    with transaction.open() as fp:
        return json.load(fp)


def test_get_field():
    record = {"a": {"b": {"c": "d"}}}
    # Test expected result - field_path is a list
    assert "d" == PaypalTransactionStream.get_field(record, field_path=["a", "b", "c"])
    # Test expected result - field_path is a string
    assert {"b": {"c": "d"}} == PaypalTransactionStream.get_field(record, field_path="a")

    # Test failures - not existing field_path
    assert None is PaypalTransactionStream.get_field(record, field_path=["a", "b", "x"])
    assert None is PaypalTransactionStream.get_field(record, field_path=["a", "x", "x"])
    assert None is PaypalTransactionStream.get_field(record, field_path=["x", "x", "x"])

    # Test failures - incorrect record structure
    record = {"a": [{"b": {"c": "d"}}]}
    assert None is PaypalTransactionStream.get_field(record, field_path=["a", "b", "c"])

    record = {"a": {"b": "c"}}
    assert None is PaypalTransactionStream.get_field(record, field_path=["a", "b", "c"])

    record = {}
    assert None is PaypalTransactionStream.get_field(record, field_path=["a", "b", "c"])


def test_update_field():
    # Test success 1
    record = {"a": {"b": {"c": "d"}}}
    PaypalTransactionStream.update_field(record, field_path=["a", "b", "c"], update=lambda x: x.upper())
    assert record == {"a": {"b": {"c": "D"}}}

    # Test success 2
    record = {"a": {"b": {"c": "d"}}}
    PaypalTransactionStream.update_field(record, field_path="a", update=lambda x: "updated")
    assert record == {"a": "updated"}

    # Test failure - incorrect field_path
    record = {"a": {"b": {"c": "d"}}}
    PaypalTransactionStream.update_field(record, field_path=["a", "b", "x"], update=lambda x: x.upper())
    assert record == {"a": {"b": {"c": "d"}}}

    # Test failure - incorrect field_path
    record = {"a": {"b": {"c": "d"}}}
    PaypalTransactionStream.update_field(record, field_path=["a", "x", "x"], update=lambda x: x.upper())
    assert record == {"a": {"b": {"c": "d"}}}


def now():
    return datetime.now().replace(microsecond=0).astimezone()


def test_transactions_stream_slices():
    start_date_max = {"hours": 0}

    # if start_date > now - **start_date_max then no slices
    transactions = Transactions(
        authenticator=NoAuth(),
        start_date=now() - timedelta(**start_date_max) - timedelta(minutes=2),
    )
    transactions.get_last_refreshed_datetime = lambda x: None
    stream_slices = transactions.stream_slices(sync_mode="any")
    assert 1 == len(stream_slices)

    # start_date <= now - **start_date_max
    transactions = Transactions(
        authenticator=NoAuth(),
        start_date=now() - timedelta(**start_date_max),
    )
    transactions.get_last_refreshed_datetime = lambda x: None
    stream_slices = transactions.stream_slices(sync_mode="any")
    assert 1 == len(stream_slices)

    transactions = Transactions(
        authenticator=NoAuth(),
        start_date=now() - timedelta(**start_date_max) + timedelta(minutes=2),
    )
    transactions.get_last_refreshed_datetime = lambda x: None
    stream_slices = transactions.stream_slices(sync_mode="any")
    assert 1 == len(stream_slices)

    transactions = Transactions(
        authenticator=NoAuth(),
        start_date=now() - timedelta(**start_date_max) - timedelta(hours=2),
    )
    transactions.get_last_refreshed_datetime = lambda x: None
    stream_slices = transactions.stream_slices(sync_mode="any")
    assert 1 == len(stream_slices)

    transactions = Transactions(
        authenticator=NoAuth(),
        start_date=now() - timedelta(**start_date_max) - timedelta(days=1),
    )
    transactions.get_last_refreshed_datetime = lambda x: None
    transactions.stream_slice_period = {"days": 1}
    stream_slices = transactions.stream_slices(sync_mode="any")
    assert 2 == len(stream_slices)

    transactions = Transactions(
        authenticator=NoAuth(),
        start_date=now() - timedelta(**start_date_max) - timedelta(days=1, hours=2),
    )
    transactions.get_last_refreshed_datetime = lambda x: None
    transactions.stream_slice_period = {"days": 1}
    stream_slices = transactions.stream_slices(sync_mode="any")
    assert 2 == len(stream_slices)

    transactions = Transactions(
        authenticator=NoAuth(),
        start_date=now() - timedelta(**start_date_max) - timedelta(days=30, minutes=1),
    )
    transactions.get_last_refreshed_datetime = lambda x: None
    transactions.stream_slice_period = {"days": 1}
    stream_slices = transactions.stream_slices(sync_mode="any")
    assert 31 == len(stream_slices)

    # tests with specified end_date
    transactions = Transactions(
        authenticator=NoAuth(),
        start_date=isoparse("2021-06-01T10:00:00+00:00"),
        end_date=isoparse("2021-06-04T12:00:00+00:00"),
    )
    transactions.get_last_refreshed_datetime = lambda x: None
    transactions.stream_slice_period = {"days": 1}
    stream_slices = transactions.stream_slices(sync_mode="any")
    assert [
        {"start_date": "2021-06-01T10:00:00+00:00", "end_date": "2021-06-02T10:00:00+00:00"},
        {"start_date": "2021-06-02T10:00:00+00:00", "end_date": "2021-06-03T10:00:00+00:00"},
        {"start_date": "2021-06-03T10:00:00+00:00", "end_date": "2021-06-04T10:00:00+00:00"},
        {"start_date": "2021-06-04T10:00:00+00:00", "end_date": "2021-06-04T12:00:00+00:00"},
    ] == stream_slices

    # tests with specified end_date and stream_state
    transactions = Transactions(
        authenticator=NoAuth(),
        start_date=isoparse("2021-06-01T10:00:00+00:00"),
        end_date=isoparse("2021-06-04T12:00:00+00:00"),
    )
    transactions.get_last_refreshed_datetime = lambda x: None
    transactions.stream_slice_period = {"days": 1}
    stream_slices = transactions.stream_slices(sync_mode="any", stream_state={"date": "2021-06-02T10:00:00+00:00"})
    assert [
        {"start_date": "2021-06-02T10:00:00+00:00", "end_date": "2021-06-03T10:00:00+00:00"},
        {"start_date": "2021-06-03T10:00:00+00:00", "end_date": "2021-06-04T10:00:00+00:00"},
        {"start_date": "2021-06-04T10:00:00+00:00", "end_date": "2021-06-04T12:00:00+00:00"},
    ] == stream_slices

    transactions = Transactions(
        authenticator=NoAuth(),
        start_date=isoparse("2021-06-01T10:00:00+00:00"),
        end_date=isoparse("2021-06-04T12:00:00+00:00"),
    )
    transactions.get_last_refreshed_datetime = lambda x: None
    stream_slices = transactions.stream_slices(sync_mode="any", stream_state={"date": "2021-06-04T10:00:00+00:00"})
    assert [{"start_date": "2021-06-04T10:00:00+00:00", "end_date": "2021-06-04T12:00:00+00:00"}] == stream_slices


def test_balances_stream_slices():
    """Test slices for Balance stream.
    Note that <end_date> is not used by this stream.
    """
    now = datetime.now().replace(microsecond=0).astimezone()

    # Test without end_date (it equal <now> by default)
    balance = Balances(authenticator=NoAuth(), start_date=now)
    balance.get_last_refreshed_datetime = lambda x: None
    stream_slices = balance.stream_slices(sync_mode="any")
    assert 1 == len(stream_slices)

    balance = Balances(authenticator=NoAuth(), start_date=now - timedelta(minutes=1))
    balance.get_last_refreshed_datetime = lambda x: None
    stream_slices = balance.stream_slices(sync_mode="any")
    assert 1 == len(stream_slices)

    balance = Balances(
        authenticator=NoAuth(),
        start_date=now - timedelta(hours=23),
    )
    balance.get_last_refreshed_datetime = lambda x: None
    stream_slices = balance.stream_slices(sync_mode="any")
    assert 1 == len(stream_slices)

    balance = Balances(
        authenticator=NoAuth(),
        start_date=now - timedelta(days=1),
    )
    balance.get_last_refreshed_datetime = lambda x: None
    balance.stream_slice_period = {"days": 1}
    stream_slices = balance.stream_slices(sync_mode="any")
    assert 2 == len(stream_slices)

    balance = Balances(
        authenticator=NoAuth(),
        start_date=now - timedelta(days=1, minutes=1),
    )
    balance.get_last_refreshed_datetime = lambda x: None
    balance.stream_slice_period = {"days": 1}
    stream_slices = balance.stream_slices(sync_mode="any")
    assert 2 == len(stream_slices)

    # test with custom end_date
    balance = Balances(
        authenticator=NoAuth(),
        start_date=isoparse("2021-06-01T10:00:00+00:00"),
        end_date=isoparse("2021-06-03T12:00:00+00:00"),
    )
    balance.get_last_refreshed_datetime = lambda x: None
    balance.stream_slice_period = {"days": 1}
    stream_slices = balance.stream_slices(sync_mode="any")
    assert [
        {"start_date": "2021-06-01T10:00:00+00:00", "end_date": "2021-06-02T10:00:00+00:00"},
        {"start_date": "2021-06-02T10:00:00+00:00", "end_date": "2021-06-03T10:00:00+00:00"},
        {"start_date": "2021-06-03T10:00:00+00:00", "end_date": "2021-06-03T12:00:00+00:00"},
    ] == stream_slices

    # Test with stream state
    balance = Balances(
        authenticator=NoAuth(),
        start_date=isoparse("2021-06-01T10:00:00+00:00"),
        end_date=isoparse("2021-06-03T12:00:00+00:00"),
    )
    balance.get_last_refreshed_datetime = lambda x: None
    balance.stream_slice_period = {"days": 1}
    stream_slices = balance.stream_slices(sync_mode="any", stream_state={"date": "2021-06-02T10:00:00+00:00"})
    assert [
        {"start_date": "2021-06-02T10:00:00+00:00", "end_date": "2021-06-03T10:00:00+00:00"},
        {"start_date": "2021-06-03T10:00:00+00:00", "end_date": "2021-06-03T12:00:00+00:00"},
    ] == stream_slices

    balance = Balances(
        authenticator=NoAuth(),
        start_date=isoparse("2021-06-01T10:00:00+00:00"),
        end_date=isoparse("2021-06-03T12:00:00+00:00"),
    )
    balance.get_last_refreshed_datetime = lambda x: None
    balance.stream_slice_period = {"days": 1}
    stream_slices = balance.stream_slices(sync_mode="any", stream_state={"date": "2021-06-03T11:00:00+00:00"})
    assert [{"start_date": "2021-06-03T11:00:00+00:00", "end_date": "2021-06-03T12:00:00+00:00"}] == stream_slices

    balance = Balances(
        authenticator=NoAuth(),
        start_date=isoparse("2021-06-01T10:00:00+00:00"),
        end_date=isoparse("2021-06-03T12:00:00+00:00"),
    )
    balance.get_last_refreshed_datetime = lambda x: None
    balance.stream_slice_period = {"days": 1}
    stream_slices = balance.stream_slices(sync_mode="any", stream_state={"date": "2021-06-03T12:00:00+00:00"})
    assert [{"start_date": "2021-06-03T12:00:00+00:00", "end_date": "2021-06-03T12:00:00+00:00"}] == stream_slices


def test_max_records_in_response_reached(transactions, requests_mock):
    balance = Transactions(
        authenticator=NoAuth(),
        start_date=isoparse("2021-07-01T10:00:00+00:00"),
        end_date=isoparse("2021-07-29T12:00:00+00:00"),
    )
    error_message = {
        "name": "RESULTSET_TOO_LARGE",
        "message": "Result set size is greater than the maximum limit. Change the filter " "criteria and try again.",
    }
    url = "https://api-m.paypal.com/v1/reporting/transactions"

    requests_mock.register_uri(
        "GET",
        url + "?start_date=2021-07-01T12%3A00%3A00%2B00%3A00&end_date=2021-07-29T12%3A00%3A00%2B00%3A00",
        json=error_message,
        status_code=400,
    )
    requests_mock.register_uri(
        "GET", url + "?start_date=2021-07-01T12%3A00%3A00%2B00%3A00&end_date=2021-07-15T12%3A00%3A00%2B00%3A00", json=transactions
    )
    requests_mock.register_uri(
        "GET", url + "?start_date=2021-07-15T12%3A00%3A00%2B00%3A00&end_date=2021-07-29T12%3A00%3A00%2B00%3A00", json=transactions
    )
    month_date_slice = {"start_date": "2021-07-01T12:00:00+00:00", "end_date": "2021-07-29T12:00:00+00:00"}
    assert len(list(balance.read_records(sync_mode="any", stream_slice=month_date_slice))) == 2

    requests_mock.register_uri(
        "GET",
        url + "?start_date=2021-07-01T12%3A00%3A00%2B00%3A00&end_date=2021-07-01T12%3A00%3A00%2B00%3A00",
        json=error_message,
        status_code=400,
    )
    one_day_slice = {"start_date": "2021-07-01T12:00:00+00:00", "end_date": "2021-07-01T12:00:00+00:00"}
    with raises(Exception):
        assert next(balance.read_records(sync_mode="any", stream_slice=one_day_slice))
