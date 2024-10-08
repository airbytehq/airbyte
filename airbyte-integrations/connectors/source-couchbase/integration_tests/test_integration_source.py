import json
import logging
from pathlib import Path

import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConnectorSpecification, Level, TraceType, Type, SyncMode, DestinationSyncMode
from source_couchbase.source import SourceCouchbase

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
    assert result == (True, None), "Connection check failed"

def test_source_name(source):
    assert source.name == "Couchbase", "Source name is not 'Couchbase'"

def test_get_connector_spec(source, logger):
    spec = source.spec(logger=logger)
    assert isinstance(spec, ConnectorSpecification), "Spec is not an instance of ConnectorSpecification"
    assert spec.documentationUrl == "https://docs.airbyte.com/integrations/sources/couchbase", "Incorrect documentationUrl"
    
    connection_spec = spec.connectionSpecification
    assert connection_spec['$schema'] == "http://json-schema.org/draft-07/schema#", "Incorrect schema in connectionSpecification"
    assert connection_spec['title'] == "Couchbase Source Spec", "Incorrect title in connectionSpecification"
    
    required_properties = ["connection_string", "username", "password", "bucket", "use_incremental", "cursor_field"]
    for prop in required_properties:
        assert prop in connection_spec["properties"], f"{prop} not in spec properties"

@pytest.fixture(scope="module")
def configured_catalog(config, source, logger):
    catalog = source.discover(logger=logger, config=config)
    return ConfiguredAirbyteCatalog(
        streams=[
            {
                "stream": stream,
                "sync_mode": SyncMode.full_refresh,
                "destination_sync_mode": DestinationSyncMode.overwrite,
            }
            for stream in catalog.streams
        ]
    )

def configure_incremental_sync(config, configured_catalog):
    incremental_config = {**config, "use_incremental": True, "cursor_field": "updated_at"}
    for stream in configured_catalog.streams:
        stream.sync_mode = SyncMode.incremental
        stream.cursor_field = ["updated_at"]
        stream.destination_sync_mode = DestinationSyncMode.append
    return incremental_config

def assert_record(record, configured_catalog, sync_mode, state):
    assert record.stream in [stream.stream.name for stream in configured_catalog.streams], f"Record stream {record.stream} not in catalog"
    assert isinstance(record.data, dict), "Record data is not a dict"
    assert "id" in record.data, "id not in record data"
    assert "content" in record.data, "content not in record data"
    
    if sync_mode == "incremental":
        assert "updated_at" in record.data["content"], "updated_at not in record content"
        if state:
            assert record.data["content"]["updated_at"] >= state["updated_at"], "Record updated_at is less than state updated_at"

def assert_message(message, configured_catalog, sync_mode, state):
    assert message.type in [Type.RECORD, Type.STATE, Type.TRACE, Type.LOG], f"Unexpected message type {message.type}"
    
    if message.type == Type.RECORD:
        assert_record(message.record, configured_catalog, sync_mode, state)
    elif message.type == Type.STATE:
        assert message.state.data is None or isinstance(message.state.data, dict), "State data is not None or dict"
    elif message.type == Type.TRACE:
        assert message.trace.type in [TraceType.STREAM_STATUS, TraceType.ERROR], f"Unexpected trace type {message.trace.type}"
    elif message.type == Type.LOG:
        assert message.log.level in [Level.INFO, Level.ERROR], f"Unexpected log level {message.log.level}"

@pytest.mark.parametrize("sync_mode", ["full_refresh", "incremental"])
def test_read(config, source, logger, configured_catalog, sync_mode):
    if sync_mode == "incremental":
        config = configure_incremental_sync(config, configured_catalog)

    state = {}
    records_found = False
    for message in source.read(logger=logger, config=config, catalog=configured_catalog, state=state):
        assert_message(message, configured_catalog, sync_mode, state)
        
        if message.type == Type.RECORD:
            records_found = True
        elif message.type == Type.STATE and sync_mode == "incremental":
            state = message.state.data

    if not records_found:
        pytest.skip(f"No records found for {sync_mode} sync")

    if sync_mode == "incremental":
        assert state, "State should be updated after incremental sync"

if __name__ == "__main__":
    pytest.main([__file__])
