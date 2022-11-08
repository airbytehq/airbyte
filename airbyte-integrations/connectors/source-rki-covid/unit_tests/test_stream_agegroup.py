#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_rki_covid.source import GermanyAgeGroups


@pytest.fixture
def patch_age_group(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(GermanyAgeGroups, "primary_key", None)


def test_path(patch_age_group):
    stream = GermanyAgeGroups()
    expected_params = {"path": "germany/age-groups"}
    assert stream.path() == expected_params.get("path")
