#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_stripe.streams import IncrementalStripeStream, StripeLazySubStream


@pytest.fixture(name="config")
def config_fixture():
    config = {"client_secret": "sk_test(live)_<secret>",
              "account_id": "<account_id>", "start_date": "2020-05-01T00:00:00Z"}
    return config


@pytest.fixture(name="stream_args")
def stream_args_fixture():
    authenticator = TokenAuthenticator("sk_test(live)_<secret>")
    args = {
        "authenticator": authenticator,
        "account_id": "<account_id>",
        "start_date": 1588315041,
        "slice_range": 365,
    }
    return args


@pytest.fixture(name="incremental_stream_args")
def incremental_args_fixture(stream_args):
    return {
        "lookback_window_days": 14,
        **stream_args
    }


@pytest.fixture(name="invoices")
def invoices_fixture(stream_args):
    def mocker(args=stream_args):
        return IncrementalStripeStream(
            name="invoices",
            path="invoices",
            use_cache=False,
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
            **args
        )
    return mocker


@pytest.fixture(name="invoice_line_items")
def invoice_line_items_fixture(invoices, stream_args):
    parent_stream = invoices()

    def mocker(args=stream_args, parent_stream=parent_stream):
        return StripeLazySubStream(
            name="invoice_line_items",
            path=lambda self, *args, stream_slice, **kwargs: f"invoices/{stream_slice[self.parent_id]}/lines",
            parent=parent_stream,
            parent_id="invoice_id",
            sub_items_attr="lines",
            add_parent_id=True,
            **args,
        )
    return mocker
