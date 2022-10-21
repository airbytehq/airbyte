#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from pydantic import ValidationError, root_validator
from source_acceptance_test import config

from .conftest import does_not_raise


@root_validator
def dumb_validator(cls, x):
    return x


class TestConfig:
    @pytest.mark.parametrize(
        "raw_config, expected_test_mode, expected_error",
        [
            pytest.param({"connector_image": "foo", "tests": {}}, None, does_not_raise(), id="No test_mode declared defaults to None."),
            pytest.param(
                {"connector_image": "foo", "tests": {}, "test_mode": "strict"},
                config.Config.TestMode.strict,
                does_not_raise(),
                id="The test_mode set to strict is a valid enum value is provided.",
            ),
            pytest.param(
                {"connector_image": "foo", "tests": {}, "test_mode": "medium"},
                config.Config.TestMode.medium,
                does_not_raise(),
                id="The test_mode set to strict is a valid enum value is provided.",
            ),
            pytest.param(
                {"connector_image": "foo", "tests": {}, "test_mode": "light"},
                config.Config.TestMode.light,
                does_not_raise(),
                id="The test_mode set to strict is a valid enum value is provided.",
            ),
            pytest.param(
                {"connector_image": "foo", "tests": {}, "test_mode": "unknown"},
                None,
                pytest.raises(ValidationError),
                id="The strict_mode set to strict, acceptance tests are not declared -> ValidationError",
            ),
            pytest.param(
                {
                    "connector_image": "foo",
                    "strict_mode": "strict",
                    "acceptance_tests": {
                        "connection": {"bypass_reason": "No good reason"},
                        "spec": {"bypass_reason": "No good reason"},
                        "basic_read": {"bypass_reason": "No good reason"},
                        "full_refresh": {"bypass_reason": "No good reason"},
                        "incremental": {"bypass_reason": "No good reason"},
                        "discovery": {"bypass_reason": "No good reason"},
                    },
                },
                config.Config.StrictMode.strict,
                does_not_raise(),
                id="The strict_mode set to strict, all acceptance tests have a bypass reason -> No failure",
            ),
        ],
    )
    def test_test_mode(self, raw_config, expected_test_mode, expected_error):
        with expected_error:
            parsed_config = config.Config.parse_obj(raw_config)
            assert parsed_config.test_mode == expected_test_mode
