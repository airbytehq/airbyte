#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Dict, List, Set, Tuple, Union

import yaml
from connector_ops import utils

# TODO: Check to see if GL still wants to get tagged in this. If so,
# the logic needs to be audited to make sure its actually just python.
STRATEGIC_PYTHON_CONNECTOR_REVIEWERS = {"gl-python"}
# The breaking change reviewers is still in active use.
BREAKING_CHANGE_REVIEWERS = {"breaking-change-reviewers"}
REVIEW_REQUIREMENTS_FILE_PATH = ".github/connector_org_review_requirements.yaml"


def find_changed_strategic_connectors(
    languages: Tuple[utils.ConnectorLanguage] = (
        utils.ConnectorLanguage.JAVA,
        utils.ConnectorLanguage.LOW_CODE,
        utils.ConnectorLanguage.PYTHON,
    )
) -> Set[utils.Connector]:
    """Find important connectors modified on the current branch.

    Returns:
        Set[utils.Connector]: The set of important connectors that were modified on the current branch.
    """
    changed_connectors = utils.get_changed_connectors(destination=False, third_party=False)
    return {connector for connector in changed_connectors if connector.is_strategic_connector and connector.language in languages}


def find_mandatory_reviewers() -> List[Dict[str, Union[str, Dict[str, List]]]]:
    requirements = [
        {
            "name": "Strategic python connectors",
            "teams": list(STRATEGIC_PYTHON_CONNECTOR_REVIEWERS),
            "is_required": find_changed_strategic_connectors((utils.ConnectorLanguage.PYTHON, utils.ConnectorLanguage.LOW_CODE)),
        },
        {
            "name": "Breaking changes",
            "teams": list(BREAKING_CHANGE_REVIEWERS),
            "is_required": utils.get_changed_metadata(diff_regex="upgradeDeadline"),
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
