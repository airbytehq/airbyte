#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import pytest
from airbyte_cdk.models import ConnectorSpecification
from source_instagram.source import SourceInstagram, ConnectorConfig
import logging
from facebook_business import FacebookAdsApi, FacebookSession

FB_API_VERSION = FacebookAdsApi.API_VERSION

logger = logging.getLogger("test_client")


def test_check_connection_ok(api, some_config):
    ok, error_msg = SourceInstagram().check_connection(logger, config=some_config)

    assert ok
    assert not error_msg


def test_check_connection_empty_config(api):
    config = {}
    ok, error_msg = SourceInstagram().check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_check_connection_invalid_config(api, some_config):
    some_config.pop("start_date")
    ok, error_msg = SourceInstagram().check_connection(logger, config=some_config)

    assert not ok
    assert error_msg


def test_check_connection_exception(api, some_config):
    api.side_effect = RuntimeError("Something went wrong!")
    ok, error_msg = SourceInstagram().check_connection(logger, config=some_config)

    assert not ok
    assert error_msg


def test_streams(api, config):
    streams = SourceInstagram().streams(config)

    assert len(streams) == 7


def test_spec():
    spec = SourceInstagram().spec()

    assert isinstance(spec, ConnectorSpecification)
