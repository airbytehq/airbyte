#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import sys
from typing import Dict, List, Set, Union

import yaml
from connector_ops import utils

BACKWARD_COMPATIBILITY_REVIEWERS = {"connector-operations", "connector-extensibility"}
TEST_STRICTNESS_LEVEL_REVIEWERS = {"connector-operations"}
GA_BYPASS_REASON_REVIEWERS = {"connector-operations"}
GA_CONNECTOR_REVIEWERS = {"gl-python"}
BREAKING_CHANGE_REVIEWERS = {"breaking-change-reviewers"}
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
        check_for_high_strictness = connector.acceptance_test_config is not None and connector.requires_high_test_strictness_level
        if check_for_high_strictness:
            try:
                assert connector.acceptance_test_config.get("test_strictness_level") == "high"
            except AssertionError:
                connectors_with_bad_strictness_level.append(connector)
    return connectors_with_bad_strictness_level


def find_changed_important_connectors() -> Set[utils.Connector]:
    """Find important connectors modified on the current branch.

    Returns:
        Set[utils.Connector]: The set of GA connectors that were modified on the current branch.
    """
    changed_connectors = utils.get_changed_connectors(destination=False, third_party=False)
    return {connector for connector in changed_connectors if connector.is_important_connector}


def get_bypass_reason_changes() -> Set[utils.Connector]:
    """Find connectors that have modified bypass_reasons.

    Returns:
        Set[str]: Set of connector names e.g {"source-github"}: The set of GA connectors that have changed bypass_reasons.
    """
    bypass_reason_changes = utils.get_changed_acceptance_test_config(diff_regex="bypass_reason")
    return bypass_reason_changes.intersection(find_changed_important_connectors())


def find_mandatory_reviewers() -> List[Union[str, Dict[str, List]]]:
    important_connector_changes = find_changed_important_connectors()
    backward_compatibility_changes = utils.get_changed_acceptance_test_config(diff_regex="disable_for_version")
    test_strictness_level_changes = utils.get_changed_acceptance_test_config(diff_regex="test_strictness_level")
    ga_bypass_reason_changes = get_bypass_reason_changes()
    breaking_change_changes = utils.get_changed_metadata(diff_regex="breakingChanges")

    required_reviewers = []

    if backward_compatibility_changes:
        required_reviewers.append({"any-of": list(BACKWARD_COMPATIBILITY_REVIEWERS)})
    if test_strictness_level_changes:
        required_reviewers.append({"any-of": list(TEST_STRICTNESS_LEVEL_REVIEWERS)})
    if ga_bypass_reason_changes:
        required_reviewers.append({"any-of": list(GA_BYPASS_REASON_REVIEWERS)})
    if important_connector_changes:
        required_reviewers.append({"any-of": list(GA_CONNECTOR_REVIEWERS)})
    if breaking_change_changes:
        required_reviewers.append({"any-of": list(BREAKING_CHANGE_REVIEWERS)})

    return required_reviewers


def check_test_strictness_level():
    connectors_with_bad_strictness_level = find_connectors_with_bad_strictness_level()
    if connectors_with_bad_strictness_level:
        logging.error(
            f"The following connectors must enable high test strictness level: {connectors_with_bad_strictness_level}. Please check this documentation for details: https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference/#strictness-level"
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
