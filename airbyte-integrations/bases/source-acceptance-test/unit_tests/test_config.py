#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from pydantic import ValidationError
from source_acceptance_test import config

from .conftest import does_not_raise


class TestConfig:
    @pytest.mark.parametrize(
        "raw_config, expected_output_config, expected_error",
        [
            pytest.param(
                {"connector_image": "foo", "tests": {"spec": [{"spec_path": "my-spec-path"}]}},
                config.Config(
                    connector_image="foo",
                    acceptance_tests=config.AcceptanceTestConfigurations(
                        spec=config.GenericTestConfig(tests=[config.SpecTestConfig(spec_path="my-spec-path")])
                    ),
                ),
                does_not_raise(),
                id="Legacy config should be parsed without error.",
            ),
            pytest.param(
                {"connector_image": "foo", "acceptance_tests": {}, "test_strictness_level": "extra-low"},
                None,
                pytest.raises(ValidationError),
                id="Invalid test mode: ValidationError",
            ),
            pytest.param(
                {"connector_image": "foo", "acceptance_tests": {}, "test_strictness_level": "low"},
                config.Config(
                    connector_image="foo",
                    test_strictness_level=config.Config.TestStrictnessLevel.low,
                    acceptance_tests=config.AcceptanceTestConfigurations(),
                ),
                does_not_raise(),
                id="Valid test mode: low",
            ),
            pytest.param(
                {"connector_image": "foo", "acceptance_tests": {}, "test_strictness_level": "high"},
                config.Config(
                    connector_image="foo",
                    test_strictness_level=config.Config.TestStrictnessLevel.high,
                    acceptance_tests=config.AcceptanceTestConfigurations(),
                ),
                does_not_raise(),
                id="Valid test mode: high",
            ),
            pytest.param(
                {
                    "connector_image": "foo",
                    "acceptance_tests": {
                        "spec": {"bypass_reason": "My good reason to bypass"},
                    },
                },
                config.Config(
                    connector_image="foo",
                    acceptance_tests=config.AcceptanceTestConfigurations(
                        spec=config.GenericTestConfig(bypass_reason="My good reason to bypass")
                    ),
                ),
                does_not_raise(),
                id="A test can only have a bypass reason.",
            ),
            pytest.param(
                {
                    "connector_image": "foo",
                    "acceptance_tests": {
                        "spec": {"bypass_reason": "My good reason to bypass"},
                    },
                },
                config.Config(
                    connector_image="foo",
                    acceptance_tests=config.AcceptanceTestConfigurations(
                        spec=config.GenericTestConfig(bypass_reason="My good reason to bypass")
                    ),
                ),
                does_not_raise(),
                id="A test can only have a test configuration.",
            ),
            pytest.param(
                {
                    "connector_image": "foo",
                    "acceptance_tests": {
                        "spec": {"tests": [{"spec_path": "my-spec-path"}], "bypass_reason": "I'm not bypassing"},
                    },
                },
                None,
                pytest.raises(ValidationError),
                id="A test can't have a bypass reason and a test configuration.",
            ),
        ],
    )
    def test_config_parsing(self, raw_config, expected_output_config, expected_error):
        with expected_error:
            parsed_config = config.Config.parse_obj(raw_config)
            assert parsed_config == expected_output_config
