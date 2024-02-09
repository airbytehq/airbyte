# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import enum
import time

import anyio
import pytest
from pipelines.helpers.execution import argument_parsing


class SupportedStepIds(enum.Enum):
    STEP1 = "step1"
    STEP2 = "step2"
    STEP3 = "step3"


def test_build_extra_params_mapping(mocker):
    ctx = mocker.Mock()
    argument = mocker.Mock()

    raw_extra_params = (
        "--step1.param1=value1",
        "--step2.param2=value2",
        "--step3.param3=value3",
        "--step1.param4",
    )

    result = argument_parsing.build_extra_params_mapping(SupportedStepIds)(ctx, argument, raw_extra_params)

    expected_result = {
        SupportedStepIds.STEP1.value: {"param1": ["value1"], "param4": []},
        SupportedStepIds.STEP2.value: {"param2": ["value2"]},
        SupportedStepIds.STEP3.value: {"param3": ["value3"]},
    }

    assert result == expected_result
