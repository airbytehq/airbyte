#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pendulum
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from source_stripe.availability_strategy import StripeSubStreamAvailabilityStrategy
from source_stripe.streams import InvoiceLineItems, Invoices


def test_traverse_over_substreams(mocker):
    # Mock base HttpAvailabilityStrategy to capture all the check_availability method calls
    check_availability_mock = mocker.MagicMock()
    check_availability_mock.return_value = (True, None)
    mocker.patch(
        "airbyte_cdk.sources.streams.http.availability_strategy.HttpAvailabilityStrategy.check_availability",
        check_availability_mock
    )

    # Prepare tree of nested objects
    root = mocker.Mock()
    root.availability_strategy = HttpAvailabilityStrategy()
    root.parent = None

    child_1 = mocker.Mock()
    child_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1.get_parent_stream_instance.return_value = root

    child_1_1 = mocker.Mock()
    child_1_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1_1.get_parent_stream_instance.return_value = child_1

    child_1_1_1 = mocker.Mock()
    child_1_1_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1_1_1.get_parent_stream_instance.return_value = child_1_1

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
        "airbyte_cdk.sources.streams.http.availability_strategy.HttpAvailabilityStrategy.check_availability",
        check_availability_mock
    )

    # Prepare tree of nested objects
    root = mocker.Mock()
    root.availability_strategy = HttpAvailabilityStrategy()
    root.parent = None

    child_1 = mocker.Mock()
    child_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1.get_parent_stream_instance.return_value = root

    child_1_1 = mocker.Mock()
    child_1_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1_1.get_parent_stream_instance.return_value = child_1

    child_1_1_1 = mocker.Mock()
    child_1_1_1.availability_strategy = StripeSubStreamAvailabilityStrategy()
    child_1_1_1.get_parent_stream_instance.return_value = child_1_1

    # Start traverse
    is_available, reason = child_1_1_1.availability_strategy.check_availability(child_1_1_1, mocker.Mock(), mocker.Mock())

    assert not is_available and reason == "child_1"

    # Check availability strategy was called once for every nested object
    assert check_availability_mock.call_count == 2

    # Check each availability strategy was called with proper instance argument
    assert id(check_availability_mock.call_args_list[0].args[0]) == id(root)
    assert id(check_availability_mock.call_args_list[1].args[0]) == id(child_1)


def test_substream_availability(mocker):
    check_availability_mock = mocker.MagicMock()
    check_availability_mock.return_value = (True, None)
    mocker.patch(
        "airbyte_cdk.sources.streams.http.availability_strategy.HttpAvailabilityStrategy.check_availability",
        check_availability_mock
    )

    stream = InvoiceLineItems(start_date=pendulum.today().subtract(days=3).int_timestamp, account_id="None")
    is_available, reason = stream.availability_strategy.check_availability(stream, mocker.Mock(), mocker.Mock())
    assert is_available and reason is None

    assert check_availability_mock.call_count == 2
    assert isinstance(check_availability_mock.call_args_list[0].args[0], Invoices)
    assert isinstance(check_availability_mock.call_args_list[1].args[0], InvoiceLineItems)


def test_substream_availability_no_parent(mocker):
    check_availability_mock = mocker.MagicMock()
    check_availability_mock.return_value = (True, None)
    mocker.patch(
        "airbyte_cdk.sources.streams.http.availability_strategy.HttpAvailabilityStrategy.check_availability",
        check_availability_mock
    )

    stream = InvoiceLineItems(start_date=pendulum.today().subtract(days=3).int_timestamp, account_id="None")
    stream.parent = None

    stream.availability_strategy.check_availability(stream, mocker.Mock(), mocker.Mock())

    assert check_availability_mock.call_count == 1
    assert isinstance(check_availability_mock.call_args_list[0].args[0], InvoiceLineItems)
