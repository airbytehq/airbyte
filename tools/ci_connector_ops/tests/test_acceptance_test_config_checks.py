#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import shutil
from typing import List

import git
import pytest
import yaml
from ci_connector_ops import acceptance_test_config_checks


@pytest.fixture
def mock_diffed_branched(mocker):
    airbyte_repo = git.Repo(search_parent_directories=True)
    mocker.patch.object(acceptance_test_config_checks.utils, "DIFFED_BRANCH", airbyte_repo.active_branch)
    return airbyte_repo.active_branch


@pytest.fixture
def pokeapi_acceptance_test_config_path():
    return "airbyte-integrations/connectors/source-pokeapi/acceptance-test-config.yml"


@pytest.fixture
def ga_connector_file():
    return "airbyte-integrations/connectors/source-amplitude/acceptance-test-config.yml"


@pytest.fixture
def not_ga_backward_compatibility_change_expected_team(tmp_path, pokeapi_acceptance_test_config_path) -> List:
    expected_teams = [{"any-of": list(acceptance_test_config_checks.BACKWARD_COMPATIBILITY_REVIEWERS)}]
    backup_path = tmp_path / "backup_poke_acceptance"
    shutil.copyfile(pokeapi_acceptance_test_config_path, backup_path)
    with open(pokeapi_acceptance_test_config_path, "a") as acceptance_test_config_file:
        acceptance_test_config_file.write("disable_for_version: 0.0.0")
    yield expected_teams
    shutil.copyfile(backup_path, pokeapi_acceptance_test_config_path)


@pytest.fixture
def not_ga_test_strictness_level_change_expected_team(tmp_path, pokeapi_acceptance_test_config_path) -> List:
    expected_teams = [{"any-of": list(acceptance_test_config_checks.TEST_STRICTNESS_LEVEL_REVIEWERS)}]
    backup_path = tmp_path / "non_ga_acceptance_test_config.backup"
    shutil.copyfile(pokeapi_acceptance_test_config_path, backup_path)
    with open(pokeapi_acceptance_test_config_path, "a") as acceptance_test_config_file:
        acceptance_test_config_file.write("test_strictness_level: foo")
    yield expected_teams
    shutil.copyfile(backup_path, pokeapi_acceptance_test_config_path)


@pytest.fixture
def not_ga_bypass_reason_file_change_expected_team(tmp_path, pokeapi_acceptance_test_config_path):
    expected_teams = []
    backup_path = tmp_path / "non_ga_acceptance_test_config.backup"
    shutil.copyfile(pokeapi_acceptance_test_config_path, backup_path)
    with open(pokeapi_acceptance_test_config_path, "a") as acceptance_test_config_file:
        acceptance_test_config_file.write("bypass_reason:")
    yield expected_teams
    shutil.copyfile(backup_path, pokeapi_acceptance_test_config_path)


@pytest.fixture
def not_ga_not_tracked_change_expected_team(tmp_path, pokeapi_acceptance_test_config_path):
    expected_teams = []
    backup_path = tmp_path / "non_ga_acceptance_test_config.backup"
    shutil.copyfile(pokeapi_acceptance_test_config_path, backup_path)
    with open(pokeapi_acceptance_test_config_path, "a") as acceptance_test_config_file:
        acceptance_test_config_file.write("not_tracked")
    yield expected_teams
    shutil.copyfile(backup_path, pokeapi_acceptance_test_config_path)


@pytest.fixture
def ga_connector_file_change_expected_team(tmp_path, ga_connector_file):
    expected_teams = list(acceptance_test_config_checks.GA_CONNECTOR_REVIEWERS)
    backup_path = tmp_path / "ga_acceptance_test_config.backup"
    shutil.copyfile(ga_connector_file, backup_path)
    with open(ga_connector_file, "a") as ga_acceptance_test_config_file:
        ga_acceptance_test_config_file.write("foobar")
    yield expected_teams
    shutil.copyfile(backup_path, ga_connector_file)


@pytest.fixture
def ga_connector_backward_compatibility_file_change_expected_team(tmp_path, ga_connector_file):
    expected_teams = [{"any-of": list(acceptance_test_config_checks.BACKWARD_COMPATIBILITY_REVIEWERS)}]
    backup_path = tmp_path / "ga_acceptance_test_config.backup"
    shutil.copyfile(ga_connector_file, backup_path)
    with open(ga_connector_file, "a") as ga_acceptance_test_config_file:
        ga_acceptance_test_config_file.write("disable_for_version: 0.0.0")
    yield expected_teams
    shutil.copyfile(backup_path, ga_connector_file)


