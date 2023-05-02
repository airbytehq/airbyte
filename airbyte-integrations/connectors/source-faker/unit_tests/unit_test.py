#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import jsonschema
import pytest
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, Type
from source_faker import SourceFaker


class MockLogger:
    def debug(a,b, **kwargs):
        return None

    def info(a,b, **kwargs):
        return None

    def exception(a,b,**kwargs):
        print(b)
        return None

    def isEnabledFor(a, b, **kwargs):
        return False


logger = MockLogger()


def schemas_are_valid():
    source = SourceFaker()
    config = {"count": 1, "parallelism": 1}
    catalog = source.discover(None, config)
    catalog = AirbyteMessage(type=Type.CATALOG, catalog=catalog).dict(exclude_unset=True)
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]

    for schema in schemas:
        jsonschema.Draft7Validator.check_schema(schema)


def test_source_streams():
    source = SourceFaker()
    config = {"count": 1, "parallelism": 1}
    catalog = source.discover(None, config)
    catalog = AirbyteMessage(type=Type.CATALOG, catalog=catalog).dict(exclude_unset=True)
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]

    assert len(schemas) == 3
    assert schemas[1]["properties"] == {
        "id": {"type": "number"},
        "created_at": {"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"},
        "updated_at": {"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"},
        "name": {"type": "string"},
        "title": {"type": "string"},
        "age": {"type": "integer"},
        "email": {"type": "string"},
        "telephone": {"type": "string"},
        "gender": {"type": "string"},
        "language": {"type": "string"},
        "academic_degree": {"type": "string"},
        "nationality": {"type": "string"},
        "occupation": {"type": "string"},
        "height": {"type": "string"},
        "blood_type": {"type": "string"},
        "weight": {"type": "integer"},
    }


def test_read_small_random_data():
    source = SourceFaker()
    config = {"count": 10, "parallelism": 1}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            {
                "stream": {"name": "users", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                "sync_mode": "incremental",
                "destination_sync_mode": "overwrite",
            }
        ]
    )
    state = {}
    iterator = source.read(logger, config, catalog, state)

    estimate_row_count = 0
    record_rows_count = 0
    state_rows_count = 0
    latest_state = {}
    for row in iterator:
        if row.type is Type.TRACE:
            estimate_row_count = estimate_row_count + 1
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1
            latest_state = row

    assert estimate_row_count == 4
    assert record_rows_count == 10
    assert state_rows_count == 1
    assert latest_state.state.data == {"users": {"id": 10, "seed": None}}


def test_no_read_limit_hit():
    source = SourceFaker()
    config = {"count": 10, "parallelism": 1}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            {
                "stream": {"name": "users", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                "sync_mode": "incremental",
                "destination_sync_mode": "overwrite",
            }
        ]
    )
    state = {"users": {"id": 10}}
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    state_rows_count = 0
    latest_state = {}
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1
            latest_state = row

    assert record_rows_count == 0
    assert state_rows_count == 1
    assert latest_state.state.data == {"users": {"id": 10, "seed": None}}


def test_read_big_random_data():
    source = SourceFaker()
    config = {"count": 1000, "records_per_slice": 100, "records_per_sync": 1000, "parallelism": 1}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            {
                "stream": {"name": "users", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                "sync_mode": "incremental",
                "destination_sync_mode": "overwrite",
            },
            {
                "stream": {"name": "products", "json_schema": {}, "supported_sync_modes": ["full_refresh"]},
                "sync_mode": "incremental",
                "destination_sync_mode": "overwrite",
            },
        ]
    )
    state = {}
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    state_rows_count = 0
    latest_state = {}
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1
            latest_state = row

    assert record_rows_count == 1000 + 100  # 1000 users, and 100 products
    assert latest_state.state.data == {'users': {'seed': None, 'id': 1000}, 'products': {'id': 100, 'seed': None}}
    assert state_rows_count == 10 + 1 + 1 + 1


def test_with_purchases():
    source = SourceFaker()
    config = {"count": 1000, "records_per_sync": 1000, "parallelism": 1}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            {
                "stream": {"name": "users", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                "sync_mode": "incremental",
                "destination_sync_mode": "overwrite",
            },
            {
                "stream": {"name": "products", "json_schema": {}, "supported_sync_modes": ["full_refresh"]},
                "sync_mode": "incremental",
                "destination_sync_mode": "overwrite",
            },
            {
                "stream": {"name": "purchases", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                "sync_mode": "incremental",
                "destination_sync_mode": "overwrite",
            },
        ]
    )
    state = {}
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    state_rows_count = 0
    latest_state = {}
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1
            latest_state = row

    assert record_rows_count > 1000 + 100  # should be greater than 1000 users, and 100 products
    assert state_rows_count > 10 + 1  # should be greater than 1000/100, and one state for the products
    assert latest_state.state.data["users"] == {"id": 1000, "seed": None}
    assert latest_state.state.data["products"] == {'id': 100, 'seed': None}
    assert latest_state.state.data["purchases"]["user_id"] > 0


def test_sync_ends_with_limit():
    source = SourceFaker()
    config = {"count": 100, "records_per_sync": 5, "parallelism": 1}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            {
                "stream": {"name": "users", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                "sync_mode": "incremental",
                "destination_sync_mode": "overwrite",
            }
        ]
    )
    state = {}
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    state_rows_count = 0
    latest_state = {}
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1
            latest_state = row

    assert record_rows_count == 5
    assert state_rows_count == 1
    assert latest_state.state.data == {"users": {"id": 5, "seed": None}}


def test_read_with_seed():
    """
    This test asserts that setting a seed always returns the same values
    """

    source = SourceFaker()
    config = {"count": 1, "seed": 100, "parallelism": 1}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            {
                "stream": {"name": "users", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                "sync_mode": "incremental",
                "destination_sync_mode": "overwrite",
            }
        ]
    )
    state = {}
    iterator = source.read(logger, config, catalog, state)

    records = [row for row in iterator if row.type is Type.RECORD]
    assert records[0].record.data["occupation"] == "Cartoonist"
    assert records[0].record.data["email"] == "reflect1958+1@yahoo.com"


def test_ensure_no_purchases_without_users():
    with pytest.raises(ValueError):
        source = SourceFaker()
        config = {"count": 100, "parallelism": 1}
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                {"stream": {"name": "purchases", "json_schema": {}}, "sync_mode": "incremental", "destination_sync_mode": "overwrite"},
            ]
        )
        state = {}
        iterator = source.read(logger, config, catalog, state)
        iterator.__next__()
