# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Mapping, Optional, Type, Union

import pytest
from airbyte_cdk.sources.declarative.concurrency_level import ConcurrencyLevel


@pytest.mark.parametrize(
    "default_concurrency, max_concurrency, expected_concurrency",
    [
        pytest.param(20, 75, 20, id="test_default_concurrency_as_int"),
        pytest.param(20, 75, 20, id="test_default_concurrency_as_int_ignores_max_concurrency"),
        pytest.param("{{ config['num_workers'] or 40 }}", 75, 50, id="test_default_concurrency_using_interpolation"),
        pytest.param("{{ config['missing'] or 40 }}", 75, 40, id="test_default_concurrency_using_interpolation_no_value"),
        pytest.param("{{ config['num_workers'] or 40 }}", 10, 10, id="test_use_max_concurrency_if_default_is_too_high"),
    ],
)
def test_stream_slices(default_concurrency: Union[int, str], max_concurrency: int, expected_concurrency: int) -> None:
    config = {"num_workers": 50}
    concurrency_level = ConcurrencyLevel(
        default_concurrency=default_concurrency,
        max_concurrency=max_concurrency,
        config=config,
        parameters={}
    )

    actual_concurrency = concurrency_level.get_concurrency_level()

    assert actual_concurrency == expected_concurrency


@pytest.mark.parametrize(
    "config, expected_concurrency, expected_error",
    [
        pytest.param({"num_workers": "fifty five"}, None, ValueError, id="test_invalid_default_concurrency_as_string"),
        pytest.param({"num_workers": "55"}, 55, None, id="test_default_concurrency_as_string_int"),
        pytest.param({"num_workers": 60}, 60, None, id="test_default_concurrency_as_int"),
    ],
)
def test_default_concurrency_input_types_and_errors(
        config: Mapping[str, Any],
        expected_concurrency: Optional[int],
        expected_error: Optional[Type[Exception]],
) -> None:
    concurrency_level = ConcurrencyLevel(
        default_concurrency="{{ config['num_workers'] or 30 }}",
        max_concurrency=65,
        config=config,
        parameters={}
    )

    if expected_error:
        with pytest.raises(expected_error):
            concurrency_level.get_concurrency_level()
    else:
        actual_concurrency = concurrency_level.get_concurrency_level()

        assert actual_concurrency == expected_concurrency


def test_max_concurrency_is_required_for_default_concurrency_using_config() -> None:
    config = {"num_workers": "50"}

    with pytest.raises(ValueError):
        ConcurrencyLevel(
            default_concurrency="{{ config['num_workers'] or 40 }}",
            max_concurrency=None,
            config=config,
            parameters={}
        )
