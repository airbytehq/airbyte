#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import jsonschema
import pytest
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, Type
from source_faker import SourceFaker


def test_source_streams():
    source = SourceFaker()
    config = {"count": 1}
    catalog = source.discover(None, config)
    catalog = AirbyteMessage(type=Type.CATALOG, catalog=catalog).dict(exclude_unset=True)
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]

    assert len(schemas) == 3
    assert schemas[0]["properties"] == {
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

    for schema in schemas:
        jsonschema.Draft7Validator.check_schema(schema)


def test_read_small_random_data():
    source = SourceFaker()
    logger = None
    config = {"count": 10}
    catalog = ConfiguredAirbyteCatalog(
        streams=[{"stream": {"name": "Users", "json_schema": {}}, "sync_mode": "full_refresh", "destination_sync_mode": "overwrite"}]
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

    assert record_rows_count == 10
    assert state_rows_count == 1
    assert latest_state.state.data == {"Users": {"cursor": 10, "seed": None}}


def test_read_big_random_data():
    source = SourceFaker()
    logger = None
    config = {"count": 1000, "records_per_slice": 100, "records_per_sync": 1000}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            {"stream": {"name": "Users", "json_schema": {}}, "sync_mode": "full_refresh", "destination_sync_mode": "overwrite"},
            {"stream": {"name": "Products", "json_schema": {}}, "sync_mode": "full_refresh", "destination_sync_mode": "overwrite"},
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
    assert state_rows_count == 10 + 1 + 1  # 1000/100 + one more state at the end, and one state for the products
    assert latest_state.state.data == {"Products": {"product_count": 100}, "Users": {"cursor": 1000, "seed": None}}


def test_with_purchases():
    source = SourceFaker()
    logger = None
    config = {"count": 1000, "records_per_sync": 1000}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            {"stream": {"name": "Users", "json_schema": {}}, "sync_mode": "full_refresh", "destination_sync_mode": "overwrite"},
            {"stream": {"name": "Products", "json_schema": {}}, "sync_mode": "full_refresh", "destination_sync_mode": "overwrite"},
            {"stream": {"name": "Purchases", "json_schema": {}}, "sync_mode": "full_refresh", "destination_sync_mode": "overwrite"},
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
    assert state_rows_count > 10 + 1 + 1  # should be greater than 1000/100 + one more state at the end, and one state for the products
    assert latest_state.state.data["Users"] == {"cursor": 1000, "seed": None}
    assert latest_state.state.data["Products"] == {"product_count": 100}
    assert latest_state.state.data["Purchases"]["purchases_count"] > 0


def test_sync_ends_with_limit():
    source = SourceFaker()
    logger = None
    config = {"count": 100, "records_per_sync": 5}
    catalog = ConfiguredAirbyteCatalog(
        streams=[{"stream": {"name": "Users", "json_schema": {}}, "sync_mode": "full_refresh", "destination_sync_mode": "overwrite"}]
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
    assert latest_state.state.data == {"Users": {"cursor": 5, "seed": None}}


def test_read_with_seed():
    """
    This test asserts that setting a seed always returns the same values
    """

    source = SourceFaker()
    logger = None
    config = {"count": 1, "seed": 100}
    catalog = ConfiguredAirbyteCatalog(
        streams=[{"stream": {"name": "Users", "json_schema": {}}, "sync_mode": "full_refresh", "destination_sync_mode": "overwrite"}]
    )
    state = {}
    iterator = source.read(logger, config, catalog, state)

    records = [row for row in iterator if row.type is Type.RECORD]
    assert records[0].record.data["occupation"] == "Roadworker"
    assert records[0].record.data["email"] == "reproduce1856@outlook.com"


def test_ensure_no_purchases_without_users():
    with pytest.raises(ValueError):
        source = SourceFaker()
        logger = None
        config = {"count": 100}
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                {"stream": {"name": "Purchases", "json_schema": {}}, "sync_mode": "full_refresh", "destination_sync_mode": "overwrite"},
            ]
        )
        state = {}
        iterator = source.read(logger, config, catalog, state)
        iterator.__next__()
