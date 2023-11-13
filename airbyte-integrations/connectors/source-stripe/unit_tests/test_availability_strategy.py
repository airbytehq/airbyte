#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from source_stripe.availability_strategy import STRIPE_ERROR_CODES, StripeSubStreamAvailabilityStrategy
from source_stripe.streams import IncrementalStripeStream, StripeLazySubStream


def test_traverse_over_substreams(mocker):
    # Mock base HttpAvailabilityStrategy to capture all the check_availability method calls
    check_availability_mock = mocker.MagicMock()
    check_availability_mock.return_value = (True, None)
    mocker.patch(
        "airbyte_cdk.sources.streams.http.availability_strategy.HttpAvailabilityStrategy.check_availability", check_availability_mock
    )

    # Prepare tree of nested objects
    root = mocker.Mock()
    root.availability_strategy = HttpAvailabilityStrategy()
    root.parent = None

    child_1 = mocker.Mock()
    child_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1.parent = root

    child_1_1 = mocker.Mock()
    child_1_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1_1.parent = child_1

    child_1_1_1 = mocker.Mock()
    child_1_1_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1_1_1.parent = child_1_1

    # Start traverse
    is_available, reason = child_1_1_1.availability_strategy.check_availability(child_1_1_1, mocker.Mock(), mocker.Mock())

    assert is_available and reason is None

    # Check availability strategy was called once for every nested object
    assert check_availability_mock.call_count == 4

    # Check each availability strategy was called with proper instance argument
    assert id(check_availability_mock.call_args_list[0].args[0]) == id(root)
    assert id(check_availability_mock.call_args_list[1].args[0]) == id(child_1)
    assert id(check_availability_mock.call_args_list[2].args[0]) == id(child_1_1)
    assert id(check_availability_mock.call_args_list[3].args[0]) == id(child_1_1_1)


def test_traverse_over_substreams_failure(mocker):
    # Mock base HttpAvailabilityStrategy to capture all the check_availability method calls
    check_availability_mock = mocker.MagicMock()
    check_availability_mock.side_effect = [(True, None), (False, "child_1")]
    mocker.patch(
        "airbyte_cdk.sources.streams.http.availability_strategy.HttpAvailabilityStrategy.check_availability", check_availability_mock
    )

    # Prepare tree of nested objects
    root = mocker.Mock()
    root.availability_strategy = HttpAvailabilityStrategy()
    root.parent = None

    child_1 = mocker.Mock()
    child_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1.parent = root

    child_1_1 = mocker.Mock()
    child_1_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1_1.parent = child_1

    child_1_1_1 = mocker.Mock()
    child_1_1_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1_1_1.parent = child_1_1

    # Start traverse
    is_available, reason = child_1_1_1.availability_strategy.check_availability(child_1_1_1, mocker.Mock(), mocker.Mock())

    assert not is_available and reason == "child_1"

    # Check availability strategy was called once for every nested object
    assert check_availability_mock.call_count == 2

    # Check each availability strategy was called with proper instance argument
    assert id(check_availability_mock.call_args_list[0].args[0]) == id(root)
    assert id(check_availability_mock.call_args_list[1].args[0]) == id(child_1)


def test_substream_availability(mocker, stream_by_name):
    check_availability_mock = mocker.MagicMock()
    check_availability_mock.return_value = (True, None)
    mocker.patch(
        "airbyte_cdk.sources.streams.http.availability_strategy.HttpAvailabilityStrategy.check_availability", check_availability_mock
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
        "airbyte_cdk.sources.streams.http.availability_strategy.HttpAvailabilityStrategy.check_availability", check_availability_mock
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
