from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_kapiche_export_api.source import (
    IncrementalKapicheExportApiStream,
    ExportDataGet,
)


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(
        IncrementalKapicheExportApiStream, "path", "v0/example_endpoint"
    )
    mocker.patch.object(
        IncrementalKapicheExportApiStream, "primary_key", "test_primary_key"
    )
    mocker.patch.object(IncrementalKapicheExportApiStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = ExportDataGet("uuid", None)
    expected_cursor_field = "document_id__"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = IncrementalKapicheExportApiStream()
    inputs = {"current_stream_state": None, "latest_record": None}
    expected_state = {}
    assert stream.get_updated_state(**inputs) == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = IncrementalKapicheExportApiStream()
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {}}
    expected_stream_slice = [None]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(ExportDataGet, "cursor_field", "dummy_field")
    stream = ExportDataGet("uuid", None)
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = IncrementalKapicheExportApiStream()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = IncrementalKapicheExportApiStream()
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
