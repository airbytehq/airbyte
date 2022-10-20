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
        "raw_config, expected_strict_mode, expected_error",
        [
            pytest.param(
                {"connector_image": "foo", "acceptance_tests": {}},
                None,
                does_not_raise(),
                id="No strict_mode declared -> strict_mode is None and no failure.",
            ),
            pytest.param(
                {"connector_image": "foo", "acceptance_tests": {}, "strict_mode": "unknown"},
                config.Config.StrictMode.strict,
                pytest.raises(ValidationError),
                id="An invalid enum is passed -> ValidationError",
            ),
            pytest.param(
                {"connector_image": "foo", "strict_mode": "strict", "acceptance_tests": {}},
                config.Config.StrictMode.strict,
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
    def test_strict_mode(self, mocker, raw_config, expected_strict_mode, expected_error):
        with expected_error:
            parsed_config = config.Config.parse_obj(raw_config)
            assert parsed_config.strict_mode == expected_strict_mode
