#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_rki_covid.source import GermanyStatesAgeGroups


@pytest.fixture
def patch_states_age_group(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(GermanyStatesAgeGroups, "primary_key", None)


def test_path(patch_states_age_group):
    stream = GermanyStatesAgeGroups()
    expected_params = {"path": "states/age-groups"}
    assert stream.path() == expected_params.get("path")
