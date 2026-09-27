#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime

import jsonschema
import pytest
from source_faker import SourceFaker
from source_faker.review_generator import purchase_ids_for_user

from airbyte_cdk.models import AirbyteMessage, AirbyteMessageSerializer, ConfiguredAirbyteCatalog, ConfiguredAirbyteStreamSerializer, Type


class MockLogger:
    def debug(a, b, **kwargs):
        return None

    def info(a, b, **kwargs):
        return None

    def exception(a, b, **kwargs):
        print(b)
        return None

    def isEnabledFor(a, b, **kwargs):
        return False


logger = MockLogger()


def schemas_are_valid():
    source = SourceFaker()
    config = {"count": 1, "parallelism": 1}
    catalog = source.discover(None, config)
    catalog = AirbyteMessageSerializer.dump(AirbyteMessage(type=Type.CATALOG, catalog=catalog))
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]

    for schema in schemas:
        jsonschema.Draft7Validator.check_schema(schema)


def test_source_streams():
    source = SourceFaker()
    config = {"count": 1, "parallelism": 1}
    catalog = source.discover(None, config)
    catalog = AirbyteMessageSerializer.dump(AirbyteMessage(type=Type.CATALOG, catalog=catalog))
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]

    assert len(schemas) == 4
    assert schemas[1]["properties"] == {
        "id": {"type": "integer"},
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
        "address": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "country_code": {"type": "string"},
                "postal_code": {"type": "string"},
                "province": {"type": "string"},
                "state": {"type": "string"},
                "street_name": {"type": "string"},
                "street_number": {"type": "string"},
            },
        },
    }


def test_read_small_random_data():
    source = SourceFaker()
    config = {"count": 10, "parallelism": 1}
    stream_dict = {
        "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
        "sync_mode": "incremental",
        "destination_sync_mode": "overwrite",
    }
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    estimate_row_count = 0
    record_rows_count = 0
    state_rows_count = 0
    for row in iterator:
        if row.type is Type.TRACE:
            estimate_row_count = estimate_row_count + 1
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1

    assert estimate_row_count == 4
    assert record_rows_count == 10
    assert state_rows_count == 1


def test_read_always_updated():
    source = SourceFaker()
    config = {"count": 10, "parallelism": 1, "always_updated": False}
    stream_dict = {
        "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
        "sync_mode": "incremental",
        "destination_sync_mode": "overwrite",
    }
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1

    assert record_rows_count == 10

    from airbyte_cdk.models import AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor
    from airbyte_cdk.models.airbyte_protocol import AirbyteStateBlob

    stream_descriptor = StreamDescriptor(name="users", namespace=None)
    stream_state = AirbyteStreamState(stream_descriptor=stream_descriptor, stream_state=AirbyteStateBlob(updated_at="something"))
    state = [AirbyteStateMessage(type=AirbyteStateType.STREAM, stream=stream_state)]
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1

    assert record_rows_count == 0


def test_read_products():
    source = SourceFaker()
    config = {"count": 999, "parallelism": 1}
    stream_dict = {
        "stream": {"name": "products", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["full_refresh"]},
        "sync_mode": "incremental",
        "destination_sync_mode": "overwrite",
    }
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    estimate_row_count = 0
    record_rows_count = 0
    state_rows_count = 0
    for row in iterator:
        if row.type is Type.TRACE:
            estimate_row_count = estimate_row_count + 1
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1

    assert estimate_row_count == 4
    assert record_rows_count == 100  # only 100 products, no matter the count
    assert state_rows_count in {1, 2}, "Expected 1 or 2 state messages per stream."


