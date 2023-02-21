#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
from pathlib import Path

import git
import pytest
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
    repo.git.commit(m="🤖 Initialized the repo")
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
    ],
)
def test_update_definitions_mask(mocker, tmp_path, definitions_mask_content_before_update, definition_id, expect_update):
    connector = mocker.Mock(connector_name="foobar", connector_definition_id=definition_id, connector_type="unknown")
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
        assert len([d for d in definitions if d["unknownDefinitionId"] == definition_id]) == 1
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
    mock_repo.git.push.assert_called_once_with("--force", "--set-upstream", "origin", "new_branch")


@pytest.mark.slow
def test_deploy_new_connector_to_cloud_repo(mocker, tmp_path):
    mocker.patch.object(cloud_availability_updater, "push_branch")
    mocker.patch.object(cloud_availability_updater, "run_generate_cloud_connector_catalog")
    mocker.patch.object(cloud_availability_updater, "create_pr")
    mocker.patch.object(
        cloud_availability_updater,
        "get_authenticated_repo_url",
        mocker.Mock(return_value=cloud_availability_updater.AIRBYTE_PLATFORM_INTERNAL_GITHUB_REPO_URL),
    )
    repo_path = tmp_path / "airbyte-cloud"
    repo_path.mkdir()
    airbyte_cloud_repo = cloud_availability_updater.clone_airbyte_cloud_repo(repo_path)
    source_definitions_mask_path = repo_path / "cloud-config/cloud-config-seed/src/main/resources/seed/source_definitions_mask.yaml"
    destination_definitions_mask_path = (
        repo_path / "cloud-config/cloud-config-seed/src/main/resources/seed/destination_definitions_mask.yaml"
    )
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
        documentation_is_available=True,
        number_of_connections=0,
        number_of_users=0,
        sync_success_rate=0.99,
        total_syncs_count=0,
        failed_syncs_count=0,
        succeeded_syncs_count=0,
        is_eligible_for_promotion_to_cloud=True,
        report_generation_datetime=datetime.utcnow(),
    )
    cloud_availability_updater.deploy_new_connector_to_cloud_repo(repo_path, airbyte_cloud_repo, connector)
    new_branch_name = f"cloud-availability-updater/deploy-{connector.connector_technical_name}"

    cloud_availability_updater.push_branch.assert_called_once_with(airbyte_cloud_repo, new_branch_name)
    cloud_availability_updater.run_generate_cloud_connector_catalog.assert_called_once_with(repo_path)
    airbyte_cloud_repo.git.checkout(new_branch_name)
    edited_files = airbyte_cloud_repo.git.diff("--name-only", "master").split("\n")
    assert edited_files == ["cloud-config/cloud-config-seed/src/main/resources/seed/source_definitions_mask.yaml"]
    assert airbyte_cloud_repo.head.reference.commit.message == "🤖 Add foobar connector to cloud\n"


