#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import freezegun
import pendulum
import pytest
from source_stripe.streams import (
    CheckoutSessionsLineItems,
    CreatedCursorIncrementalStripeStream,
    CustomerBalanceTransactions,
    Persons,
    SetupAttempts,
    StripeStream,
    UpdatedCursorIncrementalStripeStream,
)


@pytest.fixture()
def accounts(stream_args):
    def mocker(args=stream_args):
        return StripeStream(name="accounts", path="accounts", **args)
    return mocker


@pytest.fixture()
def balance_transactions(incremental_stream_args):
    def mocker(args=incremental_stream_args):
        return CreatedCursorIncrementalStripeStream(name="balance_transactions", path="balance_transactions", **args)
    return mocker


@pytest.fixture()
def credit_notes(incremental_stream_args):
    def mocker(args=incremental_stream_args):
        return UpdatedCursorIncrementalStripeStream(
            name="credit_notes",
            path="credit_notes",
            event_types=["credit_note.created", "credit_note.updated", "credit_note.voided"],
            **args
        )
    return mocker


def test_request_headers(accounts):
    stream = accounts()
    headers = stream.request_headers()
    assert headers["Stripe-Version"] == "2022-11-15"


def test_lazy_sub_stream(requests_mock, invoice_line_items, invoices, stream_args, incremental_stream_args):
    # First initial request to parent stream
    requests_mock.get(
        "https://api.stripe.com/v1/invoices",
        json={
            "has_more": False,
            "object": "list",
            "url": "/v1/checkout/sessions",
            "data": [
                {
                    "created": 1641038947,
                    "customer": "cus_HezytZRkaQJC8W",
                    "id": "in_1KD6OVIEn5WyEQxn9xuASHsD",
                    "object": "invoice",
                    "total": 1,
                    "lines": {
                        "data": [
                            {
                                "id": "il_1",
                                "object": "line_item",
                            },
                            {
                                "id": "il_2",
                                "object": "line_item",
                            },
                        ],
                        "has_more": True,
                        "object": "list",
                        "total_count": 3,
                        "url": "/v1/invoices/in_1KD6OVIEn5WyEQxn9xuASHsD/lines",
                    },
                }
            ],
        },
    )

    # Second pagination request to main stream
    requests_mock.get(
        "https://api.stripe.com/v1/invoices/in_1KD6OVIEn5WyEQxn9xuASHsD/lines",
        json={
            "data": [
                {
                    "id": "il_3",
                    "object": "line_item",
                },
            ],
            "has_more": False,
            "object": "list",
            "total_count": 3,
            "url": "/v1/invoices/in_1KD6OVIEn5WyEQxn9xuASHsD/lines",
        },
    )

    # make start date a recent date so there's just one slice in a parent stream
    stream_args["start_date"] = pendulum.today().subtract(days=3).int_timestamp
    incremental_stream_args["start_date"] = pendulum.today().subtract(days=3).int_timestamp
    parent_stream = invoices(incremental_stream_args)
    stream = invoice_line_items(stream_args, parent_stream=parent_stream)
    records = []

    for slice_ in stream.stream_slices(sync_mode="full_refresh"):
        records.extend(stream.read_records(sync_mode="full_refresh", stream_slice=slice_))
    assert list(records) == [
        {"id": "il_1", "invoice_id": "in_1KD6OVIEn5WyEQxn9xuASHsD", "object": "line_item"},
        {"id": "il_2", "invoice_id": "in_1KD6OVIEn5WyEQxn9xuASHsD", "object": "line_item"},
        {"id": "il_3", "invoice_id": "in_1KD6OVIEn5WyEQxn9xuASHsD", "object": "line_item"},
    ]


