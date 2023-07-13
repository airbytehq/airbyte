#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture(autouse=True)
def disable_cache(mocker):
    mocker.patch(
        "source_github.streams.Repositories.use_cache",
        new_callable=mocker.PropertyMock,
        return_value=False
    )
