#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_rki_covid.source import GermanyStates


@pytest.fixture
def patch_germany_states_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(GermanyStates, "primary_key", None)


def test_path(patch_germany_states_class):
    stream = GermanyStates()
    expected_params = {"path": "states/"}
    assert stream.path() == expected_params.get("path")