@freezegun.freeze_time("2023-08-23T15:00:15Z")
def test_created_cursor_incremental_stream(requests_mock, balance_transactions, incremental_stream_args):
    incremental_stream_args["start_date"] = pendulum.now().subtract(months=23).int_timestamp
    stream = balance_transactions(incremental_stream_args)
    requests_mock.get(
        "/v1/balance_transactions",
        [
            {
                "json": {
                    "data": [{
                        "id": "txn_1KVQhfEcXtiJtvvhF7ox3YEm", "object": "balance_transaction", "amount": 435, "status": "available"}
                    ],
                    "has_more": False
                }
            },
            {
                "json": {
                    "data":[{
                        "id": "txn_tiJtvvhF7ox3YEmKvVQhfEcX", "object": "balance_transaction", "amount": -9164, "status": "available"}
                    ],
                    "has_more": False
                }
            }
        ]
    )

    slices = list(stream.stream_slices("full_refresh"))
    assert slices == [{'created[gte]': 1631199615, 'created[lte]': 1662735615}, {'created[gte]': 1662735616, 'created[lte]': 1692802815}]
    records = []
    for slice_ in slices:
        for record in stream.read_records("full_refresh", stream_slice=slice_):
            records.append(record)
    assert records == [
        {"id": "txn_1KVQhfEcXtiJtvvhF7ox3YEm", "object": "balance_transaction", "amount": 435, "status": "available"},
        {"id": "txn_tiJtvvhF7ox3YEmKvVQhfEcX", "object": "balance_transaction", "amount": -9164, "status": "available"}
    ]


@pytest.mark.parametrize(
    "start_date, lookback_window, max_days_from_now, stream_state, expected_start_timestamp",
    (
        ("2020-01-01T00:00:00Z", 0, 0, {}, "2020-01-01T00:00:00Z"),
        ("2020-01-01T00:00:00Z", 14, 0, {}, "2019-12-18T00:00:00Z"),
        ("2020-01-01T00:00:00Z", 0, 30, {}, "2023-07-24T15:00:15Z"),
        ("2020-01-01T00:00:00Z", 14, 30, {}, "2023-07-24T15:00:15Z"),
        ("2020-01-01T00:00:00Z", 0, 0, {"created": pendulum.parse("2022-07-17T00:00:00Z").int_timestamp}, "2022-07-17T00:00:00Z"),
        ("2020-01-01T00:00:00Z", 14, 0, {"created": pendulum.parse("2022-07-17T00:00:00Z").int_timestamp}, "2022-07-03T00:00:00Z"),
        ("2020-01-01T00:00:00Z", 0, 30, {"created": pendulum.parse("2022-07-17T00:00:00Z").int_timestamp}, "2023-07-24T15:00:15Z"),
        ("2020-01-01T00:00:00Z", 14, 30, {"created": pendulum.parse("2022-07-17T00:00:00Z").int_timestamp}, "2023-07-24T15:00:15Z"),
    )
)
@freezegun.freeze_time("2023-08-23T15:00:15Z")
def test_get_start_timestamp(balance_transactions, incremental_stream_args, start_date, lookback_window, max_days_from_now, stream_state, expected_start_timestamp):
    incremental_stream_args["start_date"] = pendulum.parse(start_date).int_timestamp
    incremental_stream_args["lookback_window_days"] = lookback_window
    incremental_stream_args["start_date_max_days_from_now"] = max_days_from_now
    stream = balance_transactions(incremental_stream_args)
    assert stream.get_start_timestamp(stream_state) == pendulum.parse(expected_start_timestamp).int_timestamp


@pytest.mark.parametrize("sync_mode", ("full_refresh", "incremental"))
def test_updated_cursor_incremental_stream_slices(credit_notes, sync_mode):
    stream = credit_notes()
    assert list(stream.stream_slices(sync_mode)) == [{}]


@pytest.mark.parametrize(
    "last_record, stream_state, expected_state",
    (
        ({"updated": 110}, {"updated": 111}, {"updated": 111}),
        ({"created": 110}, {"updated": 111}, {"updated": 111})
    )
)
def test_updated_cursor_incremental_stream_get_updated_state(credit_notes, last_record, stream_state, expected_state):
    stream = credit_notes()
    assert stream.get_updated_state(last_record, stream_state) == expected_state


