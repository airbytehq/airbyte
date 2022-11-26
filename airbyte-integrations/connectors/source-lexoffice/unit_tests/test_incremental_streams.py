#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.models import SyncMode
from pytest import fixture
from source_lexware.source import VoucherList


@fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(VoucherList, "path", "voucherlist")
    mocker.patch.object(VoucherList, "primary_key", "id")
    mocker.patch.object(VoucherList, "__abstractmethods__", set())


def test_cursor_field(patch_incremental_base_class):
    stream = VoucherList()
    # TODO: replace this with your expected cursor field
    expected_cursor_field = "updatedDate"
    assert stream.cursor_field == expected_cursor_field


def test_get_updated_state(patch_incremental_base_class):
    stream = VoucherList()
    expected_state = {'updatedDate': '1990-01-01'}
    assert stream.state == expected_state


def test_stream_slices(patch_incremental_base_class):
    stream = VoucherList()
    # TODO: replace this with your input parameters
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": {"updatedDate": "2022-05-30"}}
    # TODO: replace this with your expected stream slices list
    expected_stream_slice = [{"updatedDate": "2022-05-30"}]
    assert stream.stream_slices(**inputs) == expected_stream_slice


def test_supports_incremental(patch_incremental_base_class, mocker):
    mocker.patch.object(VoucherList, "cursor_field", "dummy_field")
    stream = VoucherList()
    assert stream.supports_incremental


def test_source_defined_cursor(patch_incremental_base_class):
    stream = VoucherList()
    assert stream.source_defined_cursor


def test_stream_checkpoint_interval(patch_incremental_base_class):
    stream = VoucherList()
    # TODO: replace this with your expected checkpoint interval
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval
