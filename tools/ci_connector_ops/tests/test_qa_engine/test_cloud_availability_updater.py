#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
from pathlib import Path

import pytest
import git
import yaml

from ci_connector_ops.qa_engine import cloud_availability_updater, models

@pytest.fixture(scope="module")
def dummy_repo_path(tmp_path_factory) -> Path:
    repo_path = tmp_path_factory.mktemp("cloud_availability_updater_tests") / "airbyte-cloud"
    repo_path.mkdir()
    return repo_path

@pytest.fixture(scope="module")
def dummy_repo(dummy_repo_path) -> git.Repo:
    seed_dir = dummy_repo_path / "cloud-config/cloud-config-seed/src/main/resources/seed"
    seed_dir.mkdir(parents=True)
    repo = git.Repo.init(dummy_repo_path)
    source_definitions_mask_path = seed_dir / "source_definitions_mask.yaml"
    destination_definitions_mask_path = seed_dir / "destination_definitions_mask.yaml"
    source_definitions_mask_path.touch()
    destination_definitions_mask_path.touch()
    repo.git.add("--all")
    repo.git.commit(m=f"🤖 Initialized the repo")
    return repo


@pytest.fixture
def checkout_master(dummy_repo):
    """
    Ensure we're always on dummy repo master before and after each test using this fixture
    """
    yield dummy_repo.heads.master.checkout()
    dummy_repo.heads.master.checkout()

def test_get_definitions_mask_path(checkout_master, dummy_repo_path: Path):
    path = cloud_availability_updater.get_definitions_mask_path(dummy_repo_path, "source")
    assert path.exists() and path.name == "source_definitions_mask.yaml"
    path = cloud_availability_updater.get_definitions_mask_path(dummy_repo_path, "destination")
    assert path.exists() and path.name == "destination_definitions_mask.yaml"
    with pytest.raises(FileNotFoundError):
        cloud_availability_updater.get_definitions_mask_path(dummy_repo_path, "foobar")

def test_checkout_new_branch(mocker, checkout_master, dummy_repo):
    new_branch = cloud_availability_updater.checkout_new_branch(dummy_repo, "test-branch")
    assert new_branch.name == dummy_repo.active_branch.name == "test-branch"


@pytest.mark.parametrize(
    "definitions_mask_content_before_update, definition_id, expect_update",
    [
        ("", "abcdefg", True),
        ("abcdefg", "abcdefg", False),
    ]

)
def test_update_definitions_mask(
    mocker,
    tmp_path, 
    definitions_mask_content_before_update,
    definition_id, 
    expect_update
):
    connector = mocker.Mock(
        connector_name="foobar",
        connector_definition_id=definition_id,
        connector_type="unknown"
    )
    definitions_mask_path = tmp_path / "definitions_mask.yaml"
    with open(definitions_mask_path, "w") as definitions_mask:
        definitions_mask.write(definitions_mask_content_before_update)
    updated_path = cloud_availability_updater.update_definitions_mask(connector, definitions_mask_path)
    if not expect_update:
        assert updated_path is None
    else:
        with open(updated_path, "r") as definitions_mask:
            raw_content = definitions_mask.read()
            definitions = yaml.safe_load(raw_content)
        assert isinstance(definitions, list)
        assert definitions[0]["unknownDefinitionId"] == definition_id
        assert len(
        [
            d for d in definitions 
            if d["unknownDefinitionId"] == definition_id
        ]) == 1
        assert "# foobar (from cloud availability updater)" in raw_content
        assert raw_content[-1] == "\n"

def test_commit_files(checkout_master, dummy_repo, dummy_repo_path):
    cloud_availability_updater.checkout_new_branch(dummy_repo, "test-commit-files")
    commit_message = "🤖 Add new connector to cloud"
    with open(dummy_repo_path / "test_file.txt", "w") as f:
        f.write(".")
    
    cloud_availability_updater.commit_all_files(dummy_repo, commit_message)
    
    assert dummy_repo.head.reference.commit.message == commit_message + "\n"
    edited_files = dummy_repo.git.diff("--name-only", checkout_master.name).split("\n")
    assert "test_file.txt" in edited_files

def test_push_branch(mocker):
    mock_repo = mocker.Mock()
    cloud_availability_updater.push_branch(mock_repo, "new_branch")
    mock_repo.git.push.assert_called_once_with("--set-upstream", "origin", "new_branch")

@pytest.mark.slow
def test_deploy_new_connector_to_cloud_repo(mocker, tmp_path):
    mocker.patch.object(cloud_availability_updater, "push_branch")
    mocker.patch.object(cloud_availability_updater, "run_generate_cloud_connector_catalog")

    repo_path = tmp_path / "airbyte-cloud"
    repo_path.mkdir()
    airbyte_cloud_repo = cloud_availability_updater.clone_airbyte_cloud_repo(repo_path)
    source_definitions_mask_path = repo_path / "cloud-config/cloud-config-seed/src/main/resources/seed/source_definitions_mask.yaml"
    destination_definitions_mask_path = repo_path / "cloud-config/cloud-config-seed/src/main/resources/seed/destination_definitions_mask.yaml"
    assert source_definitions_mask_path.exists() and destination_definitions_mask_path.exists()
    
    connector = models.ConnectorQAReport(
        connector_type="source",
        connector_name="foobar",
        connector_technical_name="source-foobar",
        connector_definition_id="abcdefg",
        connector_version="0.0.0",
        release_stage="alpha",
        is_on_cloud=False,
        is_appropriate_for_cloud_use=True,
        latest_build_is_successful=True,
        documentation_is_available=True
    )
    cloud_availability_updater.deploy_new_connector_to_cloud_repo(repo_path, airbyte_cloud_repo, connector)
    new_branch_name = f"cloud-availability-updater/deploy-{connector.connector_technical_name}"

    cloud_availability_updater.push_branch.assert_called_once_with(airbyte_cloud_repo, new_branch_name)
    cloud_availability_updater.run_generate_cloud_connector_catalog.assert_called_once_with(repo_path)
    airbyte_cloud_repo.git.checkout(new_branch_name)
    edited_files = airbyte_cloud_repo.git.diff("--name-only", "master").split("\n")
    assert edited_files == ['cloud-config/cloud-config-seed/src/main/resources/seed/source_definitions_mask.yaml']
    assert airbyte_cloud_repo.head.reference.commit.message == "🤖 Add foobar connector to cloud\n"
