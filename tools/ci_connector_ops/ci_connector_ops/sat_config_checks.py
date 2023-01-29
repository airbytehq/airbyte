#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import sys
from typing import List, Dict, Union
import yaml

from ci_connector_ops import utils

RELEASE_STAGE_TO_STRICTNESS_LEVEL_MAPPING = {"generally_available": "high"}
BACKWARD_COMPATIBILITY_REVIEWERS = {"connector-operations", "connector-extensibility"}
TEST_STRICTNESS_LEVEL_REVIEWERS = {"connector-operations"}
GA_CONNECTOR_REVIEWERS = {"gl-python"}
REVIEW_REQUIREMENTS_FILE_PATH = ".github/connector_org_review_requirements.yaml"

def find_connectors_with_bad_strictness_level() -> List[utils.Connector]:
    """Check if changed connectors have the expected SAT test strictness level according to their release stage.
    1. Identify changed connectors
    2. Retrieve their release stage from the catalog
    3. Parse their acceptance test config file
    4. Check if the test strictness level matches the strictness level expected for their release stage.

    Returns:
        List[utils.Connector]: List of changed connector that are not matching test strictness level expectations.
    """
    connectors_with_bad_strictness_level = []
    changed_connector = utils.get_changed_connectors()
    for connector in changed_connector:
        expected_test_strictness_level = RELEASE_STAGE_TO_STRICTNESS_LEVEL_MAPPING.get(connector.release_stage)
        can_check_strictness_level = all(
            [item is not None for item in [connector.release_stage, expected_test_strictness_level, connector.acceptance_test_config]]
        )
        if can_check_strictness_level:
            try:
                assert connector.acceptance_test_config.get("test_strictness_level") == expected_test_strictness_level
            except AssertionError:
                connectors_with_bad_strictness_level.append(connector)
    return connectors_with_bad_strictness_level

def find_changed_ga_connectors() -> List[utils.Connector]:
    """Find GA connectors modified on the current branch.

    Returns:
        List[utils.Connector]: The list of GA connectors that were modified on the current branch.
    """
    changed_connectors = utils.get_changed_connectors()
    return [connector for connector in changed_connectors if connector.release_stage == "generally_available"]

def find_mandatory_reviewers() -> List[Union[str, Dict[str, List]]]:
    ga_connector_changes = find_changed_ga_connectors()
    backward_compatibility_changes = utils.get_changed_acceptance_test_config(diff_regex="disable_for_version")
    test_strictness_level_changes = utils.get_changed_acceptance_test_config(diff_regex="test_strictness_level")
    if backward_compatibility_changes:
        return [{"any-of": list(BACKWARD_COMPATIBILITY_REVIEWERS)}]
    if test_strictness_level_changes:
        return [{"any-of": list(TEST_STRICTNESS_LEVEL_REVIEWERS)}]
    if ga_connector_changes:
        return list(GA_CONNECTOR_REVIEWERS)
    return []

def check_test_strictness_level():
    connectors_with_bad_strictness_level = find_connectors_with_bad_strictness_level()
    if connectors_with_bad_strictness_level:
        logging.error(
            f"The following GA connectors must enable high test strictness level: {connectors_with_bad_strictness_level}. Please check this documentation for details: https://docs.airbyte.com/connector-development/testing-connectors/source-acceptance-tests-reference/#strictness-level"
        )
        sys.exit(1)
    else:
        sys.exit(0)

def write_review_requirements_file():
    mandatory_reviewers = find_mandatory_reviewers()

    if mandatory_reviewers:
        requirements_file_content = [{
            "name": "Required reviewers from the connector org teams",
            "paths": "unmatched",
            "teams": mandatory_reviewers
        }]
        with open(REVIEW_REQUIREMENTS_FILE_PATH, "w") as requirements_file:
            yaml.safe_dump(requirements_file_content, requirements_file)
        print("CREATED_REQUIREMENTS_FILE=true")
    else:
        print("CREATED_REQUIREMENTS_FILE=false")

def print_mandatory_reviewers():
    teams = []
    mandatory_reviewers = find_mandatory_reviewers()
    for mandatory_reviewer in mandatory_reviewers:
        if isinstance(mandatory_reviewer, dict):
            teams += mandatory_reviewer["any-of"]
        else:
            teams.append(mandatory_reviewer)
    print(f"MANDATORY_REVIEWERS=A review is required from these teams: {','.join(teams)}")
