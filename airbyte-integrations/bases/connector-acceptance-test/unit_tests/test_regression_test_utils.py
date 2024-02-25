#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
import yaml
from connector_acceptance_test.config import Config
from connector_acceptance_test.utils.regression_test import update_config_expected_records_path


@pytest.mark.parametrize(
    "config_before, output_dir, config_after",
    [
        pytest.param(
            """
            connector_image: my-image
            base_path: my-base-path
            acceptance_tests:
              basic_read:
                config_path: my-test-read-config-path
                tests:
                  - config_path: secrets/config.json
                    expect_records:
                      path: integration_tests/expected_records.jsonl
            """,
            "/new_test_dir",
            """
            connector_image: my-image
            base_path: my-base-path
            acceptance_tests:
              basic_read:
                config_path: my-test-read-config-path
                tests:
                  - config_path: secrets/config.json
                    expect_records:
                      path: /new_test_dir/integration_tests/expected_records.jsonl
            """,
            id="update single test path"
        ),
        pytest.param(
            """
            connector_image: my-image
            base_path: my-base-path
            acceptance_tests:
              basic_read:
              config_path: my-test-read-config-path
              tests:
                - config_path: secrets/config1.json
                  expect_records:
                    path: integration_tests/expected_records1.jsonl
                - config_path: secrets/config2.json
                  expect_records:
                    path: integration_tests/expected_records2.jsonl
            """,
            "/new_test_dir",
            """
            connector_image: my-image
            base_path: my-base-path
            acceptance_tests:
              basic_read:
                config_path: my-test-read-config-path
                tests:
                  - config_path: secrets/config1.json
                    expect_records:
                      path: /new_test_dir/integration_tests/expected_records1.jsonl
                  - config_path: secrets/config2.json
                    expect_records:
                      path: /new_test_dir/integration_tests/expected_records2.jsonl
            """,
            id="update multiple test paths",
        ),
        pytest.param(
            """
            connector_image: my-image
            base_path: my-base-path
            acceptance_tests:
              basic_read:
                config_path: my-test-read-config-path
                tests: []
            """,
            "/new_test_dir",
            """
            connector_image: my-image
            base_path: my-base-path
            acceptance_tests:
            basic_read:
              config_path: my-test-read-config-path
              tests: []
            """,
            id="no tests in basic read",
        )
    ],
)
async def test_all_supported_file_types_present(config_before, output_dir, config_after):
    config = Config.parse_obj(yaml.safe_load(config_before))
    update_config_expected_records_path(config, output_dir, "dummy_new_config_path")
    expected_config = Config.parse_obj(yaml.safe_load(config_after))

    # Convert the paths in the config object to strings for comparison
    for test in expected_config.acceptance_tests.basic_read.tests:
        test.expect_records.path = str(test.expect_records.path)

    assert config.dict() == expected_config.dict()
