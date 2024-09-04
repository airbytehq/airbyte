# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import re
from pathlib import Path
from unittest.mock import Mock

import pytest
from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.sources.file_based.availability_strategy import DefaultFileBasedAvailabilityStrategy
from source_gcs import Config, Cursor, SourceGCS, SourceGCSStreamReader


def _source_gcs(catalog, config):
    return SourceGCS(
        SourceGCSStreamReader(),
        Config,
        catalog,
        config,
        None,
        cursor_cls=Cursor,
    )


def _catalog_path():
    return Path(__file__).resolve().parent.joinpath("resource/catalog/")


def _config_path():
    return Path(__file__).resolve().parent.joinpath("resource/config/")


def _mock_encoding_error():
    DefaultFileBasedAvailabilityStrategy.check_availability_and_parsability = Mock(side_effect=AirbyteTracedException(message="encoding error"))


def test_check_connection_with_airbyte_traced_exception(logger):
    config = SourceGCS.read_config(f"{_config_path()}/config_bad_encoding_single_stream.json")
    catalog = SourceGCS.read_catalog(f"{_catalog_path()}/catalog_bad_encoding.json")
    source = _source_gcs(catalog, config)
    _mock_encoding_error()

    with pytest.raises(AirbyteTracedException) as ate:
        source.check_connection(logger, config)

    assert re.search(r"^Unable to connect.+encoding error", ate.value.message)


def test_check_connection_with_airbyte_traced_exception_multiple_failures(logger):
    config = SourceGCS.read_config(f"{_config_path()}/config_bad_encoding.json")
    catalog = SourceGCS.read_catalog(f"{_catalog_path()}/catalog_bad_encoding.json")
    source = _source_gcs(catalog, config)
    _mock_encoding_error()

    with pytest.raises(AirbyteTracedException) as ate:
        source.check_connection(logger, config)

    assert re.search(r"2 streams with errors.+encoding error", ate.value.message)
