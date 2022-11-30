#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import base64
import json
import time
from datetime import datetime
from pathlib import Path

import pytest
import requests
from airbyte_cdk.models import SyncMode
from source_salesforce.api import Salesforce
from source_salesforce.source import SourceSalesforce

HERE = Path(__file__).parent

NOTE_CONTENT = "It's the note for integration test"
UPDATED_NOTE_CONTENT = "It's the updated note for integration test"


@pytest.fixture(scope="module")
def input_sandbox_config():
    with open(HERE.parent / "secrets/config_sandbox.json", "r") as file:
        return json.loads(file.read())


@pytest.fixture(scope="module")
def sf(input_sandbox_config):
    sf = Salesforce(**input_sandbox_config)
    sf.login()
    return sf


@pytest.fixture(scope="module")
def stream_name():
    return "ContentNote"


@pytest.fixture(scope="module")
def stream(input_sandbox_config, stream_name, sf):
    return SourceSalesforce.generate_streams(input_sandbox_config, {stream_name: None}, sf)[0]


def _encode_content(text):
    base64_bytes = base64.b64encode(text.encode("utf-8"))
    return base64_bytes.decode("utf-8")


def create_note(stream, headers):
    url = stream.url_base + f"/services/data/{stream.sf_api.version}/sobjects/{stream.name}"
    note_data = {"Title": "Integration Test", "Content": _encode_content(NOTE_CONTENT)}
    return requests.post(url, headers=headers, json=note_data)


def delete_note(stream, note_id, headers):
    url = stream.url_base + f"/services/data/{stream.sf_api.version}/sobjects/{stream.name}/{note_id}"
    return requests.delete(url, headers=headers)


def update_note(stream, note_id, headers):
    url = stream.url_base + f"/services/data/{stream.sf_api.version}/sobjects/{stream.name}/{note_id}"
    note_data = {"Content": _encode_content(UPDATED_NOTE_CONTENT)}
    return requests.patch(url, headers=headers, json=note_data)


def get_stream_state():
    state_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"LastModifiedDate": state_date}


def test_update_for_deleted_record(stream):
    headers = stream.authenticator.get_auth_header()
    stream_state = get_stream_state()
    time.sleep(1)
    response = create_note(stream, headers)
    assert response.status_code == 201, "Note was not created"

    created_note_id = response.json()["id"]

    notes = set(record["Id"] for record in stream.read_records(sync_mode=None))
    assert created_note_id in notes, "The stream didn't return the note we created"

    response = delete_note(stream, created_note_id, headers)
    assert response.status_code == 204, "Note was not deleted"

    is_note_updated = False
    is_deleted = False
    for record in stream.read_records(sync_mode=SyncMode.incremental, stream_state=stream_state):
        if created_note_id == record["Id"]:
            is_note_updated = True
            is_deleted = record["IsDeleted"]
            break
    assert is_note_updated, "No deleted note during the sync"
    assert is_deleted, "Wrong field value for deleted note during the sync"

    time.sleep(1)
    response = update_note(stream, created_note_id, headers)
    assert response.status_code == 404, "Expected an update to a deleted note to return 404"


def test_deleted_record(stream):
    headers = stream.authenticator.get_auth_header()
    response = create_note(stream, headers)
    assert response.status_code == 201, "Note was note created"

    created_note_id = response.json()["id"]

    notes = set(record["Id"] for record in stream.read_records(sync_mode=None))
    assert created_note_id in notes, "No created note during the sync"

    response = update_note(stream, created_note_id, headers)
    assert response.status_code == 204, "Note was not updated"

    stream_state = get_stream_state()
    response = delete_note(stream, created_note_id, headers)
    assert response.status_code == 204, "Note was not deleted"

    record = None
    for record in stream.read_records(sync_mode=SyncMode.incremental, stream_state=stream_state):
        if created_note_id == record["Id"]:
            break

    assert record, "No updated note during the sync"
    assert record["IsDeleted"], "Wrong field value for deleted note during the sync"
    assert record["TextPreview"] == UPDATED_NOTE_CONTENT and record["TextPreview"] != NOTE_CONTENT, "Note Content was not updated"


def test_parallel_discover(input_sandbox_config):
    sf = Salesforce(**input_sandbox_config)
    sf.login()
    stream_objects = sf.get_validated_streams(config=input_sandbox_config)

    # try to load all schema with the old consecutive logic
    consecutive_schemas = {}
    start_time = datetime.now()
    for stream_name, sobject_options in stream_objects.items():
        consecutive_schemas[stream_name] = sf.generate_schema(stream_name, sobject_options)
    consecutive_loading_time = (datetime.now() - start_time).total_seconds()
    start_time = datetime.now()
    parallel_schemas = sf.generate_schemas(stream_objects)
    parallel_loading_time = (datetime.now() - start_time).total_seconds()

    print(f"\nparallel discover ~ {round(consecutive_loading_time/parallel_loading_time, 1)}x faster over traditional.\n")

    assert parallel_loading_time < consecutive_loading_time, "parallel should be more than 10x faster"
    assert set(consecutive_schemas.keys()) == set(parallel_schemas.keys())
    for stream_name, schema in consecutive_schemas.items():
        assert schema == parallel_schemas[stream_name]
