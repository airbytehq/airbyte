#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
from source_faker import SourceFaker

from airbyte_cdk.models import Status


@pytest.mark.parametrize(
    "config",
    [
        {},
        {"sourceType": "faker", "count": 5000, "seed": 42},
        {"count": 5000, "seed": 42, "records_per_slice": 1000},
        {"count": 5000, "seed": 42, "parallelism": 4},
        {"records_per_slice": 1000, "parallelism": 4},
        {"count": 1, "records_per_slice": 1, "parallelism": 1},
    ],
)
def test_check_accepts_omitted_numeric_settings(config: dict) -> None:
    result = SourceFaker().check(logging.getLogger(__name__), config)

    assert result.status == Status.SUCCEEDED, result.message
    assert result.message is None


@pytest.mark.parametrize("setting", ["count", "records_per_slice", "parallelism"])
@pytest.mark.parametrize("value", [0, -1, True, False, "1", None])
def test_check_rejects_explicit_invalid_numeric_settings(setting: str, value: object) -> None:
    result = SourceFaker().check(logging.getLogger(__name__), {setting: value})

    assert result.status == Status.FAILED
    assert result.message == repr(f"`{setting}` must be a number greater than or equal to 1, got {value!r}")
