#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_acceptance_test import conftest
from source_acceptance_test.config import BasicReadTestConfig, Config, EmptyStreamConfiguration


@pytest.mark.parametrize(
    "test_strictness_level, basic_read_test_config, expect_test_failure",
    [
        pytest.param(
            Config.TestStrictnessLevel.low,
            BasicReadTestConfig(config_path="config_path", empty_streams={EmptyStreamConfiguration(name="my_empty_stream")}),
            False,
            id="[LOW test strictness level] Empty streams can be declared without bypass_reason.",
        ),
        pytest.param(
            Config.TestStrictnessLevel.low,
            BasicReadTestConfig(
                config_path="config_path", empty_streams={EmptyStreamConfiguration(name="my_empty_stream", bypass_reason="good reason")}
            ),
            False,
            id="[LOW test strictness level] Empty streams can be declared with a bypass_reason.",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            BasicReadTestConfig(config_path="config_path", empty_streams={EmptyStreamConfiguration(name="my_empty_stream")}),
            True,
            id="[HIGH test strictness level] Empty streams can't be declared without bypass_reason.",
        ),
        pytest.param(
            Config.TestStrictnessLevel.high,
            BasicReadTestConfig(
                config_path="config_path", empty_streams={EmptyStreamConfiguration(name="my_empty_stream", bypass_reason="good reason")}
            ),
            False,
            id="[HIGH test strictness level] Empty streams can be declared with a bypass_reason.",
        ),
    ],
)
def test_empty_streams_fixture(mocker, test_strictness_level, basic_read_test_config, expect_test_failure):
    mocker.patch.object(conftest.pytest, "fail")
    # Pytest prevents fixture to be directly called. Using __wrapped__ allows us to call the actual function before it's been wrapped by the decorator.
    assert conftest.empty_streams_fixture.__wrapped__(basic_read_test_config, test_strictness_level) == basic_read_test_config.empty_streams
    if expect_test_failure:
        conftest.pytest.fail.assert_called_once()
    else:
        conftest.pytest.fail.assert_not_called()


# @pytest.mark.parametrize()
# def test_expected_records_by_stream_fixture(mocker, test_strictness_level, configured_ctalog, empty_streams, inputs, base_path):
#     mocker.patch.object(conftest.pytest, "fail")
