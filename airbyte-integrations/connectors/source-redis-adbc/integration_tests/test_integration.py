# Copyright (c) 2026 Albert Wong
# SPDX-License-Identifier: MIT
import os
import uuid
from contextlib import closing

import pytest
from source_redis_adbc.backend import AdbcBackend, connect, quote
from source_redis_adbc.source import SourceRedisAdbc

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer, Status


pytestmark = pytest.mark.integration


@pytest.fixture
def seeded():
    uri = os.environ.get("REDIS_URI")
    if not uri:
        pytest.skip("Set REDIS_URI to a disposable Redis Search database")
    config = {"uri": uri, "batch_size": 2}
    name = "airbyte_it_" + uuid.uuid4().hex[:12]
    with closing(connect(config)) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(f"CREATE TABLE {quote(name)} (id BIGINT, label VARCHAR, amount DECIMAL(30,9))")
        try:
            cursor.execute(
                f"INSERT INTO {quote(name)} VALUES (9007199254740993, 'first', 12345678901234567890.123456789), (2, NULL, NULL), (3, 'third', 1.000000001), (4, 'fourth', 0), (5, 'fifth', -0.000000001)"
            )
            yield config, name
        finally:
            cursor.execute(f"DROP TABLE {quote(name)}")


def selected_catalog(source, config, name, fields=None):
    stream = next(s for s in source.discover(None, config).streams if s.name == name)
    properties = stream.json_schema["properties"]
    if fields:
        properties = {field: properties[field] for field in fields}
    return ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {
                        "name": name,
                        "namespace": stream.namespace,
                        "json_schema": {"type": "object", "properties": properties},
                        "supported_sync_modes": ["full_refresh"],
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite",
                }
            ]
        }
    )


def test_native_check_discover_multibatch_projection_retry(seeded):
    config, name = seeded
    source = SourceRedisAdbc()
    assert source.check(None, config).status == Status.SUCCEEDED
    catalog = selected_catalog(source, config, name)
    records = [m.record.data for m in source.read(None, config, catalog)]
    assert len(records) == 5
    by_id = {row["id"]: row for row in records}
    assert by_id["9007199254740993"]["amount"] == "12345678901234567890.123456789"
    assert by_id["2"]["label"] is None
    assert by_id["5"]["amount"] == "-0.000000001"
    # A fresh read repeats the full result without persisted cursor state.
    assert sorted(m.record.data["id"] for m in source.read(None, config, catalog)) == sorted(by_id)
    projected = selected_catalog(source, config, name, ["id"])
    assert all(set(m.record.data) == {"id"} for m in source.read(None, config, projected))


def test_native_empty_table(seeded):
    config, name = seeded
    with closing(connect(config)) as connection, closing(connection.cursor()) as cursor:
        cursor.execute(f"DELETE FROM {quote(name)}")
    source = SourceRedisAdbc()
    assert list(source.read(None, config, selected_catalog(source, config, name))) == []


def test_native_reader_spans_multiple_batches_and_cancel(seeded):
    config, name = seeded
    backend = AdbcBackend(config)
    with backend.connection() as connection:
        with backend.query(connection, f"SELECT * FROM {quote(name)}") as reader:
            batches = list(reader)
            assert sum(b.num_rows for b in batches) == 5
            assert len(batches) >= 3
    with closing(
        backend.read([(t.namespace, t.name, schema["properties"]) for t, schema in backend.discover() if t.name == name])
    ) as records:
        next(records)  # Abandon before exhausting; context manager cancels.