@pytest.mark.parametrize("pr_already_created", [True, False, True])
def test_create_pr(mocker, pr_already_created):
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
        documentation_is_available=True,
        number_of_connections=0,
        number_of_users=0,
        sync_success_rate=0.99,
        total_syncs_count=0,
        failed_syncs_count=0,
        succeeded_syncs_count=0,
        is_eligible_for_promotion_to_cloud=True,
        report_generation_datetime=datetime.utcnow(),
    )
    mocker.patch.object(cloud_availability_updater, "requests")
    pr_post_response = mocker.Mock(json=mocker.Mock(return_value={"url": "pr_url", "number": "pr_number"}))
    cloud_availability_updater.requests.post.side_effect = [pr_post_response, mocker.Mock()]
    mocker.patch.object(cloud_availability_updater, "pr_already_created_for_branch", mocker.Mock(return_value=pr_already_created))
    mocker.patch.object(cloud_availability_updater, "GITHUB_API_COMMON_HEADERS", {"common": "headers"})
    response = cloud_availability_updater.create_pr(connector, "my_awesome_branch")
    expected_pr_url = "https://api.github.com/repos/airbytehq/airbyte-platform-internal/pulls"
    expected_body = f"""The Cloud Availability Updater decided that it's the right time to make {connector.connector_name} available on Cloud!
    - Technical name: {connector.connector_technical_name}
    - Version: {connector.connector_version}
    - Definition ID: {connector.connector_definition_id}
    - OSS sync success rate: {connector.sync_success_rate}
    - OSS number of connections: {connector.number_of_connections}
    """
    expected_pr_data = {
        "title": "🤖 Add source-foobar to cloud",
        "body": expected_body,
        "head": "my_awesome_branch",
        "base": "master",
    }
    expected_issue_url = "https://api.github.com/repos/airbytehq/airbyte-platform-internal/issues/pr_number/labels"
    expected_issue_data = {"labels": cloud_availability_updater.PR_LABELS}
    if not pr_already_created:
        expected_post_calls = [
            mocker.call(expected_pr_url, headers=cloud_availability_updater.GITHUB_API_COMMON_HEADERS, json=expected_pr_data),
            mocker.call(expected_issue_url, headers=cloud_availability_updater.GITHUB_API_COMMON_HEADERS, json=expected_issue_data),
        ]
        cloud_availability_updater.requests.post.assert_has_calls(expected_post_calls, any_order=False)
        assert response == pr_post_response


@pytest.mark.parametrize("json_response, expected_result", [([], False), (["foobar"], True)])
def test_pr_already_created_for_connector(mocker, json_response, expected_result):
    mocker.patch.object(cloud_availability_updater.requests, "get")
    cloud_availability_updater.requests.get.return_value.json.return_value = json_response
    mocker.patch.object(cloud_availability_updater, "GITHUB_API_COMMON_HEADERS", {"common": "headers"})

    is_already_created = cloud_availability_updater.pr_already_created_for_branch("my-awesome-branch")
    expected_url = "https://api.github.com/repos/airbytehq/airbyte-platform-internal/pulls"
    expected_headers = {"common": "headers"}
    expected_params = {"head": "airbytehq:my-awesome-branch", "state": "open"}
    cloud_availability_updater.requests.get.assert_called_with(expected_url, headers=expected_headers, params=expected_params)
    assert is_already_created == expected_result


def test_set_git_identity(mocker):
    mock_repo = mocker.Mock()
    repo = cloud_availability_updater.set_git_identity(mock_repo)
    repo.git.config.assert_has_calls(
        [
            mocker.call("--global", "user.email", cloud_availability_updater.GIT_USER_EMAIL),
            mocker.call("--global", "user.name", cloud_availability_updater.GIT_USERNAME),
        ]
    )
    assert repo == mock_repo


def test_deploy_eligible_connectors_to_cloud_repo(mocker, tmp_path):
    mocker.patch.object(cloud_availability_updater.tempfile, "mkdtemp", mocker.Mock(return_value=str(tmp_path)))
    mocker.patch.object(cloud_availability_updater, "clone_airbyte_cloud_repo")
    mocker.patch.object(cloud_availability_updater, "set_git_identity")
    mocker.patch.object(cloud_availability_updater, "deploy_new_connector_to_cloud_repo")
    mocker.patch.object(cloud_availability_updater, "shutil")
    eligible_connectors = [mocker.Mock(), mocker.Mock()]
    cloud_availability_updater.deploy_eligible_connectors_to_cloud_repo(eligible_connectors)
    cloud_availability_updater.clone_airbyte_cloud_repo.assert_called_once_with(tmp_path)
    cloud_availability_updater.set_git_identity.assert_called_once_with(cloud_availability_updater.clone_airbyte_cloud_repo.return_value)
    cloud_availability_updater.deploy_new_connector_to_cloud_repo.assert_has_calls(
        [
            mocker.call(tmp_path, cloud_availability_updater.set_git_identity.return_value, eligible_connectors[0]),
            mocker.call(tmp_path, cloud_availability_updater.set_git_identity.return_value, eligible_connectors[1]),
        ]
    )
    cloud_availability_updater.shutil.rmtree.assert_called_with(tmp_path)
