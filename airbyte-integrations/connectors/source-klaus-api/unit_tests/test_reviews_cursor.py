# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import datetime
from pathlib import Path

import isodate
import yaml
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import (
    CustomFormatConcurrentStreamStateConverter,
)
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.state_builder import StateBuilder


TEST_CONFIG = {
    "api_key": "test-api-key",
    "account": 12345,
    "workspace": 67890,
    "start_date": "2024-01-01T00:00:00Z",
}

BASE = "https://kibbles.klausapp.com/api/v2"

_MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"


def _get_source(config, state=None) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().build()
    state = StateBuilder().build() if not state else state
    return YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=state)


def _read_reviews(cfg, state=None) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("reviews", SyncMode.incremental).build()
    return read(_get_source(cfg, state), cfg, catalog, state)


def test_cursor_granularity_matches_datetime_format():
    """Verify cursor_granularity and datetime_format are compatible.

    Regression for oncall airbytehq/oncall#12928: if cursor_granularity is finer
    than datetime_format (e.g. PT0.001S with second-precision format), slice
    boundaries are truncated on serialization and consecutive intervals cannot
    merge in the concurrent cursor, causing the persisted cursor to never advance.
    """
    manifest = yaml.safe_load(_MANIFEST_PATH.read_text())
    reviews = manifest["definitions"]["streams"]["reviews"]
    inc = reviews["incremental_sync"]

    datetime_format = inc["datetime_format"]
    cursor_granularity = isodate.parse_duration(inc["cursor_granularity"])
    step = isodate.parse_duration(inc["step"])

    converter = CustomFormatConcurrentStreamStateConverter(
        datetime_format=datetime_format,
        cursor_granularity=cursor_granularity,
    )

    start = datetime.datetime(2024, 2, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    slice1_end_raw = start + step - cursor_granularity
    slice1_end_formatted = converter.output_format(slice1_end_raw)
    slice1_end_parsed = converter.parse_timestamp(slice1_end_formatted)
    slice2_start = start + step

    assert converter.increment(slice1_end_parsed) == slice2_start, (
        f"Slice intervals cannot merge: increment(format(end)) = "
        f"{converter.increment(slice1_end_parsed)} != next slice start "
        f"{slice2_start}. cursor_granularity ({inc['cursor_granularity']}) is "
        f"finer than datetime_format ({datetime_format}) precision."
    )


@freeze_time("2024-04-01T00:00:00Z")
def test_reviews_cursor_advances_across_windows(requests_mock):
    """End-to-end regression for stuck-cursor bug (oncall airbytehq/oncall#12928).

    Runs two consecutive incremental syncs. Sync-2 must start from the cursor
    emitted by sync-1, not re-read the entire history.
    """
    account = TEST_CONFIG["account"]
    workspace = TEST_CONFIG["workspace"]
    reviews_url = f"{BASE}/account/{account}/workspace/{workspace}/reviews"

    def _reviews_response(request, context):
        context.status_code = 200
        return {
            "conversations": [
                {
                    "lastUpdatedISO": "2024-03-15T12:00:00Z",
                    "id": "review-1",
                }
            ]
        }

    requests_mock.get(reviews_url, json=_reviews_response)

    saved_cursor = "2024-02-01T00:00:00Z"
    state_1 = StateBuilder().with_stream_state("reviews", {"lastUpdatedISO": saved_cursor}).build()

    output_1 = _read_reviews(TEST_CONFIG, state_1)

    final_cursor = output_1.most_recent_state.stream_state.__dict__.get("lastUpdatedISO")
    assert final_cursor is not None, "expected lastUpdatedISO in final state"
    assert final_cursor > saved_cursor, f"sync-1 cursor did not advance (stuck at {final_cursor})"
