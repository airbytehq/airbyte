#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import urllib.parse

import pytest
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from source_stripe.availability_strategy import STRIPE_ERROR_CODES, StripeSubStreamAvailabilityStrategy
from source_stripe.streams import IncrementalStripeStream, StripeLazySubStream


@pytest.fixture()
def stream_mock(mocker):
    def _mocker():
        return mocker.Mock(stream_slices=mocker.Mock(return_value=[{}]), read_records=mocker.Mock(return_value=[{}]))
    return _mocker


def test_traverse_over_substreams(stream_mock, mocker):
    # Mock base HttpAvailabilityStrategy to capture all the check_availability method calls
    check_availability_mock = mocker.MagicMock(return_value=(True, None))
    cdk_check_availability_mock = mocker.MagicMock(return_value=(True, None))
    mocker.patch(
        "source_stripe.availability_strategy.StripeAvailabilityStrategy.check_availability", check_availability_mock
    )
    mocker.patch(
        "airbyte_cdk.sources.streams.http.availability_strategy.HttpAvailabilityStrategy.check_availability", cdk_check_availability_mock
    )
    # Prepare tree of nested objects
    root = stream_mock()
    root.availability_strategy = HttpAvailabilityStrategy()
    root.parent = None

    child_1 = stream_mock()
    child_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1.parent = root

    child_1_1 = stream_mock()
    child_1_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1_1.parent = child_1

    child_1_1_1 = stream_mock()
    child_1_1_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1_1_1.parent = child_1_1

    # Start traverse
    is_available, reason = child_1_1_1.availability_strategy.check_availability(child_1_1_1, mocker.Mock(), mocker.Mock())

    assert is_available and reason is None
    # Check availability strategy was called once for every nested object
    assert check_availability_mock.call_count == 3
    assert cdk_check_availability_mock.call_count == 1

    # Check each availability strategy was called with proper instance argument
    assert id(cdk_check_availability_mock.call_args_list[0].args[0]) == id(root)
    assert id(check_availability_mock.call_args_list[0].args[0]) == id(child_1)
    assert id(check_availability_mock.call_args_list[1].args[0]) == id(child_1_1)
    assert id(check_availability_mock.call_args_list[2].args[0]) == id(child_1_1_1)


def test_traverse_over_substreams_failure(stream_mock, mocker):
    # Mock base HttpAvailabilityStrategy to capture all the check_availability method calls
    check_availability_mock = mocker.MagicMock(side_effect=[(True, None), (False, "child_1")])
    mocker.patch(
        "source_stripe.availability_strategy.StripeAvailabilityStrategy.check_availability", check_availability_mock
    )

    # Prepare tree of nested objects
    root = stream_mock()
    root.availability_strategy = HttpAvailabilityStrategy()
    root.parent = None

    child_1 = stream_mock()
    child_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1.parent = root

    child_1_1 = stream_mock()
    child_1_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1_1.parent = child_1

    child_1_1_1 = stream_mock()
    child_1_1_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1_1_1.parent = child_1_1

    # Start traverse
    is_available, reason = child_1_1_1.availability_strategy.check_availability(child_1_1_1, mocker.Mock(), mocker.Mock())

    assert not is_available and reason == "child_1"

    # Check availability strategy was called once for every nested object
    assert check_availability_mock.call_count == 2

    # Check each availability strategy was called with proper instance argument
    assert id(check_availability_mock.call_args_list[0].args[0]) == id(child_1)
    assert id(check_availability_mock.call_args_list[1].args[0]) == id(child_1_1)


def test_substream_availability(mocker, stream_by_name):
    check_availability_mock = mocker.MagicMock()
    check_availability_mock.return_value = (True, None)
    mocker.patch(
        "source_stripe.availability_strategy.StripeAvailabilityStrategy.check_availability", check_availability_mock
    )
    stream = stream_by_name("invoice_line_items")
    is_available, reason = stream.availability_strategy.check_availability(stream, mocker.Mock(), mocker.Mock())
    assert is_available and reason is None

    assert check_availability_mock.call_count == 2
    assert isinstance(check_availability_mock.call_args_list[0].args[0], IncrementalStripeStream)
    assert isinstance(check_availability_mock.call_args_list[1].args[0], StripeLazySubStream)


def test_substream_availability_no_parent(mocker, stream_by_name):
    check_availability_mock = mocker.MagicMock()
    check_availability_mock.return_value = (True, None)
    mocker.patch(
        "source_stripe.availability_strategy.StripeAvailabilityStrategy.check_availability", check_availability_mock
    )
    stream = stream_by_name("invoice_line_items")
    stream.parent = None

    stream.availability_strategy.check_availability(stream, mocker.Mock(), mocker.Mock())

    assert check_availability_mock.call_count == 1
    assert isinstance(check_availability_mock.call_args_list[0].args[0], StripeLazySubStream)


def test_403_error_handling(stream_by_name, requests_mock):
    stream = stream_by_name("invoices")
    logger = logging.getLogger("airbyte")
    for error_code in STRIPE_ERROR_CODES:
        requests_mock.get(f"{stream.url_base}{stream.path()}", status_code=403, json={"error": {"code": f"{error_code}"}})
        available, message = stream.check_availability(logger)
        assert not available
        assert STRIPE_ERROR_CODES[error_code] in message


@pytest.mark.parametrize(
    "stream_name, endpoints, expected_calls",
    (
        (
            "accounts",
            {
                "/v1/accounts": {"data": []}
            },
            1
        ),
        (
            "refunds",
            {
                "/v1/refunds": {"data": []}
            },
            2
        ),
        (
            "credit_notes",
            {
                "/v1/credit_notes": {"data": []}, "/v1/events": {"data": []}
            },
            2
        ),
        (
            "charges",
            {
                "/v1/charges": {"data": []}, "/v1/events": {"data": []}
            },
            2
        ),
        (
            "subscription_items",
            {
                "/v1/subscriptions": {"data": [{"id": 1}]},
                "/v1/events": {"data": []}
            },
            3
        ),
        (
            "bank_accounts",
            {
                "/v1/customers": {"data": [{"id": 1}]},
                "/v1/events": {"data": []}
            },
            2
        ),
        (
            "customer_balance_transactions",
            {
                "/v1/events": {"data": [{"data":{"object": {"id": 1}}, "created": 1, "type": "customer.updated"}]},
                "/v1/customers": {"data": [{"id": 1}]},
                "/v1/customers/1/balance_transactions": {"data": []}
            },
            4
        ),
        (
            "transfer_reversals",
            {
                "/v1/transfers": {"data": [{"id": 1}]},
                "/v1/events": {"data": [{"data":{"object": {"id": 1}}, "created": 1, "type": "transfer.updated"}]},
                "/v1/transfers/1/reversals": {"data": []}
            },
            4
        ),
        (
            "persons",
            {
                "/v1/accounts": {"data": [{"id": 1}]},
                "/v1/events": {"data": []},
                "/v1/accounts/1/persons": {"data": []}
            },
            4
        )
    )
)
def test_availability_strategy_visits_endpoints(stream_by_name, stream_name, endpoints, expected_calls, requests_mock, mocker, config):
    for endpoint, data in endpoints.items():
        requests_mock.get(endpoint, json=data)
    stream = stream_by_name(stream_name, config)
    is_available, reason = stream.check_availability(mocker.Mock(), mocker.Mock())
    assert (is_available, reason) == (True, None)
    assert len(requests_mock.request_history) == expected_calls

    for call in requests_mock.request_history:
        assert urllib.parse.urlparse(call.url).path in endpoints.keys()
