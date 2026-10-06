# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Smoke tests against a real SAP HANA instance.

Put a real config in secrets/config.json (see sample_config.json), then:

    HANA_TEST_TABLE=CSKT uv run pytest integration_tests -m integration -s

Only the first HANA_TEST_LIMIT records (default 100) of HANA_TEST_TABLE are read.
"""

import json
import logging
import os
from itertools import islice
from pathlib import Path

import pytest
from source_sap_hana import SourceSapHana

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, Status, SyncMode, Type


CONFIG_PATH = Path(__file__).parent.parent / "secrets" / "config.json"

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not CONFIG_PATH.exists(), reason="secrets/config.json not found"),
]

logger = logging.getLogger("airbyte")


@pytest.fixture(scope="module")
def config():
    return json.loads(CONFIG_PATH.read_text())


@pytest.fixture(scope="module")
def catalog(config):
    return SourceSapHana().discover(logger, config)


def test_check(config):
    status = SourceSapHana().check(logger, config)
    assert status.status == Status.SUCCEEDED, status.message


def test_discover(catalog):
    assert catalog.streams, "no streams discovered: check schemas / table_name_patterns"
    for stream in catalog.streams:
        assert stream.json_schema["properties"], f"{stream.name} has no columns"


def _sample(config, stream, limit):
    """Reads the first `limit` records of one stream, fetching no more than needed from HANA."""
    config = {**config, "fetch_size": max(limit, 100)}
    configured = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(stream=stream, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.overwrite)
        ]
    )
    messages = SourceSapHana().read(logger, config, configured, [])
    try:
        return [m.record.data for m in islice((m for m in messages if m.type == Type.RECORD), limit)]
    finally:
        messages.close()


def _assert_matches_schema(stream, records):
    types = {"integer": int, "number": (int, float), "string": str, "boolean": bool}
    for record in records:
        assert set(record) <= set(stream.json_schema["properties"]), f"{stream.name}: unexpected columns"
        for column, value in record.items():
            if value is None:
                continue
            declared = [t for t in stream.json_schema["properties"][column]["type"] if t != "null"][0]
            assert isinstance(value, types[declared]), f"{stream.name}.{column}: {value!r} is not {declared}"
            if declared == "integer":
                assert not isinstance(value, bool)


def test_read_sample(config, catalog):
    table = os.environ.get("HANA_TEST_TABLE") or catalog.streams[0].name
    limit = int(os.environ.get("HANA_TEST_LIMIT", "100"))
    stream = next(s for s in catalog.streams if s.name == table)
    records = _sample(config, stream, limit)
    assert records, f"{table} returned no records"
    json.dumps(records)  # everything must be JSON-serializable
    _assert_matches_schema(stream, records)
    print(f"\n{table}: first record = {records[0]}")


def test_every_stream_matches_its_schema(config, catalog):
    """Reads a few rows of every discovered stream and checks values against the discovered JSON schema."""
    limit = int(os.environ.get("HANA_TEST_ALL_LIMIT", "20"))
    for stream in catalog.streams:
        records = _sample(config, stream, limit)
        json.dumps(records)
        _assert_matches_schema(stream, records)
        print(f"{stream.namespace}.{stream.name}: {len(records)} records OK")


def test_resumable_full_refresh_reconciles_with_count(config, catalog):
    """Reads a whole (small) table with tiny pages and checks nothing is skipped or duplicated across pages."""
    from hdbcli import dbapi
    from source_sap_hana.client import HanaClient, qualified_name
    from source_sap_hana.config import HanaConfig

    table = os.environ.get("HANA_RECON_TABLE", "CSKT")
    stream = next(s for s in catalog.streams if s.name == table)
    assert stream.source_defined_primary_key, f"{table} needs a primary key for this test"
    key = [k[0] for k in stream.source_defined_primary_key]

    client = HanaClient(HanaConfig.from_mapping(config), logger)
    conn = dbapi.connect(**client.connect_kwargs())
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {qualified_name(stream.namespace, table)}")
        expected = cursor.fetchone()[0]
    finally:
        conn.close()

    page_config = {**config, "full_refresh_page_size": 100, "resumable_full_refresh": True}
    configured_stream = ConfiguredAirbyteStream(
        stream=stream, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.overwrite
    )
    keys = [
        tuple(m.record.data[k] for k in key)
        for m in SourceSapHana().read(logger, page_config, ConfiguredAirbyteCatalog(streams=[configured_stream]), [])
        if m.type == Type.RECORD
    ]
    assert len(keys) == expected
    assert len(set(keys)) == expected
    print(f"\n{table}: {expected} rows in pages of 100, reconciled with COUNT(*)")
