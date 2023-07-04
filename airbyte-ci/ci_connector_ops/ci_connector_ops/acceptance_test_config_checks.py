#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import sys
from typing import List, Dict, Union, Set
import yaml

from ci_connector_ops import utils

RELEASE_STAGE_TO_STRICTNESS_LEVEL_MAPPING = {"generally_available": "high"}
BACKWARD_COMPATIBILITY_REVIEWERS = {"connector-operations", "connector-extensibility"}
TEST_STRICTNESS_LEVEL_REVIEWERS = {"connector-operations"}
GA_BYPASS_REASON_REVIEWERS = {"connector-operations"}
GA_CONNECTOR_REVIEWERS = {"gl-python"}
REVIEW_REQUIREMENTS_FILE_PATH = ".github/connector_org_review_requirements.yaml"


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


def find_changed_ga_connectors() -> Set[utils.Connector]:
    """Find GA connectors modified on the current branch.

    Returns:
        Set[utils.Connector]: The set of GA connectors that were modified on the current branch.
    """
    changed_connectors = utils.get_changed_connectors(destination=False, third_party=False)
    return {connector for connector in changed_connectors if connector.release_stage == "generally_available"}


def get_ga_bypass_reason_changes() -> Set[utils.Connector]:
    """Find GA connectors that have modified bypass_reasons.

    Returns:
        Set[str]: Set of connector names e.g {"source-github"}: The set of GA connectors that have changed bypass_reasons.
    """
    bypass_reason_changes = utils.get_changed_acceptance_test_config(diff_regex="bypass_reason")
    return bypass_reason_changes.intersection(find_changed_ga_connectors())


def find_mandatory_reviewers() -> List[Union[str, Dict[str, List]]]:
    ga_connector_changes = find_changed_ga_connectors()
    backward_compatibility_changes = utils.get_changed_acceptance_test_config(diff_regex="disable_for_version")
    test_strictness_level_changes = utils.get_changed_acceptance_test_config(diff_regex="test_strictness_level")
    ga_bypass_reason_changes = get_ga_bypass_reason_changes()

    if backward_compatibility_changes:
        return [{"any-of": list(BACKWARD_COMPATIBILITY_REVIEWERS)}]
    if test_strictness_level_changes:
        return [{"any-of": list(TEST_STRICTNESS_LEVEL_REVIEWERS)}]
    if ga_bypass_reason_changes:
        return [{"any-of": list(GA_BYPASS_REASON_REVIEWERS)}]
    if ga_connector_changes:
        return list(GA_CONNECTOR_REVIEWERS)
    return []


def check_test_strictness_level():
    connectors_with_bad_strictness_level = find_connectors_with_bad_strictness_level()
    if connectors_with_bad_strictness_level:
        logging.error(
            f"The following GA connectors must enable high test strictness level: {connectors_with_bad_strictness_level}. Please check this documentation for details: https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference/#strictness-level"
        )
        sys.exit(1)
    else:
        sys.exit(0)


def write_review_requirements_file():
    mandatory_reviewers = find_mandatory_reviewers()

    if mandatory_reviewers:
        requirements_file_content = [
            {"name": "Required reviewers from the connector org teams", "paths": "unmatched", "teams": mandatory_reviewers}
        ]
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
