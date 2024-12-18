#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

import pendulum
import pytest
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from source_salesforce.api import Salesforce
from source_salesforce.source import SourceSalesforce

HERE = Path(__file__).parent

NOTE_CONTENT = "It's the note for integration test"
UPDATED_NOTE_CONTENT = "It's the updated note for integration test"

_ANY_CATALOG = CatalogBuilder().build()
_ANY_CONFIG = {}
_ANY_STATE = {}


@pytest.fixture(scope="module")
def input_sandbox_config():
    with open(HERE.parent / "secrets/config_sandbox.json", "r") as file:
        return json.loads(file.read())


@pytest.fixture(scope="module")
def sf(input_sandbox_config):
    sf = Salesforce(**input_sandbox_config)
    sf.login()
    return sf


def _authentication_headers(salesforce: Salesforce) -> Dict[str, str]:
    return {"Authorization": f"Bearer {salesforce.access_token}"}


@pytest.fixture(scope="module")
def stream_name():
    return "ContentNote"


@pytest.fixture(scope="module")
def stream(input_sandbox_config, stream_name, sf):
    return SourceSalesforce(_ANY_CATALOG, _ANY_CONFIG, _ANY_STATE).generate_streams(input_sandbox_config, {stream_name: None}, sf)[0]._legacy_stream


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
    return {"LastModifiedDate": pendulum.now(tz="UTC").add(days=-1).isoformat(timespec="milliseconds")}


def test_update_for_deleted_record(stream, sf):
    headers = _authentication_headers(sf)
    stream_state = get_stream_state()
    time.sleep(1)
    response = create_note(stream, headers)
    assert response.status_code == 201, "Note was not created"

    created_note_id = response.json()["id"]

    # A record may not be accessible right after creation. This workaround makes few attempts to receive latest record
    notes = []
    attempts = 10
    while created_note_id not in notes:
        now = pendulum.now(tz="UTC")
        stream_slice = {
            "start_date": now.add(days=-1).isoformat(timespec="milliseconds"),
            "end_date": now.isoformat(timespec="milliseconds"),
        }
        notes = set(record["Id"] for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))
        try:
            assert created_note_id in notes, "The stream didn't return the note we created"
            break
        except Exception as e:
            if attempts:
                time.sleep(2)
            else:
                raise e
        attempts = attempts - 1

    response = delete_note(stream, created_note_id, headers)
    assert response.status_code == 204, "Note was not deleted"

    # A record may still be accessible right after deletion for some time
    attempts = 10
    while True:
        is_note_updated = False
        is_deleted = False
        now = pendulum.now(tz="UTC")
        stream_slice = {
            "start_date": now.add(days=-1).isoformat(timespec="milliseconds"),
            "end_date": now.isoformat(timespec="milliseconds"),
        }
        for record in stream.read_records(sync_mode=SyncMode.incremental, stream_state=stream_state, stream_slice=stream_slice):
            if created_note_id == record["Id"]:
                is_note_updated = True
                is_deleted = record["IsDeleted"]
                break
        try:
            assert is_note_updated, "No deleted note during the sync"
            assert is_deleted, "Wrong field value for deleted note during the sync"
            break
        except Exception as e:
            if attempts:
                time.sleep(2)
            else:
                raise e
        attempts = attempts - 1

    time.sleep(1)
    response = update_note(stream, created_note_id, headers)
    assert response.status_code == 404, "Expected an update to a deleted note to return 404"


def test_deleted_record(stream, sf):
    headers = _authentication_headers(sf)
    response = create_note(stream, headers)
    assert response.status_code == 201, "Note was note created"

    created_note_id = response.json()["id"]

    # A record may not be accessible right after creation. This workaround makes few attempts to receive latest record
    notes = []
    attempts = 10
    while created_note_id not in notes:
        now = pendulum.now(tz="UTC")
        stream_slice = {
            "start_date": now.add(days=-1).isoformat(timespec="milliseconds"),
            "end_date": now.isoformat(timespec="milliseconds"),
        }
        notes = set(record["Id"] for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice))
        try:
            assert created_note_id in notes, "No created note during the sync"
            break
        except Exception as e:
            if attempts:
                time.sleep(2)
            else:
                raise e
        attempts = attempts - 1

    response = update_note(stream, created_note_id, headers)
    assert response.status_code == 204, "Note was not updated"

    stream_state = get_stream_state()
    response = delete_note(stream, created_note_id, headers)
    assert response.status_code == 204, "Note was not deleted"

    # A record updates take some time to become accessible
    attempts = 10
    while created_note_id not in notes:
        now = pendulum.now(tz="UTC")
        stream_slice = {
            "start_date": now.add(days=-1).isoformat(timespec="milliseconds"),
            "end_date": now.isoformat(timespec="milliseconds"),
        }
        record = None
        for record in stream.read_records(sync_mode=SyncMode.incremental, stream_state=stream_state, stream_slice=stream_slice):
            if created_note_id == record["Id"]:
                break
        try:
            assert record, "No updated note during the sync"
            assert record["IsDeleted"], "Wrong field value for deleted note during the sync"
            assert record["TextPreview"] == UPDATED_NOTE_CONTENT and record["TextPreview"] != NOTE_CONTENT, "Note Content was not updated"
            break
        except Exception as e:
            if attempts:
                time.sleep(2)
            else:
                raise e
        attempts = attempts - 1


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
