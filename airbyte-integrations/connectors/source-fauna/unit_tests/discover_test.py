#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, Mock

from airbyte_cdk.models import AirbyteCatalog, AirbyteStream, SyncMode
from source_fauna import SourceFauna
from test_util import config, mock_logger


def mock_source() -> SourceFauna:
    source = SourceFauna()
    source._setup_client = Mock()
    source.client = MagicMock()
    return source


def schema(properties) -> dict:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": properties,
    }


def test_simple_discover():
    source = SourceFauna()
    source._setup_client = Mock()
    source.client = MagicMock()
    source.client.query = Mock()

    logger = mock_logger()
    result = source.discover(
        logger,
        config=config(
            {
                "collection": {
                    "name": "1234",
                    "index": "",
                    "data_column": True,
                    "additional_columns": [],
                }
            }
        ),
    )
    assert result.streams == [
        AirbyteStream(
            name="1234",
            json_schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                    },
                    "ref": {
                        "type": "string",
                    },
                    "ts": {
                        "type": "integer",
                    },
                },
            },
            supported_sync_modes=["full_refresh"],
            source_defined_cursor=True,
            default_cursor_field=["ts"],
            source_defined_primary_key=None,
            namespace=None,
        )
    ]
    assert not logger.info.called
    assert not logger.error.called

    assert not source._setup_client.called
    assert not source.client.query.called


def test_discover_valid_index():
    source = SourceFauna()
    source._setup_client = Mock()
    source.client = MagicMock()
    source.client.query = Mock()

    logger = mock_logger()
    result = source.discover(
        logger,
        config=config(
            {
                "collection": {
                    "name": "1234",
                    "index": "my_index",
                    "data_column": True,
                    "additional_columns": [],
                }
            }
        ),
    )
    assert result.streams == [
        AirbyteStream(
            name="1234",
            json_schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                    },
                    "ref": {
                        "type": "string",
                    },
                    "ts": {
                        "type": "integer",
                    },
                },
            },
            supported_sync_modes=["full_refresh", "incremental"],
            source_defined_cursor=True,
            default_cursor_field=["ts"],
            source_defined_primary_key=None,
            namespace=None,
        )
    ]
    assert not logger.info.called
    assert not logger.error.called

    assert not source._setup_client.called
    assert not source.client.query.called


# Validates that the stream from discover() has the correct schema.
def test_config_columns():
    def expect_schema(collection_config, schema):
        collection_config["name"] = "my_stream_name"
        collection_config["index"] = ""
        source = mock_source()
        logger = mock_logger()
        result = source.discover(
            logger,
            config=config(
                {
                    "collection": collection_config,
                }
            ),
        )
        assert result == AirbyteCatalog(
            streams=[
                AirbyteStream(
                    name="my_stream_name",
                    json_schema=schema,
                    supported_sync_modes=[SyncMode.full_refresh],
                    default_cursor_field=["ts"],
                    source_defined_cursor=True,
                ),
            ]
        )
        assert not source.client.query.called

    expect_schema(
        {
            "data_column": True,
            "additional_columns": [],
        },
        schema(
            {
                "ref": {
                    "type": "string",
                },
                "ts": {
                    "type": "integer",
                },
                "data": {
                    "type": "object",
                },
            }
        ),
    )
    expect_schema(
        {
            "data_column": False,
            "additional_columns": [],
        },
        schema(
            {
                "ref": {
                    "type": "string",
                },
                "ts": {
                    "type": "integer",
                },
            }
        ),
    )
    expect_schema(
        {
            "data_column": False,
            "additional_columns": [
                {
                    "name": "my_column",
                    "path": ["a", "b", "c"],
                    "type": "boolean",
                    "required": True,
                }
            ],
        },
        schema(
            {
                "ref": {
                    "type": "string",
                },
                "ts": {
                    "type": "integer",
                },
                "my_column": {
                    "type": "boolean",
                },
            }
        ),
    )
    # Optional columns should be nullable (the type being [null, boolean] means it is nullable).
    expect_schema(
        {
            "data_column": False,
            "additional_columns": [
                {
                    "name": "my_column",
                    "path": ["a", "b", "c"],
                    "type": "boolean",
                    "required": False,
                }
            ],
        },
        schema(
            {
                "ref": {
                    "type": "string",
                },
                "ts": {
                    "type": "integer",
                },
                "my_column": {
                    "type": ["null", "boolean"],
                },
            }
        ),
    )
    expect_schema(
        {
            "data_column": True,
            "additional_columns": [
                {
                    "name": "extra_date_info",
                    "path": ["data", "date_created"],
                    "type": "string",
                    "format": "date-time",
                    "airbyte_type": "timestamp_with_timezone",
                    "required": True,
                }
            ],
        },
        schema(
            {
                "ref": {
                    "type": "string",
                },
                "ts": {
                    "type": "integer",
                },
                "data": {
                    "type": "object",
                },
                "extra_date_info": {"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"},
            }
        ),
    )


def test_discover_extra_columns():
    source = SourceFauna()
    source._setup_client = Mock()
    source.client = MagicMock()
    source.client.query = Mock()

    logger = mock_logger()
    result = source.discover(
        logger,
        config=config(
            {
                "collection": {
                    "name": "1234",
                    "index": "",
                    "data_column": False,
                    "additional_columns": [
                        {
                            "name": "my_column",
                            "path": ["data", "my_field"],
                            "type": "string",
                            "required": True,
                            "format": "date-time",
                            "airbyte_type": "date_with_timezone",
                        }
                    ],
                }
            }
        ),
    )
    assert result.streams == [
        AirbyteStream(
            name="1234",
            json_schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "ref": {
                        "type": "string",
                    },
                    "ts": {
                        "type": "integer",
                    },
                    "my_column": {
                        "type": "string",
                        "format": "date-time",
                        "airbyte_type": "date_with_timezone",
                    },
                },
            },
            supported_sync_modes=["full_refresh"],
            source_defined_cursor=True,
            default_cursor_field=["ts"],
            source_defined_primary_key=None,
            namespace=None,
        )
    ]
    assert not logger.error.called

    assert not source._setup_client.called
    assert not source.client.query.called
