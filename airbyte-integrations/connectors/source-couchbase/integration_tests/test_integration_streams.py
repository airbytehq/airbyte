import json
from pathlib import Path

import pytest
from airbyte_cdk.models import SyncMode
from source_couchbase.source import SourceCouchbase
from source_couchbase.streams import CouchbaseStream, IncrementalCouchbaseStream

@pytest.fixture(scope="module")
def config():
    config_path = Path(__file__).parent.parent / "secrets" / "config.json"
    with open(config_path, "r") as f:
        return json.load(f)

@pytest.fixture(scope="module")
def source():
    return SourceCouchbase()

@pytest.fixture(scope="module")
def streams(config, source):
    return source.streams(config)

@pytest.fixture(scope="module")
def incremental_streams(config, source):
    incremental_config = {**config, "use_incremental": True}
    return source.streams(incremental_config)

def test_streams_not_empty(streams):
    assert len(streams) > 0, "No streams found"

@pytest.mark.parametrize("stream_type,expected_type", [
    (CouchbaseStream, "CouchbaseStream"),
    (IncrementalCouchbaseStream, "IncrementalCouchbaseStream")
])
def test_stream_types(streams, incremental_streams, stream_type, expected_type):
    stream_list = incremental_streams if stream_type == IncrementalCouchbaseStream else streams
    for stream in stream_list:
        assert isinstance(stream, stream_type), f"Stream {stream.name} is not an instance of {expected_type}"

def test_stream_names(streams, config):
    for stream in streams:
        assert stream.name.count('.') == 2, f"Stream name {stream.name} does not follow the pattern bucket.scope.collection"
        assert config['bucket'] in stream.name, f"Bucket name {config['bucket']} not found in stream name {stream.name}"
        parts = stream.name.split('.')
        assert len(parts) == 3, f"Stream name {stream.name} does not have three parts separated by dots"
        assert parts[0] == config['bucket'], f"First part of stream name {stream.name} does not match bucket name {config['bucket']}"

def test_incremental_stream_cursor_field(incremental_streams):
    for stream in incremental_streams:
        assert stream.cursor_field == "_ab_cdc_updated_at", f"Cursor field for stream {stream.name} is not '_ab_cdc_updated_at'"

@pytest.mark.parametrize("sync_mode,stream_type", [
    (SyncMode.full_refresh, CouchbaseStream),
    (SyncMode.incremental, IncrementalCouchbaseStream)
])
def test_stream_read(streams, sync_mode, stream_type):
    records_found = False
    for stream in streams:
        if isinstance(stream, stream_type):
            state = {"_ab_cdc_updated_at": 0} if sync_mode == SyncMode.incremental else None
            records = list(stream.read_records(sync_mode=sync_mode, cursor_field="_ab_cdc_updated_at", stream_state=state))
            if len(records) > 0:
                records_found = True
                for record in records:
                    assert "_id" in record, f"Record in stream {stream.name} is missing '_id' field"
                    assert "content" in record, f"Record in stream {stream.name} is missing 'content' field"
                    if sync_mode == SyncMode.incremental:
                        assert "_ab_cdc_updated_at" in record, f"Incremental record in stream {stream.name} is missing '_ab_cdc_updated_at' field"
                        assert record["_ab_cdc_updated_at"] >= state["_ab_cdc_updated_at"], f"Record '_ab_cdc_updated_at' is less than state '_ab_cdc_updated_at' in stream {stream.name}"
    
    if not records_found:
        pytest.skip(f"No records found for any stream with {sync_mode} sync mode")

def test_json_schema(streams):
    for stream in streams:
        schema = stream.get_json_schema()
        assert isinstance(schema, dict), f"Schema for stream {stream.name} is not a dictionary"
        assert "properties" in schema, f"Schema for stream {stream.name} is missing 'properties'"
        assert "_id" in schema["properties"], f"Schema for stream {stream.name} is missing '_id' property"
        assert "content" in schema["properties"], f"Schema for stream {stream.name} is missing 'content' property"
        if isinstance(stream, IncrementalCouchbaseStream):
            assert "_ab_cdc_updated_at" in schema["properties"], f"Schema for incremental stream {stream.name} is missing '_ab_cdc_updated_at' property"

def test_incremental_sync_updates_state(incremental_streams):
    state_updated = False
    for stream in incremental_streams:
        initial_state = {"_ab_cdc_updated_at": 0}
        records = list(stream.read_records(sync_mode=SyncMode.incremental, cursor_field="_ab_cdc_updated_at", stream_state=initial_state))
        if len(records) > 0:
            final_state = stream.state
            assert "_ab_cdc_updated_at" in final_state, f"State does not contain '_ab_cdc_updated_at' for incremental stream {stream.name}"
            assert final_state["_ab_cdc_updated_at"] > initial_state["_ab_cdc_updated_at"], f"State not updated for incremental stream {stream.name}"
            state_updated = True
    
    if not state_updated:
        pytest.skip("No records found for any incremental stream to update state")

if __name__ == "__main__":
    pytest.main()
