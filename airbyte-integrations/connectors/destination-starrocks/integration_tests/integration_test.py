# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import random
import string
from logging import getLogger

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)

from destination_starrocks.destination import DestinationStarRocks


logger = getLogger("airbyte")


@pytest.fixture(name="config")
def config_fixture():
    with open("secrets/config.json") as f:
        return json.load(f)


@pytest.fixture(name="stream_name")
def stream_name_fixture():
    suffix = "".join(random.choices(string.ascii_lowercase, k=8))
    return f"airbyte_integration_test_{suffix}"


@pytest.fixture(name="engine")
def engine_fixture(config):
    connection_url = URL.create(
        drivername="starrocks",
        username=config["username"],
        password=config["password"],
        host=config["host"],
        port=config.get("port", 9030),
        database=config["database"],
    )
    engine = create_engine(connection_url)
    yield engine
    engine.dispose()


@pytest.fixture(name="stream_name", autouse=False)
def managed_stream_fixture(config, engine):
    """Yields a randomized stream name and drops related tables after the test."""
    suffix = "".join(random.choices(string.ascii_lowercase, k=8))
    name = f"airbyte_integration_test_{suffix}"
    yield name
    db = config["database"]
    with engine.connect() as conn:
        for table in [f"_airbyte_raw_{name}", name]:
            conn.execute(text(f"DROP TABLE IF EXISTS `{db}`.`{table}`"))
        conn.commit()


@pytest.fixture(name="catalog")
def catalog_fixture(stream_name):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=stream_name,
                    json_schema={
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                        },
                    },
                    supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )


def _record(stream_name, record_id, name):
    return AirbyteMessage(
        type=Type.RECORD,
        record=AirbyteRecordMessage(
            stream=stream_name,
            data={"id": record_id, "name": name},
            emitted_at=0,
        ),
    )


def _state():
    return AirbyteMessage(type=Type.STATE, state=AirbyteStateMessage(data={"cursor": 1}))


def _overwrite_catalog(stream_name):
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=stream_name,
                    json_schema={
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                        },
                    },
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )
        ]
    )


def test_check_valid_config(config):
    result = DestinationStarRocks().check(logger, config)
    assert result.status == Status.SUCCEEDED


def test_check_invalid_config():
    with open("integration_tests/invalid_config.json") as f:
        bad_config = json.load(f)
    result = DestinationStarRocks().check(logger, bad_config)
    assert result.status == Status.FAILED


def test_write_raw(config, stream_name, engine):
    config = {**config, "loading_mode": {"mode": "raw"}}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=stream_name,
                    json_schema={"type": "object", "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}},
                    supported_sync_modes=[SyncMode.incremental],
                ),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )
    messages = [_record(stream_name, 1, "Alice"), _record(stream_name, 2, "Bob"), _state()]

    output = list(DestinationStarRocks().write(config, catalog, iter(messages)))
    assert len([m for m in output if m.type == Type.STATE]) == 1

    with engine.connect() as conn:
        count = conn.execute(
            text(f"SELECT COUNT(*) FROM `{config['database']}`.`_airbyte_raw_{stream_name}`")
        ).fetchone()[0]
    assert count == 2


def test_write_typed(config, stream_name, engine, catalog):
    messages = [_record(stream_name, i, f"user_{i}") for i in range(3)] + [_state()]

    output = list(DestinationStarRocks().write(config, catalog, iter(messages)))
    assert len([m for m in output if m.type == Type.STATE]) == 1

    with engine.connect() as conn:
        count = conn.execute(
            text(f"SELECT COUNT(*) FROM `{config['database']}`.`{stream_name}`")
        ).fetchone()[0]
    assert count == 3


def test_write_overwrite_replaces_data(config, stream_name, engine, catalog):
    # First sync: append 3 records
    list(DestinationStarRocks().write(config, catalog, iter([_record(stream_name, i, f"user_{i}") for i in range(3)])))

    # Second sync: overwrite with 1 record
    list(DestinationStarRocks().write(config, _overwrite_catalog(stream_name), iter([_record(stream_name, 99, "only_one")])))

    with engine.connect() as conn:
        count = conn.execute(
            text(f"SELECT COUNT(*) FROM `{config['database']}`.`{stream_name}`")
        ).fetchone()[0]
    assert count == 1
