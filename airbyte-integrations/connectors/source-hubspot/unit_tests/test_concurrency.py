#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest

from .conftest import get_source


@pytest.mark.parametrize(
    "config, expected_concurrency",
    [
        pytest.param({"num_worker": 25}, 25, id="configured_num_worker"),
        pytest.param({}, 10, id="default_num_worker"),
    ],
)
def test_concurrency_level_uses_num_worker(config, expected_concurrency):
    source = get_source(config)

    assert source._concurrent_source._threadpool._threadpool._max_workers == expected_concurrency
