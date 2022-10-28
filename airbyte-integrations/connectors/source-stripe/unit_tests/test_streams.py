#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pendulum
import pytest
from airbyte_cdk.models import SyncMode
from source_stripe.streams import (
    BalanceTransactions,
    BankAccounts,
    Charges,
    CheckoutSessions,
    CheckoutSessionsLineItems,
    Coupons,
    CustomerBalanceTransactions,
    Customers,
    Disputes,
    Events,
    ExternalAccount,
    ExternalAccountBankAccounts,
    ExternalAccountCards,
    InvoiceItems,
    InvoiceLineItems,
    Invoices,
    PaymentIntents,
    Payouts,
    Plans,
    Products,
    PromotionCodes,
    Refunds,
    SubscriptionItems,
    Subscriptions,
    Transfers,
)


def test_missed_id_child_stream(requests_mock):

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
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh))
    assert len(records) == 1


def test_sub_stream(requests_mock):

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
    start_date = pendulum.today().subtract(days=3).int_timestamp
    stream = InvoiceLineItems(start_date=start_date, account_id="None")
    records = stream.read_records(sync_mode=SyncMode.full_refresh)
    assert list(records) == [
        {"id": "il_1", "invoice_id": "in_1KD6OVIEn5WyEQxn9xuASHsD", "object": "line_item"},
        {"id": "il_2", "invoice_id": "in_1KD6OVIEn5WyEQxn9xuASHsD", "object": "line_item"},
        {"id": "il_3", "invoice_id": "in_1KD6OVIEn5WyEQxn9xuASHsD", "object": "line_item"},
    ]


@pytest.fixture(name="config")
def config_fixture():
    config = {"authenticator": "authenticator", "account_id": "<account_id>", "start_date": 1596466368}
    return config


@pytest.mark.parametrize(
    "stream, kwargs, expected",
    [
        (Customers, {}, "customers"),
        (BalanceTransactions, {}, "balance_transactions"),
        (Charges, {}, "charges"),
        (CustomerBalanceTransactions, {"stream_slice": {"customer_id": "C1"}}, "customers/C1/balance_transactions"),
        (Coupons, {}, "coupons"),
        (Disputes, {}, "disputes"),
        (Events, {}, "events"),
        (Invoices, {}, "invoices"),
        (InvoiceLineItems, {"stream_slice": {"invoice_id": "I1"}}, "invoices/I1/lines"),
        (InvoiceItems, {}, "invoiceitems"),
        (Payouts, {}, "payouts"),
        (Plans, {}, "plans"),
        (Products, {}, "products"),
        (Subscriptions, {}, "subscriptions"),
        (SubscriptionItems, {}, "subscription_items"),
        (Transfers, {}, "transfers"),
        (Refunds, {}, "refunds"),
        (PaymentIntents, {}, "payment_intents"),
        (BankAccounts, {"stream_slice": {"customer_id": "C1"}}, "customers/C1/sources"),
        (CheckoutSessions, {}, "checkout/sessions"),
        (CheckoutSessionsLineItems, {"stream_slice": {"checkout_session_id": "CS1"}}, "checkout/sessions/CS1/line_items"),
        (PromotionCodes, {}, "promotion_codes"),
        (ExternalAccount, {}, "accounts/<account_id>/external_accounts"),
    ],
)
def test_path(
    stream,
    kwargs,
    expected,
    config,
):
    assert stream(**config).path(**kwargs) == expected


@pytest.mark.parametrize(
    "stream, kwargs, expected",
    [
        (
            CustomerBalanceTransactions,
            {"stream_state": {}, "stream_slice": {"created[gte]": 1596466368, "created[lte]": 1596552768}},
            {"limit": 100, "created[gte]": 1596466368, "created[lte]": 1596552768},
        ),
        (
            Customers,
            {"stream_state": {}, "stream_slice": {"created[gte]": 1596466368, "created[lte]": 1596552768}},
            {"created[gte]": 1596466368, "created[lte]": 1596552768, "limit": 100},
        ),
        (InvoiceLineItems, {"stream_state": {}, "stream_slice": {"starting_after": "2030"}}, {"limit": 100, "starting_after": "2030"}),
        (
            Subscriptions,
            {"stream_slice": {"created[gte]": 1596466368, "created[lte]": 1596552768}},
            {"created[gte]": 1596466368, "limit": 100, "status": "all", "created[lte]": 1596552768},
        ),
        (SubscriptionItems, {"stream_state": {}, "stream_slice": {"subscription_id": "SI"}}, {"limit": 100, "subscription": "SI"}),
        (BankAccounts, {"stream_state": {}, "stream_slice": {"subscription_id": "SI"}}, {"limit": 100, "object": "bank_account"}),
        (CheckoutSessions, {"stream_state": None, "stream_slice": {}}, {"limit": 100}),
        (
            CheckoutSessionsLineItems,
            {"stream_state": None, "stream_slice": {}},
            {"limit": 100, "expand[]": ["data.discounts", "data.taxes"]},
        ),
        (ExternalAccountBankAccounts, {"stream_state": None, "stream_slice": {}}, {"limit": 100, "object": "bank_account"}),
        (ExternalAccountCards, {"stream_state": None, "stream_slice": {}}, {"limit": 100, "object": "card"}),
    ],
)
def test_request_params(
    stream,
    kwargs,
    expected,
    config,
):
    assert stream(**config).request_params(**kwargs) == expected
