#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import jsonschema
import pytest
from source_faker import SourceFaker

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


def test_ensure_no_reviews_without_users():
    with pytest.raises(ValueError):
        source = SourceFaker()
        config = {"count": 100, "parallelism": 1}
        stream_dict = {
            "stream": {"name": "reviews", "json_schema": {"type": "object", "properties": {}}},
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
    streams = catalog["catalog"]["streams"]

    assert streams[-1]["name"] == "reviews"
    reviews_stream = streams[-1]

    assert reviews_stream["json_schema"]["properties"] == {
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
    assert reviews_stream["source_defined_primary_key"] == [["id"]]
    assert reviews_stream["default_cursor_field"] == ["updated_at"]


def _catalog_for(stream_names):
    stream_dicts = [
        {
            "stream": {"name": name, "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        }
        for name in stream_names
    ]
    return ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(s) for s in stream_dicts])


def _records(source, config, stream_names):
    catalog = _catalog_for(stream_names)
    return [row for row in source.read(logger, config, catalog, {}) if row.type is Type.RECORD]


def test_read_reviews():
    source = SourceFaker()
    config = {"count": 100, "records_per_slice": 10, "parallelism": 1, "seed": 7}

    catalog = _catalog_for(["reviews"])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    state_rows_count = 0
    last_state = None
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1
            last_state = row

    purchase_records = _records(source, config, ["purchases"])
    assert record_rows_count == len(purchase_records)
    assert state_rows_count >= 10
    stream_state = vars(last_state.state.stream.stream_state)
    assert set(stream_state.keys()) >= {"seed", "updated_at", "loop_offset"}
    assert stream_state["loop_offset"] == 100


def test_reviews_one_per_purchase():
    source = SourceFaker()
    config = {"count": 100, "records_per_slice": 10, "parallelism": 1, "seed": 7}

    purchase_records = _records(source, config, ["purchases"])
    review_records = _records(source, config, ["reviews"])

    purchases_by_id = {r.record.data["id"]: r.record.data for r in purchase_records}
    assert {r.record.data["purchase_id"] for r in review_records} == set(purchases_by_id.keys())
    for r in review_records:
        data = r.record.data
        assert data["id"] == data["purchase_id"]
        assert data["user_id"] == purchases_by_id[data["purchase_id"]]["user_id"]


def test_review_generator_created_at_after_purchase():
    from source_faker import purchase_generator as purchase_generator_module
    from source_faker.review_generator import ReviewGenerator

    seed = 100
    gen = ReviewGenerator("reviews", seed)
    gen.prepare()

    purchase_gen = purchase_generator_module.PurchaseGenerator("purchases", seed)

    null_purchased_at_seen = False
    for user_id in range(200):
        reviews = gen.generate(user_id)

        # regenerate the same purchases in-process with the same per-user seed
        purchase_generator_module.dt.reseed(seed + user_id)
        purchase_generator_module.numeric.reseed(seed + user_id)
        purchases = purchase_gen.generate(user_id)
        purchases_by_id = {p.record.data["id"]: p.record.data for p in purchases}

        for review_message in reviews:
            data = review_message.record.data
            purchase = purchases_by_id[data["purchase_id"]]
            assert data["user_id"] == purchase["user_id"]
            assert data["product_id"] == purchase["product_id"]
            assert 1 <= data["rating"] <= 5
            assert isinstance(data["title"], str) and data["title"]
            assert isinstance(data["body"], str) and data["body"]
            if purchase["purchased_at"] is not None:
                assert data["created_at"] >= purchase["purchased_at"]
            else:
                null_purchased_at_seen = True
                assert data["created_at"] >= purchase["added_to_cart_at"]

    assert null_purchased_at_seen


def test_reviews_deterministic_with_seed():
    def read_review_data(parallelism):
        source = SourceFaker()
        config = {"count": 50, "seed": 100, "parallelism": parallelism}
        records = _records(source, config, ["reviews"])
        data = []
        for r in records:
            d = dict(r.record.data)
            d.pop("updated_at", None)
            data.append(d)
        return data

    first = read_review_data(1)
    second = read_review_data(1)
    assert first == second

    parallel = read_review_data(3)
    assert first == parallel


def test_existing_streams_unchanged_with_seed():
    """
    Regression guard: seeded purchase generation must not change.
    Uses the in-process generator path because pool-based reads derive the worker seed
    from multiprocessing._identity, a global counter that depends on how many pools
    were created earlier in the process.
    """
    import datetime

    from source_faker.purchase_generator import PurchaseGenerator

    gen = PurchaseGenerator("purchases", 100)
    gen.prepare()

    actual = []
    for user_id in range(5):
        for m in gen.generate(user_id):
            d = dict(m.record.data)
            d.pop("updated_at", None)
            actual.append(d)

    assert actual == [
        {
            "id": 1,
            "product_id": 19,
            "user_id": 1,
            "created_at": datetime.datetime(2004, 8, 15, 5, 45, 25, 767514),
            "added_to_cart_at": "2014-12-05T05:45:25+00:00",
            "purchased_at": "2018-11-05T05:45:25+00:00",
            "returned_at": None,
        },
        {
            "id": 2,
            "product_id": 51,
            "user_id": 2,
            "created_at": datetime.datetime(2006, 6, 8, 9, 53, 49, 213772),
            "added_to_cart_at": "2022-11-07T09:53:49+00:00",
            "purchased_at": "2025-04-12T09:53:49+00:00",
            "returned_at": None,
        },
        {
            "id": 3,
            "product_id": 15,
            "user_id": 3,
            "created_at": datetime.datetime(2005, 3, 7, 11, 23, 40, 429594),
            "added_to_cart_at": "2017-02-17T11:23:40+00:00",
            "purchased_at": "2018-01-11T11:23:40+00:00",
            "returned_at": None,
        },
        {
            "id": 4,
            "product_id": 59,
            "user_id": 4,
            "created_at": datetime.datetime(2000, 10, 13, 4, 49, 54, 593659),
            "added_to_cart_at": "2012-08-06T04:49:54+00:00",
            "purchased_at": "2017-03-08T04:49:54+00:00",
            "returned_at": None,
        },
        {
            "id": 5,
            "product_id": 30,
            "user_id": 5,
            "created_at": datetime.datetime(2005, 4, 6, 0, 58, 42, 248748),
            "added_to_cart_at": "2012-03-14T00:58:42+00:00",
            "purchased_at": None,
            "returned_at": None,
        },
    ]
