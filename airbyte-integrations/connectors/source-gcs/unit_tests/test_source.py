# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import re
from unittest.mock import Mock

import pytest
from common import catalog_path, config_path
from source_gcs import Config, Cursor, SourceGCS, SourceGCSStreamReader

from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.sources.file_based.availability_strategy import DefaultFileBasedAvailabilityStrategy


def _source_gcs(catalog, config):
    return SourceGCS(
        SourceGCSStreamReader(),
        Config,
        catalog,
        config,
        None,
        cursor_cls=Cursor,
    )


def _mock_encoding_error():
    DefaultFileBasedAvailabilityStrategy.check_availability_and_parsability = Mock(
        side_effect=AirbyteTracedException(message="encoding error")
    )


def test_check_connection_with_airbyte_traced_exception(logger):
    config = SourceGCS.read_config(f"{config_path()}/config_bad_encoding_single_stream.json")
    catalog = SourceGCS.read_catalog(f"{catalog_path()}/catalog_bad_encoding.json")
    source = _source_gcs(catalog, config)
    _mock_encoding_error()

    with pytest.raises(AirbyteTracedException) as ate:
        source.check_connection(logger, config)

    assert re.search(r"^Unable to connect.+encoding error", ate.value.message)


def test_check_connection_with_airbyte_traced_exception_multiple_failures(logger):
    config = SourceGCS.read_config(f"{config_path()}/config_bad_encoding.json")
    catalog = SourceGCS.read_catalog(f"{catalog_path()}/catalog_bad_encoding.json")
    source = _source_gcs(catalog, config)
    _mock_encoding_error()

    with pytest.raises(AirbyteTracedException) as ate:
        source.check_connection(logger, config)

    assert re.search(r"2 streams with errors.+encoding error", ate.value.message)


def test_read_config_with_invalid_legacy_config(logger):
    with pytest.raises(ValueError):
        SourceGCS.read_config(f"{config_path()}/config_legacy.json")
