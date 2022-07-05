#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import Mock

import pytest
from source_smartsheets.source import SourceSmartsheets
from source_smartsheets.streams import SmartsheetStream


@pytest.mark.parametrize("connection_status", ((True, None), (False, "Internal Server Error")))
def test_check_connection(mocker, config, connection_status):
    mocker.patch("source_smartsheets.source.SmartSheetAPIWrapper.check_connection", Mock(return_value=connection_status))
    source = SourceSmartsheets()
    assert source.check_connection(logger=logging.getLogger(), config=config) == connection_status


def test_streams(config):
    source = SourceSmartsheets()
    streams_iter = iter(source.streams(config))
    assert type(next(streams_iter)) == SmartsheetStream
    assert next(streams_iter, None) is None
