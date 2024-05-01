#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import shutil
from typing import List

import git
import pytest
import yaml
from connector_ops import required_reviewer_checks


# This fixture ensure that the remote CI works the same way local CI does
@pytest.fixture(autouse=True)
def mock_diffed_branched(mocker):
    airbyte_repo = git.Repo(search_parent_directories=True)
    mocker.patch.object(required_reviewer_checks.utils, "DIFFED_BRANCH", airbyte_repo.active_branch)
    return airbyte_repo.active_branch


@pytest.fixture
def pokeapi_metadata_path():
    return "airbyte-integrations/connectors/source-pokeapi/metadata.yaml"


@pytest.fixture
def not_tracked_change_expected_team(tmp_path, pokeapi_metadata_path):
    expected_teams = []
    backup_path = tmp_path / "non_strategic_acceptance_test_config.backup"
    shutil.copyfile(pokeapi_metadata_path, backup_path)
    with open(pokeapi_metadata_path, "a") as metadata_file:
        metadata_file.write("not_tracked")
    yield expected_teams
    shutil.copyfile(backup_path, pokeapi_metadata_path)


@pytest.fixture
def test_breaking_change_release_expected_team(tmp_path, pokeapi_metadata_path) -> List:
    expected_teams = list(required_reviewer_checks.BREAKING_CHANGE_REVIEWERS)
    backup_path = tmp_path / "backup_poke_metadata"
    shutil.copyfile(pokeapi_metadata_path, backup_path)
    with open(pokeapi_metadata_path, "a") as acceptance_test_config_file:
        acceptance_test_config_file.write(
            "releases:\n  breakingChanges:\n    23.0.0:\n      message: hi\n      upgradeDeadline: 2025-01-01"
        )
    yield expected_teams
    shutil.copyfile(backup_path, pokeapi_metadata_path)


def verify_no_requirements_file_was_generated(captured: str):
    assert captured.out.split("\n")[0].split("=")[-1] == "false"


def verify_requirements_file_was_generated(captured: str):
    assert captured.out.split("\n")[0].split("=")[-1] == "true"


def verify_review_requirements_file_contains_expected_teams(requirements_file_path: str, expected_teams: List):
    with open(requirements_file_path, "r") as requirements_file:
        requirements = yaml.safe_load(requirements_file)
    all_required_teams = set().union(*(r["teams"] for r in requirements))
    assert all_required_teams == set(expected_teams)


def check_review_requirements_file(capsys, expected_teams: List):
    required_reviewer_checks.write_review_requirements_file()
    captured = capsys.readouterr()
    if not expected_teams:
        verify_no_requirements_file_was_generated(captured)
    else:
        verify_requirements_file_was_generated(captured)
        requirements_file_path = required_reviewer_checks.REVIEW_REQUIREMENTS_FILE_PATH
        verify_review_requirements_file_contains_expected_teams(requirements_file_path, expected_teams)


def test_find_mandatory_reviewers_breaking_change_release(capsys, test_breaking_change_release_expected_team):
    check_review_requirements_file(capsys, test_breaking_change_release_expected_team)


def test_find_mandatory_reviewers_no_tracked_changed(capsys, not_tracked_change_expected_team):
    check_review_requirements_file(capsys, not_tracked_change_expected_team)
