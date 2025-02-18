#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


# from airbyte_cdk.models import SyncMode
# from pytest import fixture, mark,py
import pytest


# from source_box_data_extract.source import IncrementalBoxFileTextStream

# We do not support incremental streams yet
# skip this test


@pytest.mark.skip(reason="This connector does not support incremental streams yet")
def test_incremental_stream():
    assert True

