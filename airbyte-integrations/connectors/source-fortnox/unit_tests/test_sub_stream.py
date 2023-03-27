
from airbyte_cdk.models import SyncMode
from unittest.mock import MagicMock

import pytest
from source_fortnox.source import FortnoxSubstream


@pytest.fixture
def patch_substream_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(FortnoxSubstream, "__abstractmethods__", set())


def test_slices(patch_substream_base_class):
    substream = FortnoxSubstream(parent=MagicMock(
        stream_slices=lambda **kwargs: [None],
        read_records = lambda **kwargs: (yield from [{'a': 1},{'b': 2},{'c': 3}]),
        )
    )
    expected = [
        {"parent": {"@is_first": True, "@is_last": False, "a": 1}},
        {"parent": {"@is_first": False, "@is_last": False, "b": 2}},
        {"parent": {"@is_first": False, "@is_last": True, "c": 3}},
    ]
    assert list(substream.stream_slices(sync_mode=SyncMode.incremental)) == expected

def test_slices_empty(patch_substream_base_class):
    substream = FortnoxSubstream(parent=MagicMock(
        stream_slices=lambda **kwargs: [None],
        read_records = lambda **kwargs: (yield from []),
    )
    )
    expected = [
    ]
    assert list(substream.stream_slices(sync_mode=SyncMode.incremental)) == expected
