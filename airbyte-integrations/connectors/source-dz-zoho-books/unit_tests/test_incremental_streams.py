#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from pytest import fixture


@fixture
def patch_incremental_base_class(mocker):
    assert True


def test_cursor_field(patch_incremental_base_class):
    assert True


def test_get_updated_state(patch_incremental_base_class):
    assert True


def test_stream_slices(patch_incremental_base_class):
    assert True


def test_supports_incremental(patch_incremental_base_class, mocker):
    assert True


def test_source_defined_cursor(patch_incremental_base_class):
    assert True


def test_stream_checkpoint_interval(patch_incremental_base_class):
    assert True
