import logging

import pytest
from source_faker import SourceFaker

from airbyte_cdk.models import Status, SyncMode


@pytest.mark.parametrize("config", [{"count": 5000, "seed": 42}, {}])
def test_check_with_optional_settings_omitted(config):
    source = SourceFaker()
    assert source.check(logging.getLogger(__name__), config).status == Status.SUCCEEDED


@pytest.mark.parametrize("config", [{"count": 5000, "seed": 42}, {}])
def test_streams_preserve_existing_defaults(config):
    source = SourceFaker()
    defaults = {"count": 1000, "seed": None, "records_per_slice": 100, "always_updated": True, "parallelism": 4}
    original = dict(config)
    streams = source.streams(config)
    assert len(streams) == 3
    for stream in streams:
        for key, default in defaults.items():
            if key == "parallelism" and stream.name == "products":
                continue
            assert getattr(stream, key) == config.get(key, default)
    assert config == original


@pytest.mark.parametrize("key", ["count", "records_per_slice", "parallelism"])
@pytest.mark.parametrize("value", [0, -1, None, False, "invalid"])
def test_check_rejects_explicit_invalid_settings(key, value):
    ok, error = SourceFaker().check_connection(logging.getLogger(__name__), {key: value})
    assert not ok
    assert f"`{key}`" in error


def test_read_products_with_optional_settings_omitted():
    stream = SourceFaker().streams({"count": 3})[0]
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh))
    assert [record["id"] for record in records if isinstance(record, dict)] == [1, 2, 3]
