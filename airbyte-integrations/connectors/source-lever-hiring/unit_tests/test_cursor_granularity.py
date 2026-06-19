# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from pathlib import Path

import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
API_BASE = "https://api.sandbox.lever.co/v1"

TEST_CONFIG = {
    "credentials": {
        "auth_type": "Api Key",
        "api_key": "test-api-key",
    },
    "environment": "Sandbox",
    "start_date": "2024-01-01T00:00:00Z",
}


def _get_source(config, state=None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(path_to_yaml=str(MANIFEST_PATH), catalog=catalog, config=config, state=state)


def read_from_stream(cfg, stream: str, sync_mode, state=None, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream, sync_mode).build()
    return read(_get_source(cfg, state), cfg, catalog, state, expecting_exception)


def load_manifest() -> dict:
    with open(MANIFEST_PATH, "r") as f:
        return yaml.safe_load(f)


def find_all_incremental_syncs(obj, path=""):
    """Recursively find all incremental_sync blocks in the manifest."""
    results = []
    if isinstance(obj, dict):
        if "incremental_sync" in obj:
            results.append((path, obj["incremental_sync"]))
        for key, value in obj.items():
            results.extend(find_all_incremental_syncs(value, f"{path}.{key}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(find_all_incremental_syncs(item, f"{path}[{i}]"))
    return results


def test_cursor_granularity_matches_datetime_format():
    """All incremental_sync blocks must have cursor_granularity aligned with datetime_format.

    datetime_format '%ms' means epoch-milliseconds, so cursor_granularity must be
    PT0.001S (1 millisecond). Previously it was PT0.000001S (1 microsecond), which is
    finer than the format can represent, causing cursor advancement failures.
    """
    manifest = load_manifest()
    incremental_syncs = find_all_incremental_syncs(manifest)
    assert len(incremental_syncs) >= 7, f"Expected at least 7 incremental_sync blocks, found {len(incremental_syncs)}"

    for path, sync_config in incremental_syncs:
        datetime_format = sync_config.get("datetime_format")
        cursor_granularity = sync_config.get("cursor_granularity")
        if datetime_format == "%ms":
            assert cursor_granularity == "PT0.001S", (
                f"incremental_sync at {path}: cursor_granularity is '{cursor_granularity}' "
                f"but must be 'PT0.001S' to match millisecond datetime_format '%ms'. "
                f"Sub-millisecond granularity causes cursor stuck issues."
            )


def test_opportunities_cursor_advances_across_syncs(requests_mock):
    """Verify that the cursor advances after reading records with incremental sync.

    This is a regression test for the stuck cursor issue where cursor_granularity
    PT0.000001S (microsecond) paired with datetime_format '%ms' (millisecond) caused
    the cursor to never advance.
    """
    ts_record_1 = 1704067200000  # 2024-01-01T00:00:00Z in ms
    ts_record_2 = 1704153600000  # 2024-01-02T00:00:00Z in ms

    requests_mock.get(
        f"{API_BASE}/opportunities",
        [
            {
                "json": {
                    "data": [
                        {"id": "opp-1", "updatedAt": ts_record_1, "name": "Test Opp 1"},
                        {"id": "opp-2", "updatedAt": ts_record_2, "name": "Test Opp 2"},
                    ],
                    "hasNext": False,
                },
                "status_code": 200,
            },
        ],
    )

    output = read_from_stream(TEST_CONFIG, "opportunities", SyncMode.incremental)
    records = output.records
    assert len(records) >= 1

    state_messages = output.state_messages
    assert len(state_messages) > 0, "Expected at least one state message after incremental read"

    final_state = state_messages[-1]
    state_blob = final_state.state.stream.stream_state
    state_dict = state_blob.__dict__
    cursor_value = state_dict.get("updatedAt")
    assert cursor_value is not None, (
        f"Cursor value 'updatedAt' should be present in state. "
        f"State keys: {list(state_dict.keys())}"
    )

    cursor_int = int(cursor_value) if isinstance(cursor_value, str) else cursor_value
    assert cursor_int >= ts_record_2, (
        f"Cursor should have advanced to at least {ts_record_2} "
        f"but is stuck at {cursor_int}"
    )
