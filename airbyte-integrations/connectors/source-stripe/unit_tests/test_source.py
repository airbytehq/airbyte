#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from contextlib import nullcontext as does_not_raise
from unittest.mock import patch

import pytest
import source_stripe
import stripe
from airbyte_cdk.utils import AirbyteTracedException
from source_stripe import SourceStripe

logger = logging.getLogger("airbyte")


def _a_valid_config():
    return {"account_id": 1, "client_secret": "secret"}


@patch.object(source_stripe.source, "stripe")
def test_source_check_connection_ok(mocked_client, config):
    assert SourceStripe().check_connection(logger, config=config) == (True, None)


def test_streams_are_unique(config):
    stream_names = [s.name for s in SourceStripe().streams(config=config)]
    assert len(stream_names) == len(set(stream_names)) == 46


@pytest.mark.parametrize(
    "input_config, expected_error_msg",
    (
        ({"lookback_window_days": "month"}, "Invalid lookback window month. Please use only positive integer values or 0."),
        ({"start_date": "January First, 2022"}, "Invalid start date January First, 2022. Please use YYYY-MM-DDTHH:MM:SSZ format."),
        ({"slice_range": -10}, "Invalid slice range value -10. Please use positive integer values only."),
        (_a_valid_config(), None)
    )
)
@patch.object(source_stripe.source.stripe, "Account")
def test_config_validation(mocked_client, input_config, expected_error_msg):
    context = pytest.raises(AirbyteTracedException, match=expected_error_msg) if expected_error_msg else does_not_raise()
    with context:
        SourceStripe().check_connection(logger, config=input_config)


@pytest.mark.parametrize(
    "exception",
    (
        stripe.error.AuthenticationError,
        stripe.error.PermissionError,
    )
)
@patch.object(source_stripe.source.stripe, "Account")
def test_given_stripe_error_when_check_connection_then_connection_not_available(mocked_client, exception):
    mocked_client.retrieve.side_effect = exception
    is_available, _ = SourceStripe().check_connection(logger, config=_a_valid_config())
    assert not is_available
