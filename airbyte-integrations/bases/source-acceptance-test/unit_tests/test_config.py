#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import pytest
from pydantic import ValidationError
from source_acceptance_test import config

from .conftest import does_not_raise


class TestConfig:
    @pytest.mark.parametrize(
        "raw_config, expected_strict_mode, expected_error",
        [
            pytest.param({"connector_image": "foo", "tests": {}}, None, does_not_raise(), id="No strict_mode declared defaults to None."),
            pytest.param(
                {"connector_image": "foo", "tests": {}, "strict_mode": "strict"},
                config.Config.StrictMode.strict,
                does_not_raise(),
                id="The strict_mode set to strict is a valid enum value is provided.",
            ),
            pytest.param(
                {"connector_image": "foo", "tests": {}, "strict_mode": "unknown"},
                config.Config.StrictMode.strict,
                pytest.raises(ValidationError),
                id="Validation error is raised when an invalid enum is passed.",
            ),
        ],
    )
    def test_strict_mode(self, raw_config, expected_strict_mode, expected_error):
        with expected_error:
            parsed_config = config.Config.parse_obj(raw_config)
            assert parsed_config.strict_mode == expected_strict_mode