@pytest.mark.parametrize("sync_mode", ("full_refresh", "incremental"))
def test_updated_cursor_incremental_stream_read_wo_state(requests_mock, sync_mode, credit_notes):
    requests_mock.get(
        "/v1/credit_notes",
        [
            {
                "json": {
                    "data": [{
                        "id": "cn_1NGPwmEcXtiJtvvhNXwHpgJF", "object": "credit_note", "amount": 8400, "amount_shipping": 0,
                        "created": 1686158100
                    }, {
                        "id": "cn_JtvvhNXwHpgJF1NGPwmEcXti", "object": "credit_note", "amount": 350, "amount_shipping": 150,
                        "created": 1685861100
                    }],
                    "has_more": False
                }
            }
        ]
    )
    stream = credit_notes()
    records = [record for record in stream.read_records(sync_mode)]
    assert records == [
        {"id": "cn_1NGPwmEcXtiJtvvhNXwHpgJF", "object": "credit_note", "amount": 8400, "amount_shipping": 0,
         "updated": 1686158100, "created": 1686158100},
        {"id": "cn_JtvvhNXwHpgJF1NGPwmEcXti", "object": "credit_note", "amount": 350, "amount_shipping": 150,
         "created": 1685861100, "updated": 1685861100}
    ]


@freezegun.freeze_time("2023-08-23T00:00:00")
def test_updated_cursor_incremental_stream_read_w_state(requests_mock, credit_notes):
    requests_mock.get(
        "/v1/events",
        [
            {
                "json": {
                    "data": [
                        {
                            "id": "evt_1NdNFoEcXtiJtvvhBP5mxQmL", "object": "event", "api_version": "2020-08-27", "created": 1691629292,
                            "data": {
                                "object": {"object": "credit_note", "invoice": "in_1K9GK0EcXtiJtvvhSo2LvGqT", "created": 1653341716}
                            },
                            "type": "credit_note.voided"
                        }
                    ],
                    "has_more": False
                }
            }
        ]
    )

    stream = credit_notes()
    records = [record for record in stream.read_records('incremental', stream_state={"updated": pendulum.parse("2023-01-01T15:00:15Z").int_timestamp})]
    assert records == [
        {"object": "credit_note", "invoice": "in_1K9GK0EcXtiJtvvhSo2LvGqT", "created": 1653341716, "updated": 1691629292}
    ]


def test_checkout_session_line_items(requests_mock):

    session_id_missed = "cs_test_a165K4wNihuJlp2u3tknuohrvjAxyXFUB7nxZH3lwXRKJsadNEvIEWMUJ9"
    session_id_exists = "cs_test_a1RjRHNyGUQOFVF3OkL8V8J0lZUASyVoCtsnZYG74VrBv3qz4245BLA1BP"

    response_sessions = {
        "data": [{"id": session_id_missed, "expires_at": 100_000}, {"id": session_id_exists, "expires_at": 100_000}],
        "has_more": False,
        "object": "list",
        "url": "/v1/checkout/sessions",
    }

    response_sessions_line_items = {
        "data": [{"id": "li_1JpAUUIEn5WyEQxnfGJT5MbL"}],
        "has_more": False,
        "object": "list",
        "url": "/v1/checkout/sessions/{}/line_items".format(session_id_exists),
    }

    response_error = {
        "error": {
            "code": "resource_missing",
            "doc_url": "https://stripe.com/docs/error-codes/resource-missing",
            "message": "No such checkout session: '{}'".format(session_id_missed),
            "param": "session",
            "type": "invalid_request_error",
        }
    }

    requests_mock.get("https://api.stripe.com/v1/checkout/sessions", json=response_sessions)
    requests_mock.get(
        "https://api.stripe.com/v1/checkout/sessions/{}/line_items".format(session_id_exists), json=response_sessions_line_items
    )
    requests_mock.get(
        "https://api.stripe.com/v1/checkout/sessions/{}/line_items".format(session_id_missed), json=response_error, status_code=404
    )

    stream = CheckoutSessionsLineItems(start_date=100_100, account_id=None)
    records = []
    for slice_ in stream.stream_slices(sync_mode="full_refresh"):
        records.extend(stream.read_records(sync_mode="full_refresh", stream_slice=slice_))
    assert len(records) == 1


def test_customer_balance_transactions_stream_slices(requests_mock, stream_args):
    stream_args["start_date"] = pendulum.now().subtract(days=1).int_timestamp
    requests_mock.get(
        "/v1/customers",
        json={
            "data": [
                {"id": 1, "next_invoice_sequence": 1, "balance": 0, "created": 1653341716},
                {"id": 2, "created": 1653341000},
                {"id": 3, "next_invoice_sequence": 13, "balance": 343.43, "created": 1651716334}
            ]
        }
    )
    stream = CustomerBalanceTransactions(**stream_args)
    assert list(stream.stream_slices("full_refresh")) == [
        {"id": 2, "created": 1653341000, "updated": 1653341000}, {"id": 3, "next_invoice_sequence": 13, "balance": 343.43, "created": 1651716334, "updated": 1651716334}
    ]


