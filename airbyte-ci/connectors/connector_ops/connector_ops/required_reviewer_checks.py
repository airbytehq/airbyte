#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Dict, List, Set, Union

import yaml
from connector_ops import utils

BACKWARD_COMPATIBILITY_REVIEWERS = {"connector-operations", "connector-extensibility"}
TEST_STRICTNESS_LEVEL_REVIEWERS = {"connector-operations"}
GA_BYPASS_REASON_REVIEWERS = {"connector-operations"}
GA_CONNECTOR_REVIEWERS = {"gl-python"}
BREAKING_CHANGE_REVIEWERS = {"breaking-change-reviewers"}
REVIEW_REQUIREMENTS_FILE_PATH = ".github/connector_org_review_requirements.yaml"


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


def find_mandatory_reviewers() -> List[Dict[str, Union[str, Dict[str, List]]]]:
    important_connector_changes = find_changed_important_connectors()
    backward_compatibility_changes = utils.get_changed_acceptance_test_config(diff_regex="disable_for_version")
    test_strictness_level_changes = utils.get_changed_acceptance_test_config(diff_regex="test_strictness_level")
    ga_bypass_reason_changes = get_bypass_reason_changes()
    breaking_change_changes = utils.get_changed_metadata(diff_regex="upgradeDeadline")

    required_reviewers = []

    if backward_compatibility_changes:
        required_reviewers.append({"name": "Backwards Compatibility Test Skip", "teams": list(BACKWARD_COMPATIBILITY_REVIEWERS)})
    if test_strictness_level_changes:
        required_reviewers.append({"name": "Acceptance Test Strictness Level", "teams": list(TEST_STRICTNESS_LEVEL_REVIEWERS)})
    if ga_bypass_reason_changes:
        required_reviewers.append({"name": "GA Acceptance Test Bypass", "teams": list(GA_BYPASS_REASON_REVIEWERS)})
    if important_connector_changes:
        required_reviewers.append({"name": "GA Connectors", "teams": list(GA_CONNECTOR_REVIEWERS)})
    if breaking_change_changes:
        required_reviewers.append({"name": "Breaking Changes", "teams": list(BREAKING_CHANGE_REVIEWERS)})

    return required_reviewers


def write_review_requirements_file():
    mandatory_reviewers = find_mandatory_reviewers()

    if mandatory_reviewers:
        requirements_file_content = [dict(r, paths="unmatched") for r in mandatory_reviewers]
        with open(REVIEW_REQUIREMENTS_FILE_PATH, "w") as requirements_file:
            yaml.safe_dump(requirements_file_content, requirements_file)
        print("CREATED_REQUIREMENTS_FILE=true")
    else:
        print("CREATED_REQUIREMENTS_FILE=false")


def print_mandatory_reviewers():
    teams = set()
    mandatory_reviewers = find_mandatory_reviewers()
    for reviewers in mandatory_reviewers:
        teams.update(reviewers["teams"])
    print(f"MANDATORY_REVIEWERS=A review is required from these teams: {', '.join(teams)}")
