#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import Mock, patch

import source_stripe
from source_stripe import SourceStripe

logger = logging.getLogger("airbyte")


@patch.object(source_stripe.source, "stripe")
def test_source_check_connection_ok(config):
    assert SourceStripe().check_connection(logger, config=config) == (True, None)


@patch.object(source_stripe.source, "stripe")
def test_source_check_connection_failure(mocked_client, config):
    exception = Exception("Test")
    mocked_client.Account.retrieve = Mock(side_effect=exception)
    assert SourceStripe().check_connection(logger, config=config) == (False, exception)


def test_streams_are_unique(config):
    stream_names = [s.name for s in SourceStripe().streams(config=config)]
    assert len(stream_names) == len(set(stream_names)) == 46
