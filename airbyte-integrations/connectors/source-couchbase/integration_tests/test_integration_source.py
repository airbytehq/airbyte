import json
import logging
from pathlib import Path

import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConnectorSpecification, SyncMode, DestinationSyncMode, Type
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
    logger.setLevel(logging.ERROR)
    return logger

def test_check_connection(config, source, logger):
    result = source.check_connection(logger, config)
    if result != (True, None):
        logger.error(f"Connection check failed: {result[1]}")
    assert result == (True, None), "Connection check failed"

def test_check_connection_invalid_config(source, logger):
    invalid_config = {
        "connection_string": "couchbase://localhost",
        "username": "invalid",
        "password": "invalid",
        "bucket": "invalid"
    }
    result, error_msg = source.check_connection(logger, invalid_config)
    if result:
        logger.error("Connection check with invalid config unexpectedly succeeded")
    assert result is False
    assert "Connection check failed" in error_msg

def test_source_name(source):
    assert source.name == "Couchbase", "Source name is not 'Couchbase'"

def test_get_connector_spec(source, logger):
    spec = source.spec(logger=logger)
    assert isinstance(spec, ConnectorSpecification), "Spec is not an instance of ConnectorSpecification"
    assert spec.documentationUrl == "https://docs.airbyte.com/integrations/sources/couchbase", "Incorrect documentationUrl"
    
    connection_spec = spec.connectionSpecification
    assert connection_spec['$schema'] == "http://json-schema.org/draft-07/schema#", "Incorrect schema in connectionSpecification"
    assert connection_spec['title'] == "Couchbase Source Spec", "Incorrect title in connectionSpecification"
    
    required_properties = ["connection_string", "username", "password", "bucket"]
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
    incremental_config = {**config, "use_incremental": True}
    for stream in configured_catalog.streams:
        stream.sync_mode = SyncMode.incremental
        stream.cursor_field = ["_ab_cdc_updated_at"]
        stream.destination_sync_mode = DestinationSyncMode.append
    return incremental_config

def assert_record(record, configured_catalog, sync_mode):
    assert record.stream in [stream.stream.name for stream in configured_catalog.streams], f"Record stream {record.stream} not in catalog"
    assert isinstance(record.data, dict), "Record data is not a dict"
    assert "_id" in record.data, "_id not in record data"
    assert "content" in record.data, "content not in record data"
    
    if sync_mode == "incremental":
        assert "_ab_cdc_updated_at" in record.data, "_ab_cdc_updated_at not in record data"

def assert_message(message, configured_catalog, sync_mode):
    assert message.type in [Type.RECORD, Type.STATE, Type.LOG, Type.TRACE], f"Unexpected message type {message.type}"
    
    if message.type == Type.RECORD:
        assert_record(message.record, configured_catalog, sync_mode)
    elif message.type == Type.STATE:
        assert message.state.data is None or isinstance(message.state.data, dict), "State data is not None or dict"

@pytest.mark.parametrize("sync_mode", ["full_refresh", "incremental"])
def test_read(config, source, logger, configured_catalog, sync_mode):
    if sync_mode == "incremental":
        config = configure_incremental_sync(config, configured_catalog)

    state = {}
    records_found = False
    final_state = None
    record_count = 0
    for message in source.read(logger=logger, config=config, catalog=configured_catalog, state=state):
        assert_message(message, configured_catalog, sync_mode)
        
        if message.type == Type.RECORD:
            records_found = True
            record_count += 1
        elif message.type == Type.STATE and sync_mode == "incremental":
            final_state = message.state.data

    if not records_found:
        pytest.skip(f"No records found for {sync_mode} sync")

    if sync_mode == "incremental":
        assert final_state, "State should be updated after incremental sync"
        assert isinstance(final_state, dict), "Final state should be a dictionary"
        for stream_name, stream_state in final_state.items():
            assert "_ab_cdc_updated_at" in stream_state, f"State for stream {stream_name} should contain _ab_cdc_updated_at field after incremental sync"
            assert isinstance(stream_state["_ab_cdc_updated_at"], (int, float)), f"_ab_cdc_updated_at for stream {stream_name} should be a number"

def test_no_streams_available(source, logger):
    invalid_config = {
        "connection_string": "couchbase://localhost",
        "username": "invalid",
        "password": "invalid",
        "bucket": "non_existent_bucket"
    }
    
    with pytest.raises(Exception) as exc_info:
        list(source.streams(invalid_config))
    
    error_message = str(exc_info.value)
    if "AuthenticationException" not in error_message and "No streams could be generated" not in error_message:
        logger.error(f"Unexpected error message: {error_message}")
    assert "AuthenticationException" in error_message or "No streams could be generated" in error_message

def test_validate_state():
    source = SourceCouchbase()
    
    # Test valid state
    valid_state = {"stream1": {"_ab_cdc_updated_at": 1234567890}}
    assert source._validate_state(valid_state) == valid_state

    # Test invalid state type
    with pytest.raises(ValueError, match="State must be a dictionary"):
        source._validate_state([])

    # Test invalid stream state type
    with pytest.raises(ValueError, match="State for stream stream1 must be a dictionary"):
        source._validate_state({"stream1": []})

    # Test invalid _ab_cdc_updated_at type
    with pytest.raises(ValueError, match="_ab_cdc_updated_at for stream stream1 must be a number"):
        source._validate_state({"stream1": {"_ab_cdc_updated_at": "not a number"}})

if __name__ == "__main__":
    pytest.main([__file__])
