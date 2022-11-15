#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import sys
from typing import List

from ci_connector_ops import utils

RELEASE_STAGE_TO_STRICTNESS_LEVEL_MAPPING = {"generally_available": "high"}


def find_connectors_with_bad_strictness_level() -> List[str]:
    """Check if changed connectors have the expected SAT test strictness level according to their release stage.
    1. Identify changed connectors
    2. Retrieve their release stage from the catalog
    3. Parse their acceptance test config file
    4. Check if the test strictness level matches the strictness level expected for their release stage.

    Returns:
        List[str]: List of changed connector names that are not matching test strictness level expectations.
    """
    connectors_with_bad_strictness_level = []
    changed_connector_names = utils.get_changed_connector_names()
    for connector_name in changed_connector_names:
        connector_release_stage = utils.get_connector_release_stage(connector_name)
        expected_test_strictness_level = RELEASE_STAGE_TO_STRICTNESS_LEVEL_MAPPING.get(connector_release_stage)
        _, acceptance_test_config = utils.get_acceptance_test_config(connector_name)
        can_check_strictness_level = all(
            [item is not None for item in [connector_release_stage, expected_test_strictness_level, acceptance_test_config]]
        )
        if can_check_strictness_level:
            try:
                assert acceptance_test_config.get("test_strictness_level") == expected_test_strictness_level
            except AssertionError:
                connectors_with_bad_strictness_level.append(connector_name)
    return connectors_with_bad_strictness_level


def main():
    connectors_with_bad_strictness_level = find_connectors_with_bad_strictness_level()
    if connectors_with_bad_strictness_level:
        logging.error(
            f"The following GA connectors must enable high test strictness level: {connectors_with_bad_strictness_level}. Please check this documentation for details: https://docs.airbyte.com/connector-development/testing-connectors/source-acceptance-tests-reference/#strictness-level"
        )
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
