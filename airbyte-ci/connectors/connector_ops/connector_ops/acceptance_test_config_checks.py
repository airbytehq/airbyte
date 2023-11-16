#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import sys
from typing import List

from connector_ops import utils


def find_connectors_with_bad_strictness_level() -> List[utils.Connector]:
    """Check if changed connectors have the expected connector acceptance test strictness level according to their release stage.
    1. Identify changed connectors
    2. Retrieve their release stage from the catalog
    3. Parse their acceptance test config file
    4. Check if the test strictness level matches the strictness level expected for their release stage.

    Returns:
        List[utils.Connector]: List of changed connector that are not matching test strictness level expectations.
    """
    connectors_with_bad_strictness_level = []
    changed_connector = utils.get_changed_connectors(destination=False, third_party=False)
    for connector in changed_connector:
        check_for_high_strictness = connector.acceptance_test_config is not None and connector.requires_high_test_strictness_level
        if check_for_high_strictness:
            try:
                assert connector.acceptance_test_config.get("test_strictness_level") == "high"
            except AssertionError:
                connectors_with_bad_strictness_level.append(connector)
    return connectors_with_bad_strictness_level


def check_test_strictness_level():
    connectors_with_bad_strictness_level = find_connectors_with_bad_strictness_level()
    if connectors_with_bad_strictness_level:
        logging.error(
            f"The following connectors must enable high test strictness level: {connectors_with_bad_strictness_level}. Please check this documentation for details: https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference/#strictness-level"
        )
        sys.exit(1)
    else:
        sys.exit(0)
