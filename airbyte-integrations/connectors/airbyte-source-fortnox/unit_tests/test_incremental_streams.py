from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_fortnox.source import IncrementalFortnoxStream, VoucherDetails


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalFortnoxStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalFortnoxStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalFortnoxStream, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    assert IncrementalFortnoxStream(authenticator=None).cursor_field == "lastmodified"


def test_voucher_details_state(patch_incremental_base_class):
    date = "2019-04-13"
    stream = VoucherDetails(authenticator=None)
    stream.state = date
    assert stream.state == date


def test_stream_slices(patch_incremental_base_class):
    assert IncrementalFortnoxStream(authenticator=None).stream_slices(sync_mode=SyncMode.incremental) == [None]


def test_supports_incremental(patch_incremental_base_class):
    assert IncrementalFortnoxStream(authenticator=None).supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    assert IncrementalFortnoxStream(authenticator=None).source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    assert IncrementalFortnoxStream(authenticator=None).state_checkpoint_interval is None
