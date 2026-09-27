#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

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


def test_reviews_schema():
    source = SourceFaker()
    config = {"count": 1, "parallelism": 1}
    catalog = source.discover(None, config)
    catalog = AirbyteMessageSerializer.dump(AirbyteMessage(type=Type.CATALOG, catalog=catalog))

    reviews_stream = next(stream for stream in catalog["catalog"]["streams"] if stream["name"] == "reviews")
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


def test_read_reviews():
    source = SourceFaker()
    config = {"count": 100, "seed": 100, "parallelism": 1, "records_per_slice": 10}
    stream_dicts = [
        {
            "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
        {
            "stream": {"name": "reviews", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
    ]
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict) for stream_dict in stream_dicts])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    state_rows = []
    for row in iterator:
        if row.type is Type.RECORD:
            if row.record.stream == "reviews":
                record_rows_count = record_rows_count + 1
                assert 1 <= row.record.data["rating"] <= 5
                assert row.record.data["title"]
                assert row.record.data["body"]
        if row.type is Type.STATE:
            if row.state.stream.stream_descriptor.name == "reviews":
                state_rows.append(row)

    assert record_rows_count == 100
    assert len(state_rows) >= 10
    last_state = state_rows[-1].state.stream.stream_state
    assert last_state.updated_at
    assert last_state.loop_offset == 100


def test_reviews_match_purchases():
    source = SourceFaker()
    config = {"count": 100, "seed": 100, "parallelism": 1, "records_per_slice": 10}
    stream_dicts = [
        {
            "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        },
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
    catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict) for stream_dict in stream_dicts])
    state = {}
    iterator = source.read(logger, config, catalog, state)

    purchases = {}
    reviews = []
    for row in iterator:
        if row.type is Type.RECORD:
            if row.record.stream == "purchases":
                purchases[row.record.data["id"]] = row.record.data
            elif row.record.stream == "reviews":
                reviews.append(row.record.data)

    assert {r["purchase_id"] for r in reviews} == set(purchases.keys())
    for review in reviews:
        purchase = purchases[review["purchase_id"]]
        assert review["id"] == review["purchase_id"]
        assert review["user_id"] == purchase["user_id"]


def test_review_generator_created_at_after_purchase():
    from source_faker.review_generator import ReviewGenerator

    gen = ReviewGenerator("reviews", 100)
    gen.prepare()

    unpurchased_seen = False
    for user_id in range(0, 40):
        purchases = {m.record.data["id"]: m.record.data for m in gen.purchases_for(user_id)}
        reviews = gen.generate(user_id)
        assert len(reviews) == len(purchases)
        for message in reviews:
            review = message.record.data
            purchase = purchases[review["purchase_id"]]
            assert review["product_id"] == purchase["product_id"]
            assert review["user_id"] == purchase["user_id"]
            assert review["created_at"] >= (purchase["purchased_at"] or purchase["added_to_cart_at"])
            assert 1 <= review["rating"] <= 5
            if purchase["purchased_at"] is None:
                unpurchased_seen = True
    assert unpurchased_seen


