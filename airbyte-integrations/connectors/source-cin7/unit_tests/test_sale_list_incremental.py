from datetime import datetime
from pathlib import Path

import yaml
from airbyte_cdk.legacy.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource


def _manifest() -> dict:
    return yaml.safe_load((Path(__file__).parent.parent / "manifest.yaml").read_text())


def _sale_list_stream(config: dict):
    source = ManifestDeclarativeSource(_manifest(), config=config)
    return next(stream for stream in source.streams(config) if stream.name == "sale_list")


def test_sale_list_incremental_manifest_uses_one_open_ended_slice():
    manifest = _manifest()
    stream = manifest["definitions"]["streams"]["sale_list"]
    incremental_sync = stream["incremental_sync"]

    assert incremental_sync["cursor_field"] == "Updated"
    assert incremental_sync["cursor_datetime_formats"] == [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    assert incremental_sync["start_time_option"]["field_name"] == "UpdatedSince"
    assert "end_datetime" not in incremental_sync
    assert "end_time_option" not in incremental_sync
    assert "step" not in incremental_sync
    assert "cursor_granularity" not in incremental_sync

    stream_instance = _sale_list_stream({"accountid": "account", "api_key": "key"})
    slices = list(stream_instance.cursor.stream_slices())
    assert len(slices) == 1


def test_sale_list_incremental_parses_both_timestamp_precisions():
    formats = _manifest()["definitions"]["streams"]["sale_list"]["incremental_sync"]["cursor_datetime_formats"]

    for value in ("2017-09-29T03:03:13.913Z", "2021-11-11T13:27:28.16Z"):
        assert any(datetime.strptime(value, format_) for format_ in formats)


def test_sales_parent_stream_reference_remains_unchanged():
    manifest = _manifest()
    sales = manifest["definitions"]["streams"]["sales"]
    parent = sales["retriever"]["partition_router"]["parent_stream_configs"][0]["stream"]

    assert parent == {"$ref": "#/definitions/streams/sale_list"}
    assert "incremental_dependency" not in sales
