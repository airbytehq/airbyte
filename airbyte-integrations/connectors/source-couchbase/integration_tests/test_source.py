import json
from pathlib import Path
import logging
import pytest
from airbyte_cdk.models import AirbyteCatalog, ConfiguredAirbyteCatalog, Type, TraceType, Level
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from source_couchbase.source import SourceCouchbase
from airbyte_cdk.models import ConnectorSpecification

@pytest.fixture(scope="module")
def config():
    config_path = Path(__file__).parent.parent / "secrets" / "config.json"
    with open(config_path, "r") as f:
        return json.load(f)

@pytest.fixture(scope="module")
def source():
    return SourceCouchbase()

@pytest.fixture(scope="module")
def logger():
    logger = logging.getLogger("airbyte")
    logger.setLevel(logging.DEBUG)
    return logger


def test_check_connection(config, source, logger):
    result = source.check_connection(logger, config)
    assert result[0] is True
    assert result[1] is None


def test_streams(config, source):
    streams = source.streams(config)
    assert len(streams) == 4  # Buckets, Scopes, Collections, Documents

    # Verify that each stream is an instance of Stream
    for stream in streams:
        assert isinstance(stream, Stream)

    # Verify stream names
    stream_names = [stream.name for stream in streams]
    assert "buckets" in stream_names
    assert "scopes" in stream_names
    assert "collections" in stream_names
    assert "documents" in stream_names


def test_source_name(source):
    assert source.name == "SourceCouchbase"


def test_get_connector_spec(source, logger):
    spec = source.spec(logger=logger)
    assert isinstance(spec, ConnectorSpecification)
    assert hasattr(spec, "connectionSpecification")


def test_read(config, source, logger):
    catalog = source.discover(logger=logger, config=config)
    configured_catalog = ConfiguredAirbyteCatalog(
        streams=[
            {
                "stream": {
                    "name": stream.name,
                    "json_schema": stream.json_schema,
                    "supported_sync_modes": stream.supported_sync_modes,
                },
                "sync_mode": "full_refresh",
                "destination_sync_mode": "overwrite",
            }
            for stream in catalog.streams
        ]
    )

    for message in source.read(logger=logger, config=config, catalog=configured_catalog, state={}):
        assert message.type in [Type.RECORD, Type.STATE, Type.TRACE, Type.LOG]
        if message.type == Type.RECORD:
            assert message.record.stream in [stream.stream.name for stream in configured_catalog.streams]
            assert isinstance(message.record.data, dict)
        elif message.type == Type.STATE:
            assert message.state.data is None or isinstance(message.state.data, dict)
        elif message.type == Type.TRACE:
            assert message.trace.type in [TraceType.STREAM_STATUS, TraceType.ERROR]
        elif message.type == Type.LOG:
            assert message.log.level in [Level.INFO, Level.ERROR]


if __name__ == "__main__":
    pytest.main([__file__])