def test_reviews_deterministic_with_seed():
    def read_reviews(parallelism):
        source = SourceFaker()
        config = {"count": 30, "seed": 100, "parallelism": parallelism}
        stream_dict = {
            "stream": {"name": "reviews", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "overwrite",
        }
        catalog = ConfiguredAirbyteCatalog(streams=[ConfiguredAirbyteStreamSerializer.load(stream_dict)])
        iterator = source.read(logger, config, catalog, {})
        records = []
        for row in iterator:
            if row.type is Type.RECORD and row.record.stream == "reviews":
                data = dict(row.record.data)
                data.pop("updated_at")
                records.append(data)
        return records

    single_worker = read_reviews(parallelism=1)
    assert single_worker == read_reviews(parallelism=1)
    assert sorted(single_worker, key=lambda r: r["id"]) == sorted(read_reviews(parallelism=4), key=lambda r: r["id"])


def test_purchases_unchanged_with_seed(tmp_path):
    expected_purchases = [
        {
            "id": 1,
            "product_id": 19,
            "user_id": 1,
            "created_at": "2004-11-20 11:10:35.747117",
            "added_to_cart_at": "2020-01-21T11:10:35+00:00",
            "purchased_at": None,
            "returned_at": None,
        },
        {
            "id": 2,
            "product_id": 46,
            "user_id": 2,
            "created_at": "2018-10-02 23:33:34.649758",
            "added_to_cart_at": "2020-08-27T23:33:34+00:00",
            "purchased_at": None,
            "returned_at": None,
        },
        {
            "id": 3,
            "product_id": 92,
            "user_id": 3,
            "created_at": "2014-04-17 04:05:51.055432",
            "added_to_cart_at": "2018-05-20T04:05:51+00:00",
            "purchased_at": "2021-08-31T04:05:51+00:00",
            "returned_at": None,
        },
        {
            "id": 4,
            "product_id": 55,
            "user_id": 4,
            "created_at": "2019-07-21 15:42:04.258410",
            "added_to_cart_at": "2025-11-25T15:42:04+00:00",
            "purchased_at": None,
            "returned_at": None,
        },
        {
            "id": 5,
            "product_id": 6,
            "user_id": 5,
            "created_at": "2016-07-24 19:27:53.417790",
            "added_to_cart_at": "2024-09-06T19:27:53+00:00",
            "purchased_at": "2026-03-16T19:27:53+00:00",
            "returned_at": None,
        },
        {
            "id": 6,
            "product_id": 96,
            "user_id": 6,
            "created_at": "2004-03-12 06:04:37.248771",
            "added_to_cart_at": "2012-07-04T06:04:37+00:00",
            "purchased_at": None,
            "returned_at": None,
        },
        {
            "id": 7,
            "product_id": 49,
            "user_id": 8,
            "created_at": "2020-09-15 20:55:32.716593",
            "added_to_cart_at": "2025-08-28T20:55:32+00:00",
            "purchased_at": "2026-05-16T20:55:32+00:00",
            "returned_at": None,
        },
        {
            "id": 8,
            "product_id": 11,
            "user_id": 9,
            "created_at": "2006-07-08 23:13:38.615482",
            "added_to_cart_at": "2024-09-08T23:13:38+00:00",
            "purchased_at": "2026-08-15T23:13:38+00:00",
            "returned_at": None,
        },
        {
            "id": 9,
            "product_id": 78,
            "user_id": 9,
            "created_at": "2001-07-04 15:55:11.322265",
            "added_to_cart_at": "2021-04-27T15:55:11+00:00",
            "purchased_at": "2026-01-06T15:55:11+00:00",
            "returned_at": None,
        },
        {
            "id": 10,
            "product_id": 92,
            "user_id": 10,
            "created_at": "2005-04-17 13:08:09.629238",
            "added_to_cart_at": "2017-03-10T13:08:09+00:00",
            "purchased_at": "2018-10-26T13:08:09+00:00",
            "returned_at": None,
        },
        {
            "id": 11,
            "product_id": 80,
            "user_id": 11,
            "created_at": "2008-03-04 03:49:09.004539",
            "added_to_cart_at": "2017-05-31T03:49:09+00:00",
            "purchased_at": None,
            "returned_at": None,
        },
        {
            "id": 12,
            "product_id": 62,
            "user_id": 12,
            "created_at": "2013-05-11 08:46:28.434504",
            "added_to_cart_at": "2014-11-23T08:46:28+00:00",
            "purchased_at": "2016-12-15T08:46:28+00:00",
            "returned_at": None,
        },
        {
            "id": 13,
            "product_id": 49,
            "user_id": 13,
            "created_at": "2023-11-07 00:29:12.845865",
            "added_to_cart_at": "2024-12-09T00:29:12+00:00",
            "purchased_at": "2026-02-19T00:29:12+00:00",
            "returned_at": None,
        },
        {
            "id": 14,
            "product_id": 78,
            "user_id": 14,
            "created_at": "2008-02-06 22:24:42.878164",
            "added_to_cart_at": "2017-10-07T22:24:42+00:00",
            "purchased_at": "2019-04-06T22:24:42+00:00",
            "returned_at": None,
        },
        {
            "id": 15,
            "product_id": 47,
            "user_id": 15,
            "created_at": "2007-12-06 02:40:07.497866",
            "added_to_cart_at": "2012-07-30T02:40:07+00:00",
            "purchased_at": "2025-10-13T02:40:07+00:00",
            "returned_at": None,
        },
        {
            "id": 16,
            "product_id": 81,
            "user_id": 16,
            "created_at": "2003-03-09 22:49:10.762837",
            "added_to_cart_at": "2016-05-30T22:49:10+00:00",
            "purchased_at": "2017-11-04T22:49:10+00:00",
            "returned_at": None,
        },
        {
            "id": 17,
            "product_id": 79,
            "user_id": 18,
            "created_at": "2002-06-18 04:29:58.826481",
            "added_to_cart_at": "2022-03-23T04:29:58+00:00",
            "purchased_at": None,
            "returned_at": None,
        },
        {
            "id": 18,
            "product_id": 99,
            "user_id": 19,
            "created_at": "2014-11-08 04:45:00.273470",
            "added_to_cart_at": "2020-11-04T04:45:00+00:00",
            "purchased_at": "2026-02-11T04:45:00+00:00",
            "returned_at": None,
        },
        {
            "id": 19,
            "product_id": 69,
            "user_id": 19,
            "created_at": "2000-05-17 15:35:37.627331",
            "added_to_cart_at": "2020-06-06T15:35:37+00:00",
            "purchased_at": None,
            "returned_at": None,
        },
        {
            "id": 20,
            "product_id": 66,
            "user_id": 20,
            "created_at": "2005-08-09 08:06:57.727600",
            "added_to_cart_at": "2020-12-06T08:06:57+00:00",
            "purchased_at": "2025-04-24T08:06:57+00:00",
            "returned_at": None,
        },
    ]

    # Read in a subprocess so worker identities match the baseline (users=1, purchases=2).
    import subprocess
    import sys

    config = {"count": 20, "seed": 100, "parallelism": 1}
    catalog = {
        "streams": [
            {
                "stream": {"name": "users", "json_schema": {"type": "object", "properties": {}}, "supported_sync_modes": ["incremental"]},
                "sync_mode": "incremental",
                "destination_sync_mode": "overwrite",
            },
            {
                "stream": {
                    "name": "purchases",
                    "json_schema": {"type": "object", "properties": {}},
                    "supported_sync_modes": ["incremental"],
                },
                "sync_mode": "incremental",
                "destination_sync_mode": "overwrite",
            },
        ]
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config))
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(catalog))

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from source_faker.run import run; run()",
            "read",
            "--config",
            str(config_path),
            "--catalog",
            str(catalog_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    actual_purchases = []
    for line in result.stdout.splitlines():
        message = json.loads(line)
        if message.get("type") == "RECORD" and message["record"]["stream"] == "purchases":
            data = message["record"]["data"]
            actual_purchases.append(
                {
                    "id": data["id"],
                    "product_id": data["product_id"],
                    "user_id": data["user_id"],
                    "created_at": data["created_at"].replace("T", " "),
                    "added_to_cart_at": data["added_to_cart_at"],
                    "purchased_at": data.get("purchased_at"),
                    "returned_at": data.get("returned_at"),
                }
            )

    assert actual_purchases == expected_purchases
