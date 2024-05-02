#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Dict, List, Set, Tuple, Union

import yaml
from connector_ops import utils

# The breaking change reviewers is still in active use.
BREAKING_CHANGE_REVIEWERS = {"breaking-change-reviewers"}
REVIEW_REQUIREMENTS_FILE_PATH = ".github/connector_org_review_requirements.yaml"


def find_mandatory_reviewers() -> List[Dict[str, Union[str, Dict[str, List]]]]:
    requirements = [
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
