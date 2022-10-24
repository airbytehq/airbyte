#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from pydantic import ValidationError
from source_acceptance_test import config

from .conftest import does_not_raise


class TestConfig:
    @pytest.mark.parametrize(
        "raw_config, expected_test_strictness_level, expected_error",
        [
            pytest.param(
                {"connector_image": "foo", "tests": {}}, None, does_not_raise(), id="No test_strictness_level declared defaults to None."
            ),
            pytest.param(
                {"connector_image": "foo", "tests": {}, "test_strictness_level": "high"},
                config.Config.TestStrictnessLevel.high,
                does_not_raise(),
                id="The test_strictness_level set to strict is a valid enum value is provided.",
            ),
            pytest.param(
                {"connector_image": "foo", "tests": {}, "test_strictness_level": "unknown"},
                None,
                pytest.raises(ValidationError),
                id="Validation error is raised when an invalid enum is passed.",
            ),
        ],
    )
    def test_test_strictness_level(self, raw_config, expected_test_strictness_level, expected_error):
        with expected_error:
            parsed_config = config.Config.parse_obj(raw_config)
            assert parsed_config.test_strictness_level == expected_test_strictness_level
