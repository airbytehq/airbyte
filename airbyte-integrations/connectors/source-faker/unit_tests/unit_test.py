#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import TYPE_CHECKING, Literal

import jsonschema
import pytest
from source_faker import SourceFaker
from source_faker.models import (
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Type,
)


if TYPE_CHECKING:
    from collections.abc import Iterator


class MockLogger:
    def debug(a, b, **kwargs) -> None:
        pass

    def info(a, b, **kwargs) -> None:
        pass

    def exception(a, b, **kwargs) -> None:
        print(b)
        pass

    def isEnabledFor(a, b, **kwargs) -> Literal[False]:
        return False


logger = MockLogger()


def schemas_are_valid():
    source = SourceFaker()
    config = {"count": 1, "parallelism": 1}
    catalog = source.discover(
        logger=None,
        config=config,
    )
    catalog = AirbyteMessage(type=Type.CATALOG, catalog=catalog).to_dict()
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]

    for schema in schemas:
        jsonschema.Draft7Validator.check_schema(schema)


def test_source_streams() -> None:
    source = SourceFaker()
    config = {"count": 1, "parallelism": 1}
    catalog = source.discover(None, config)
    # catalog_msg = AirbyteMessage(type=Type.CATALOG, catalog=catalog).to_dict()
    schemas = [stream.json_schema for stream in catalog.streams]

    assert len(schemas) == 3
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


def test_read_small_random_data() -> None:
    source = SourceFaker()
    config = {"count": 10, "parallelism": 1}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream.from_dict(
                {
                    "stream": {"name": "users", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                }
            )
        ]
    )
    iterator = source.read(
        logger=logger,
        config=config,
        catalog=catalog,
        state=[],
    )

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


def test_read_always_updated() -> None:
    source = SourceFaker()
    config = {"count": 10, "parallelism": 1, "always_updated": False}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream.from_dict(
                {
                    "stream": {"name": "users", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                }
            )
        ]
    )
    state = {}
    iterator: Iterator[AirbyteMessage] = source.read(logger, config, catalog, state)

    record_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1

    assert record_rows_count == 10

    state = {"users": {"updated_at": "something"}}
    iterator = source.read(
        logger=logger,
        config=config,
        catalog=catalog,
        state=state,
    )

    record_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1

    assert record_rows_count == 0


def test_read_products() -> None:
    source = SourceFaker()
    config = {"count": 999, "parallelism": 1}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream.from_dict(
                {
                    "stream": {"name": "products", "json_schema": {}, "supported_sync_modes": ["full_refresh"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                }
            )
        ]
    )
    state = {}
    iterator: Iterator[AirbyteMessage] = source.read(
        logger=logger,
        config=config,
        catalog=catalog,
        state=state,
    )

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
    assert state_rows_count == 2


def test_read_big_random_data() -> None:
    source = SourceFaker()
    config = {"count": 1000, "records_per_slice": 100, "parallelism": 1}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream.from_dict(
                {
                    "stream": {"name": "users", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                },
            ),
            ConfiguredAirbyteStream.from_dict(
                {
                    "stream": {"name": "products", "json_schema": {}, "supported_sync_modes": ["full_refresh"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                },
            ),
        ]
    )
    state = {}
    iterator = source.read(
        logger=logger,
        config=config,
        catalog=catalog,
        state=state,
    )

    record_rows_count = 0
    state_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1

    assert record_rows_count == 1000 + 100  # 1000 users, and 100 products
    assert state_rows_count == 10 + 1 + 1 + 1


def test_with_purchases() -> None:
    source = SourceFaker()
    config = {"count": 1000, "parallelism": 1}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream.from_dict(
                {
                    "stream": {"name": "users", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                },
            ),
            ConfiguredAirbyteStream.from_dict(
                {
                    "stream": {"name": "products", "json_schema": {}, "supported_sync_modes": ["full_refresh"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                },
            ),
            ConfiguredAirbyteStream.from_dict(
                {
                    "stream": {"name": "purchases", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                },
            ),
        ]
    )
    state = {}
    iterator = source.read(
        logger=logger,
        config=config,
        catalog=catalog,
        state=state,
    )

    record_rows_count = 0
    state_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD:
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1

    assert record_rows_count > 1000 + 100  # should be greater than 1000 users, and 100 products
    assert state_rows_count > 10 + 1  # should be greater than 1000/100, and one state for the products


def test_read_with_seed() -> None:
    """
    This test asserts that setting a seed always returns the same values
    """

    source = SourceFaker()
    config = {"count": 1, "seed": 100, "parallelism": 1}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream.from_dict(
                {
                    "stream": {"name": "users", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                }
            )
        ]
    )
    state = {}
    iterator = source.read(
        logger=logger,
        config=config,
        catalog=catalog,
        state=state,
    )

    records = [row for row in iterator if row.type is Type.RECORD]
    assert records[0].record.data["occupation"] == "Sheriff Principal"
    assert records[0].record.data["email"] == "alleged2069+1@example.com"


def test_ensure_no_purchases_without_users() -> None:
    with pytest.raises(ValueError):  # noqa: PT011, PT012  (too broad raises block)
        source = SourceFaker()
        config = {"count": 100, "parallelism": 1}
        catalog = ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream.from_dict(
                    {
                        "stream": {"name": "purchases", "json_schema": {}},
                        "sync_mode": "incremental",
                        "destination_sync_mode": "overwrite",
                    },
                )
            ]
        )
        state = {}
        iterator: Iterator[AirbyteMessage] = source.read(
            logger=logger,
            config=config,
            catalog=catalog,
            state=state,
        )
        iterator.__next__()