@pytest.fixture
def ga_connector_bypass_reason_file_change_expected_team(tmp_path, ga_connector_file):
    expected_teams = [{"any-of": list(acceptance_test_config_checks.GA_BYPASS_REASON_REVIEWERS)}]
    backup_path = tmp_path / "ga_acceptance_test_config.backup"
    shutil.copyfile(ga_connector_file, backup_path)
    with open(ga_connector_file, "a") as ga_acceptance_test_config_file:
        ga_acceptance_test_config_file.write("bypass_reason:")
    yield expected_teams
    shutil.copyfile(backup_path, ga_connector_file)


@pytest.fixture
def ga_connector_test_strictness_level_file_change_expected_team(tmp_path, ga_connector_file):
    expected_teams = [{"any-of": list(acceptance_test_config_checks.TEST_STRICTNESS_LEVEL_REVIEWERS)}]
    backup_path = tmp_path / "ga_acceptance_test_config.backup"
    shutil.copyfile(ga_connector_file, backup_path)
    with open(ga_connector_file, "a") as ga_acceptance_test_config_file:
        ga_acceptance_test_config_file.write("test_strictness_level: 0.0.0")
    yield expected_teams
    shutil.copyfile(backup_path, ga_connector_file)


def verify_no_requirements_file_was_generated(captured: str):
    assert captured.out.split("\n")[0].split("=")[-1] == "false"


def verify_requirements_file_was_generated(captured: str):
    assert captured.out.split("\n")[0].split("=")[-1] == "true"


def verify_review_requirements_file_contains_expected_teams(requirements_file_path: str, expected_teams: List):
    with open(requirements_file_path, "r") as requirements_file:
        requirements = yaml.safe_load(requirements_file)
    assert requirements[0]["teams"] == expected_teams


def check_review_requirements_file(capsys, expected_teams: List):
    acceptance_test_config_checks.write_review_requirements_file()
    captured = capsys.readouterr()
    if not expected_teams:
        verify_no_requirements_file_was_generated(captured)
    else:
        verify_requirements_file_was_generated(captured)
        requirements_file_path = acceptance_test_config_checks.REVIEW_REQUIREMENTS_FILE_PATH
        verify_review_requirements_file_contains_expected_teams(requirements_file_path, expected_teams)


def test_find_mandatory_reviewers_backward_compatibility(mock_diffed_branched, capsys, not_ga_backward_compatibility_change_expected_team):
    check_review_requirements_file(capsys, not_ga_backward_compatibility_change_expected_team)


def test_find_mandatory_reviewers_test_strictness_level(mock_diffed_branched, capsys, not_ga_test_strictness_level_change_expected_team):
    check_review_requirements_file(capsys, not_ga_test_strictness_level_change_expected_team)


def test_find_mandatory_reviewers_not_ga_bypass_reason(mock_diffed_branched, capsys, not_ga_bypass_reason_file_change_expected_team):
    check_review_requirements_file(capsys, not_ga_bypass_reason_file_change_expected_team)


def test_find_mandatory_reviewers_ga(mock_diffed_branched, capsys, ga_connector_file_change_expected_team):
    check_review_requirements_file(capsys, ga_connector_file_change_expected_team)


def test_find_mandatory_reviewers_ga_backward_compatibility(
    mock_diffed_branched, capsys, ga_connector_backward_compatibility_file_change_expected_team
):
    check_review_requirements_file(capsys, ga_connector_backward_compatibility_file_change_expected_team)


def test_find_mandatory_reviewers_ga_bypass_reason(mock_diffed_branched, capsys, ga_connector_bypass_reason_file_change_expected_team):
    check_review_requirements_file(capsys, ga_connector_bypass_reason_file_change_expected_team)


def test_find_mandatory_reviewers_ga_test_strictness_level(
    mock_diffed_branched, capsys, ga_connector_test_strictness_level_file_change_expected_team
):
    check_review_requirements_file(capsys, ga_connector_test_strictness_level_file_change_expected_team)


def test_find_mandatory_reviewers_no_tracked_changed(mock_diffed_branched, capsys, not_ga_not_tracked_change_expected_team):
    check_review_requirements_file(capsys, not_ga_not_tracked_change_expected_team)
