#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime, timedelta

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.auth import NoAuth
from dateutil.parser import isoparse
from pytest import raises
from source_paypal_transaction.source import Balances, PaypalTransactionStream, Transactions


def test_minimum_allowed_start_date():
    start_date = now() - timedelta(days=10 * 365)
    stream = Transactions(authenticator=NoAuth(), start_date=start_date)
    assert stream.start_date != start_date


def test_transactions_transform_function():
    start_date = now() - timedelta(days=10 * 365)
    stream = Transactions(authenticator=NoAuth(), start_date=start_date)
    transformer = stream.transformer
    input_data = {"transaction_amount": "123.45", "transaction_id": "111", "transaction_status": "done"}
    schema = stream.get_json_schema()
    schema["properties"] = {
        "transaction_amount": {"type": "number"},
        "transaction_id": {"type": "integer"},
        "transaction_status": {"type": "string"},
    }
    transformer.transform(input_data, schema)
    expected_data = {"transaction_amount": 123.45, "transaction_id": 111, "transaction_status": "done"}
    assert input_data == expected_data


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


def test_unnest_field():
    record = {"transaction_info": {"transaction_id": "123", "transaction_initiation_date": "2014-07-11T04:03:52+0000"}}
    # check the cursor is not on the root level
    assert Transactions.cursor_field not in record.keys()

    PaypalTransactionStream.unnest_field(record, Transactions.nested_object, Transactions.cursor_field)
    # check the cursor now on the root level
    assert Transactions.cursor_field in record.keys()


def test_get_last_refreshed_datetime(requests_mock, prod_config, api_endpoint):
    stream = Balances(authenticator=NoAuth(), **prod_config)
    requests_mock.post(f"{api_endpoint}/v1/oauth2/token", json={"access_token": "test_access_token", "expires_in": 12345})
    url = f"{api_endpoint}/v1/reporting/balances" + "?as_of_time=2021-07-01T00%3A00%3A00%2B00%3A00"
    requests_mock.get(url, json={})
    assert not stream.get_last_refreshed_datetime(SyncMode.full_refresh)


def test_get_updated_state(transactions):
    start_date = "2021-06-01T10:00:00+00:00"
    stream = Transactions(
        authenticator=NoAuth(),
        start_date=isoparse(start_date),
        end_date=isoparse("2021-06-04T12:00:00+00:00"),
    )
    state = stream.get_updated_state(current_stream_state={}, latest_record={})
    assert state == {"date": start_date}

    record = transactions[stream.data_field][0][stream.nested_object]
    expected_state = {"date": now().isoformat()}
    state = stream.get_updated_state(current_stream_state=expected_state, latest_record=record)
    assert state == expected_state
