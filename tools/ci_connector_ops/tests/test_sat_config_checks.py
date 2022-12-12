import pytest
import shutil

from ci_connector_ops import sat_config_checks

@pytest.fixture
def pokeapi_acceptance_test_config_path():
    return "airbyte-integrations/connectors/source-pokeapi/acceptance-test-config.yml"

@pytest.fixture
def ga_connector_file():
    return "airbyte-integrations/connectors/source-amplitude/Dockerfile"

@pytest.fixture
def acceptance_test_config_with_backward_compatibility_change(tmp_path, pokeapi_acceptance_test_config_path):
    backup_path = tmp_path / "backup_poke_acceptance"
    shutil.copyfile(pokeapi_acceptance_test_config_path, backup_path)
    with open(pokeapi_acceptance_test_config_path, "a") as acceptance_test_config_file:
        acceptance_test_config_file.write("disable_for_version: 0.0.0")
    yield pokeapi_acceptance_test_config_path
    shutil.copyfile(backup_path, pokeapi_acceptance_test_config_path)

@pytest.fixture
def acceptance_test_config_with_test_strictness_level_change(tmp_path, pokeapi_acceptance_test_config_path):
    backup_path = tmp_path / "backup_poke_acceptance"
    shutil.copyfile(pokeapi_acceptance_test_config_path, backup_path)
    with open(pokeapi_acceptance_test_config_path, "a") as acceptance_test_config_file:
        acceptance_test_config_file.write("test_strictness_level: foo")
    yield pokeapi_acceptance_test_config_path
    shutil.copyfile(backup_path, pokeapi_acceptance_test_config_path)

@pytest.fixture
def acceptance_test_config_with_no_tracked_change(tmp_path, pokeapi_acceptance_test_config_path):
    backup_path = tmp_path / "backup_poke_acceptance"
    shutil.copyfile(pokeapi_acceptance_test_config_path, backup_path)
    with open(pokeapi_acceptance_test_config_path, "a") as acceptance_test_config_file:
        acceptance_test_config_file.write("not_tracked")
    yield pokeapi_acceptance_test_config_path
    shutil.copyfile(backup_path, pokeapi_acceptance_test_config_path)


@pytest.fixture
def ga_connector_file_change(tmp_path, ga_connector_file):
    backup_path = tmp_path / "backup_ga_dockerfile"
    shutil.copyfile(ga_connector_file, backup_path)
    with open(ga_connector_file, "a") as ga_dockerfile:
        ga_dockerfile.write("foobar")
    yield ga_connector_file
    shutil.copyfile(backup_path, ga_connector_file)

def test_find_mandatory_reviewers_backward_compatibility(capsys, acceptance_test_config_with_backward_compatibility_change):
    mandatory_reviewers = sat_config_checks.BACKWARD_COMPATIBILITY_REVIEWERS
    expected_mandatory_reviewers = f"MANDATORY_REVIEWERS={','.join(mandatory_reviewers)}"
    sat_config_checks.print_mandatory_reviewers()
    captured = capsys.readouterr()
    assert expected_mandatory_reviewers in captured.out

    
def test_find_mandatory_reviewers_test_strictness_level(capsys, acceptance_test_config_with_test_strictness_level_change):
    mandatory_reviewers = sat_config_checks.TEST_STRICTNESS_LEVEL_REVIEWERS
    expected_mandatory_reviewers = f"MANDATORY_REVIEWERS={','.join(mandatory_reviewers)}"
    sat_config_checks.print_mandatory_reviewers()
    captured = capsys.readouterr()
    assert expected_mandatory_reviewers in captured.out

    
def test_find_mandatory_reviewers_ga(capsys, ga_connector_file_change):
    mandatory_reviewers = sat_config_checks.GA_CONNECTOR_REVIEWERS
    expected_mandatory_reviewers = f"MANDATORY_REVIEWERS={','.join(mandatory_reviewers)}"
    sat_config_checks.print_mandatory_reviewers()
    captured = capsys.readouterr()
    assert expected_mandatory_reviewers in captured.out


def test_find_mandatory_reviewers_no_tracked_changed(capsys, acceptance_test_config_with_no_tracked_change):
    expected_mandatory_reviewers = 'MANDATORY_REVIEWERS=""'
    sat_config_checks.print_mandatory_reviewers()
    captured = capsys.readouterr()
    assert expected_mandatory_reviewers in captured.out