def test_read_big_random_data():
    source = SourceFaker()
    config = {"count": 1000, "records_per_slice": 100, "parallelism": 1}
    stream_dicts = [
        {
            "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
        {
            "stream": {"name": "products", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["full_refresh"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
    ]
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict) for stream_dict in stream_dicts])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    state_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1

    assert record_rows_count == 1000 + 100  # 1000 users, and 100 products
    assert state_rows_count == 11


def test_with_purchases():
    source = SourceFaker()
    config = {"count": 1000, "parallelism": 1}
    stream_dicts = [
        {
            "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
        {
            "stream": {"name": "products", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["full_refresh"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
        {
            "stream": {"name": "purchases", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
    ]
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict) for stream_dict in stream_dicts])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    state_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1

    assert record_rows_count > 1000 + 100  # should be greater than 1000 users, and 100 products
    assert state_rows_count > 10 + 1  # should be greater than 1000/100, and one state for the products


def test_read_with_seed():
    """
    This test asserts that setting a seed always returns the same values
    """

    source = SourceFaker()
    config = {"count": 1, "seed": 100, "parallelism": 1}
    stream_dict = {
        "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
        "sync_mode": "incremental",
        "destination_sync_mode": "overwrite",
    }
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    records = [row for row in iterator if row.type is Type.RECORD]
    assert records[0].record.data["occupation"] == "Sheriff Principal"
    assert records[0].record.data["email"] == "alleged2069+1@example.com"


def test_ensure_no_purchases_without_users():
    with pytest.raises(ValueError):
        source = SourceFaker()
        config = {"count": 100, "parallelism": 1}
        stream_dict = {
            "stream": {"name": "purchases", "json_schema": {"type": "object", "properties": {}}},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        }
        catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])
        state = {}
        iterator = source.read(logger, config, catalog, state)
        iterator.__next__()


def test_reviews_schema():
    source = SourceFaker()
    config = {"count": 1, "parallelism": 1}
    catalog = source.discover(None, config)
    catalog = AirbyteMessageSerializer.dump(AirbyteMessage(type=Type.CATALOG, catalog=catalog))
    reviews = [stream for stream in catalog["catalog"]["streams"] if stream["name"] == "reviews"]

    assert len(reviews) == 1
    assert reviews[0]["json_schema"]["properties"] == {
        "id": {"type": "integer"},
        "purchase_id": {"type": "integer"},
        "user_id": {"type": "integer"},
        "product_id": {"type": "integer"},
        "rating": {"type": "integer"},
        "title": {"type": "string"},
        "body": {"type": "string"},
        "created_at": {"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"},
        "updated_at": {"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"},
    }


def _reviews_catalog():
    stream_dict = {
        "stream": {"name": "reviews", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
        "sync_mode": "incremental",
        "destination_sync_mode": "overwrite",
    }
    return ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])


def test_read_reviews():
    source = SourceFaker()
    config = {"count": 100, "seed": 7, "parallelism": 1, "records_per_slice": 25}
    catalog = _reviews_catalog()
    iterator = source.read(logger, config, catalog, {})

    records = []
    state_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            records.append(row.record.data)
        if row.type is Type.STATE:
            state_rows_count += 1

    expected_ids = [pid for user_id in range(100) for pid in purchase_ids_for_user(user_id)]
    assert len(expected_ids) == 100
    assert len(records) == len(expected_ids)

    seen_ids = set()
    for record in records:
        assert isinstance(record["id"], int)
        assert isinstance(record["purchase_id"], int)
        assert isinstance(record["user_id"], int)
        assert isinstance(record["product_id"], int)
        assert record["id"] == record["purchase_id"]
        assert 1 <= record["rating"] <= 5
        assert isinstance(record["title"], str)
        assert isinstance(record["body"], str)
        datetime.datetime.fromisoformat(record["created_at"])
        seen_ids.add(record["id"])

    assert seen_ids == set(expected_ids)
    assert state_rows_count > 1


def test_reviews_deterministic_across_parallelism():
    source = SourceFaker()
    catalog = _reviews_catalog()

    def read_reviews(parallelism):
        config = {"count": 100, "seed": 7, "parallelism": parallelism, "records_per_slice": 25}
        iterator = source.read(logger, config, catalog, {})
        records = []
        for row in iterator:
            if row.type is Type.RECORD:
                data = dict(row.record.data)
                data.pop("updated_at")
                records.append(data)
        return sorted(records, key=lambda r: r["id"])

    assert read_reviews(1) == read_reviews(3)


def test_reviews_ids_match_purchases():
    source = SourceFaker()
    config = {"count": 50, "seed": 5, "parallelism": 1}
    stream_dicts = [
        {
            "stream": {"name": "purchases", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
        {
            "stream": {"name": "reviews", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
    ]
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(d) for d in stream_dicts])

    purchases = {}
    reviews = {}
    for row in source.read(logger, config, catalog, {}):
        if row.type is Type.RECORD:
            if row.record.stream == "purchases":
                purchases[row.record.data["id"]] = row.record.data["user_id"]
            elif row.record.stream == "reviews":
                reviews[row.record.data["purchase_id"]] = row.record.data["user_id"]

    assert set(purchases.keys()) == set(reviews.keys())
    for purchase_id, user_id in reviews.items():
        assert purchases[purchase_id] == user_id


def test_reviews_always_updated_false_with_state():
    source = SourceFaker()
    config = {"count": 10, "parallelism": 1, "always_updated": False}
    catalog = _reviews_catalog()
    iterator = source.read(logger, config, catalog, {})

    record_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1

    assert record_rows_count > 0

    from airbyte_cdk.models import AirbyteStateMessage, AirbyteStateType, AirbyteStreamState, StreamDescriptor
    from airbyte_cdk.models.airbyte_protocol import AirbyteStateBlob

    stream_descriptor = StreamDescriptor(name="reviews", namespace=None)
    stream_state = AirbyteStreamState(stream_descriptor=stream_descriptor, stream_state=AirbyteStateBlob(updated_at="something"))
    state = [AirbyteStateMessage(type=AirbyteStateType.STREAM, stream=stream_state)]
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1

    assert record_rows_count == 0
