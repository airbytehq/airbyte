#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import shutil
from typing import List
import yaml

import pytest

from ci_connector_ops import sat_config_checks, utils


@pytest.fixture
def mock_diffed_branched(mocker):
    mocker.patch.object(sat_config_checks.utils, "DIFFED_BRANCH", utils.AIRBYTE_REPO.active_branch)
    return utils.AIRBYTE_REPO.active_branch

@pytest.fixture
def pokeapi_acceptance_test_config_path():
    return "airbyte-integrations/connectors/source-pokeapi/acceptance-test-config.yml"

@pytest.fixture
def ga_connector_file():
    return "airbyte-integrations/connectors/source-amplitude/acceptance-test-config.yml"

@pytest.fixture
def not_ga_backward_compatibility_change_expected_team(tmp_path, pokeapi_acceptance_test_config_path) -> List:
    expected_teams = [{"any-of": list(sat_config_checks.BACKWARD_COMPATIBILITY_REVIEWERS)}]
    backup_path = tmp_path / "backup_poke_acceptance"
    shutil.copyfile(pokeapi_acceptance_test_config_path, backup_path)
    with open(pokeapi_acceptance_test_config_path, "a") as acceptance_test_config_file:
        acceptance_test_config_file.write("disable_for_version: 0.0.0")
    yield expected_teams
    shutil.copyfile(backup_path, pokeapi_acceptance_test_config_path)

@pytest.fixture
def not_ga_test_strictness_level_change_expected_team(tmp_path, pokeapi_acceptance_test_config_path) -> List:
    expected_teams = [{"any-of": list(sat_config_checks.TEST_STRICTNESS_LEVEL_REVIEWERS)}]
    backup_path = tmp_path / "non_ga_acceptance_test_config.backup"
    shutil.copyfile(pokeapi_acceptance_test_config_path, backup_path)
    with open(pokeapi_acceptance_test_config_path, "a") as acceptance_test_config_file:
        acceptance_test_config_file.write("test_strictness_level: foo")
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
    expected_teams = list(sat_config_checks.GA_CONNECTOR_REVIEWERS)
    backup_path = tmp_path / "ga_acceptance_test_config.backup"
    shutil.copyfile(ga_connector_file, backup_path)
    with open(ga_connector_file, "a") as ga_acceptance_test_config_file:
        ga_acceptance_test_config_file.write("foobar")
    yield expected_teams
    shutil.copyfile(backup_path, ga_connector_file)

@pytest.fixture
def ga_connector_backward_compatibility_file_change(tmp_path, ga_connector_file):
    expected_teams = [{"any-of": list(sat_config_checks.BACKWARD_COMPATIBILITY_REVIEWERS)}]
    backup_path = tmp_path / "ga_acceptance_test_config.backup"
    shutil.copyfile(ga_connector_file, backup_path)
    with open(ga_connector_file, "a") as ga_acceptance_test_config_file:
        ga_acceptance_test_config_file.write("disable_for_version: 0.0.0")
    yield expected_teams
    shutil.copyfile(backup_path, ga_connector_file)

@pytest.fixture
def ga_connector_test_strictness_level_file_change(tmp_path, ga_connector_file):
    expected_teams = [{"any-of": list(sat_config_checks.TEST_STRICTNESS_LEVEL_REVIEWERS)}]
    backup_path = tmp_path / "ga_acceptance_test_config.backup"
    shutil.copyfile(ga_connector_file, backup_path)
    with open(ga_connector_file, "a") as ga_acceptance_test_config_file:
        ga_acceptance_test_config_file.write("test_strictness_level: 0.0.0")
    yield expected_teams
    shutil.copyfile(backup_path, ga_connector_file)

def check_review_requirements_file_contains_expected_teams(capsys, expected_teams: List):
    sat_config_checks.write_review_requirements_file()
    captured = capsys.readouterr()
    assert captured.out.split("\n")[0].split("=")[-1] == "true"
    requirements_file_path = sat_config_checks.REVIEW_REQUIREMENTS_FILE_PATH
    with open(requirements_file_path, "r") as requirements_file:
        requirements = yaml.safe_load(requirements_file)
    assert requirements[0]["teams"] == expected_teams

def test_find_mandatory_reviewers_backward_compatibility(mock_diffed_branched, capsys, not_ga_backward_compatibility_change_expected_team):
    check_review_requirements_file_contains_expected_teams(capsys, not_ga_backward_compatibility_change_expected_team)

    
def test_find_mandatory_reviewers_test_strictness_level(mock_diffed_branched, capsys, not_ga_test_strictness_level_change_expected_team):
    check_review_requirements_file_contains_expected_teams(capsys, not_ga_test_strictness_level_change_expected_team)

    
def test_find_mandatory_reviewers_ga(mock_diffed_branched, capsys, ga_connector_file_change_expected_team):
    check_review_requirements_file_contains_expected_teams(capsys, ga_connector_file_change_expected_team)

def test_find_mandatory_reviewers_ga_backward_compatibility(mock_diffed_branched, capsys, ga_connector_backward_compatibility_file_change):
    check_review_requirements_file_contains_expected_teams(capsys, ga_connector_backward_compatibility_file_change)

def test_find_mandatory_reviewers_ga_test_strictness_level(mock_diffed_branched, capsys, ga_connector_test_strictness_level_file_change):
    check_review_requirements_file_contains_expected_teams(capsys, ga_connector_test_strictness_level_file_change)

def test_find_mandatory_reviewers_no_tracked_changed(mock_diffed_branched, capsys, not_ga_not_tracked_change_expected_team):
    sat_config_checks.write_review_requirements_file()
    captured = capsys.readouterr()
    assert captured.out.split("\n")[0].split("=")[-1] == "false"
