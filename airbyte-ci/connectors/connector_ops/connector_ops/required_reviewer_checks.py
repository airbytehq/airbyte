#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Dict, List, Optional, Set, Tuple, Union

import yaml

from connector_ops import utils


# The breaking change reviewers is still in active use.
BREAKING_CHANGE_REVIEWERS = {"breaking-change-reviewers"}
CERTIFIED_MANIFEST_ONLY_CONNECTOR_REVIEWERS = {"dev-python"}
COMMUNITY_MANIFEST_ONLY_CONNECTOR_REVIEWERS = {"dev-marketplace-contributions"}
REVIEW_REQUIREMENTS_FILE_PATH = ".github/connector_org_review_requirements.yaml"


def find_changed_manifest_only_connectors(support_level: str) -> Set[utils.Connector]:
    """Find manifest-only connectors modified on the current branch for a given support level.

    Args:
        support_level (str): The support level of the connectors to find.
    Returns:
        Set[utils.Connector]: The set of manifest-only connectors that were modified on the current branch
        and match the provided support level, if provided.
    """
    changed_connectors = utils.get_changed_connectors()
    manifest_only_connectors = {
        connector for connector in changed_connectors if connector.language == utils.ConnectorLanguage.MANIFEST_ONLY
    }
    if support_level:
        return {connector for connector in manifest_only_connectors if connector.support_level == support_level}
    return manifest_only_connectors


def find_mandatory_reviewers() -> List[Dict[str, Union[str, Dict[str, List]]]]:
    requirements = [
        {
            "name": "Breaking changes",
            "teams": list(BREAKING_CHANGE_REVIEWERS),
            "is_required": utils.get_changed_metadata(diff_regex="upgradeDeadline"),
        },
        {
            "name": "Manifest-only certified connectors",
            "teams": list(CERTIFIED_MANIFEST_ONLY_CONNECTOR_REVIEWERS),
            "is_required": find_changed_manifest_only_connectors(support_level="certified"),
        },
    ]

    return [{"name": r["name"], "teams": r["teams"]} for r in requirements if r["is_required"]]


def write_review_requirements_file():
    mandatory_reviewers = find_mandatory_reviewers()

    if mandatory_reviewers:
        requirements_file_content = [dict(r, paths=["**"]) for r in mandatory_reviewers]
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