@freezegun.freeze_time("2023-08-23T15:00:15Z")
def test_setup_attempts(requests_mock, incremental_stream_args):
    requests_mock.get(
        "/v1/setup_intents",
        [{"json": {"data": [{"id": 1, "created": 111, "object": "setup_intent"}]}}, {"json":{"data":[{"id": 2, "created": 222, "object": "setup_intent"}]}}]
    )
    requests_mock.get(
        "/v1/setup_attempts",
        [{"json": {"data": [{"id": 1, "created": 112, "object": "setup_attempt"}]}},
         {"json": {"data": [{"id": 2, "created": 230, "object": "setup_attempt"}]}},
         {"json": {"data": [{"id": 3, "created": 345, "object": "setup_attempt"}]}},
         {"json": {"data": [{"id": 4, "created": 450, "object": "setup_attempt"}]}}]
    )
    incremental_stream_args["slice_range"] = 1
    incremental_stream_args["lookback_window_days"] = 0
    incremental_stream_args["start_date"] = pendulum.now().subtract(days=2).int_timestamp
    stream = SetupAttempts(**incremental_stream_args)
    slices = list(stream.stream_slices("full_refresh"))
    assert slices == [
        {"created[gte]": 1692630015, "created[lte]": 1692716415, "parent": {"id": 1, "created": 111, "updated": 111, "object": "setup_intent"}},
        {"created[gte]": 1692716416, "created[lte]": 1692802815,
         "parent": {"id": 1, "created": 111, "updated": 111, "object": "setup_intent"}},
        {"created[gte]": 1692630015, "created[lte]": 1692716415, "parent": {"id": 2, "created": 222, "updated": 222, "object": "setup_intent"}},
        {"created[gte]": 1692716416, "created[lte]": 1692802815, "parent": {"id": 2, "created": 222, "updated": 222, "object": "setup_intent"}}
    ]
    records = []
    for slice_ in slices:
        for record in stream.read_records("full_refresh", stream_slice=slice_):
            records.append(record)
    assert records == [
        {"id": 1, "created": 112, "object": "setup_attempt"},
        {"id": 2, "created": 230, "object": "setup_attempt"},
        {"id": 3, "created": 345, "object": "setup_attempt"},
        {"id": 4, "created": 450, "object": "setup_attempt"}
    ]


def test_persons_wo_state(requests_mock, incremental_stream_args):
    requests_mock.get(
        "/v1/accounts",
        json={"data": [{"id": 1, "object": "account", "created": 111}]}
    )
    stream = Persons(**incremental_stream_args)
    slices = list(stream.stream_slices("full_refresh"))
    assert slices == [{"parent": {"id": 1, "object": "account", "created": 111}}]
    requests_mock.get(
        "/v1/accounts/1/persons",
        json={"data": [{"id": 11, "object": "person", "created": 222}]}
    )
    records = []
    for slice_ in slices:
        for record in stream.read_records("full_refresh", stream_slice=slice_):
            records.append(record)
    assert records == [{"id": 11, "object": "person", "created": 222, "updated": 222}]


@freezegun.freeze_time("2023-08-23T15:00:15")
def test_persons_w_state(requests_mock, incremental_stream_args):
    requests_mock.get(
        "/v1/events",
        json={
            "data": [
                {
                    "id": "evt_1NdNFoEcXtiJtvvhBP5mxQmL", "object": "event", "api_version": "2020-08-27", "created": 1691629292, "data": {
                        "object": {
                            "object": "person", "name": "John", "created": 1653341716
                        }
                    },
                    "type": "credit_note.voided"
                }
            ],
            "has_more": False
        }
    )
    stream = Persons(**incremental_stream_args)
    slices = list(stream.stream_slices("incremental", stream_state={"updated": pendulum.parse("2023-08-20T00:00:00").int_timestamp}))
    assert slices == [{}]
    records = [
        record for record in stream.read_records("incremental", stream_state={"updated": pendulum.parse("2023-08-20T00:00:00").int_timestamp})
    ]
    assert records == [{"object": "person", "name": "John", "created": 1653341716, "updated": 1691629292}]
