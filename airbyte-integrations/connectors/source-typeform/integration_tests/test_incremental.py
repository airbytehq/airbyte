#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging

import pendulum
import pytest
import urllib.parse as urlparse
from airbyte_cdk.models import ConfiguredAirbyteCatalog, Type
from source_typeform.source import SourceTypeform


@pytest.fixture
def configured_catalog():
    return {
        "streams": [
            {
                "stream": {
                    "name": "responses",
                    "json_schema": {},
                    "supported_sync_modes": ["incremental", "full_refresh"],
                    "source_defined_cursor": True,
                    "default_cursor_field": ["submitted_at"],
                    "source_defined_primary_key": [["response_id"]],
                },
                "sync_mode": "incremental",
                "destination_sync_mode": "append",
                "primary_key": [["response_id"]],
            }
        ]
    }


def test_incremental_sync(config, configured_catalog):
    def get_form_id(record):
        referer = record.get("metadata", {}).get("referer")
        return urlparse.urlparse(referer).path.split("/")[-1] if referer else None

    def timestamp_from_datetime(value):
        return pendulum.from_format(value, "YYYY-MM-DDTHH:mm:ss[Z]").int_timestamp

    source = SourceTypeform()
    records = list(source.read(logging.getLogger("airbyte"), config, ConfiguredAirbyteCatalog.parse_obj(configured_catalog)))
    latest_state = None
    for record in records[::-1]:
        if record and record.type == Type.STATE:
            latest_state = record.state.data["responses"]
            break

    for message in records:
        if not message or message.type != Type.RECORD:
            continue
        form_id = get_form_id(message.record.data)
        cursor_value = timestamp_from_datetime(message.record.data["submitted_at"])
        assert cursor_value <= latest_state[form_id]["submitted_at"]
        assert cursor_value >= timestamp_from_datetime(config["start_date"])

    #  next sync
    records = list(
        source.read(
            logging.getLogger("airbyte"),
            config,
            ConfiguredAirbyteCatalog.parse_obj(configured_catalog),
            {"responses": latest_state},
        )
    )

    for record in records:
        if record.type == Type.RECORD:
            form_id = get_form_id(record.record.data)
            assert timestamp_from_datetime(record.record.data["submitted_at"]) >= latest_state[form_id]["submitted_at"]
        if record.type == Type.STATE:
            for form_id, form_state in record.state.data["responses"].items():
                assert form_state["submitted_at"] >= latest_state[form_id]["submitted_at"]


def test_abnormally_large_state(config, configured_catalog, abnormal_state):
    source = SourceTypeform()
    records = source.read(
        logging.getLogger("airbyte"),
        config,
        ConfiguredAirbyteCatalog.parse_obj(configured_catalog),
        abnormal_state,
    )

    no_data_records = True
    state_records = False
    for record in records:
        if record and record.type == Type.STATE:
            state_records = True
        if record and record.type == Type.RECORD:
            no_data_records = False

    assert no_data_records
    assert state_records
