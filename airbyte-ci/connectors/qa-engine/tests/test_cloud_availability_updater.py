#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import datetime
from pathlib import Path

import freezegun
import git
import pytest
import yaml
from qa_engine import cloud_availability_updater, models


@pytest.fixture(scope="module")
def dummy_repo_path(tmp_path_factory) -> Path:
    repo_path = tmp_path_factory.mktemp("cloud_availability_updater_tests") / "airbyte"
    repo_path.mkdir()
    return repo_path


@pytest.fixture(scope="module")
def eligible_connectors():
    return [
        models.ConnectorQAReport(
            connector_type="source",
            connector_name="PokeAPI",
            release_stage="alpha",
            is_on_cloud=False,
            is_appropriate_for_cloud_use=True,
            latest_build_is_successful=True,
            documentation_is_available=True,
            number_of_users=1,
            total_syncs_count=1,
            failed_syncs_count=0,
            succeeded_syncs_count=1,
            is_eligible_for_promotion_to_cloud=True,
            report_generation_datetime=datetime.datetime.utcnow(),
            connector_technical_name="source-pokeapi",
            connector_version="0.0.0",
            connector_definition_id="pokeapi-definition-id",
            sync_success_rate=0.989,
            number_of_connections=12,
        )
    ]


@pytest.fixture(scope="module")
def excluded_connectors():
    return [
        models.ConnectorQAReport(
            connector_type="source",
            connector_name="excluded",
            release_stage="alpha",
            is_on_cloud=False,
            is_appropriate_for_cloud_use=True,
            latest_build_is_successful=True,
            documentation_is_available=True,
            number_of_users=1,
            total_syncs_count=1,
            failed_syncs_count=0,
            succeeded_syncs_count=1,
            is_eligible_for_promotion_to_cloud=True,
            report_generation_datetime=datetime.datetime.utcnow(),
            connector_technical_name="source-excluded",
            connector_version="0.0.0",
            connector_definition_id="excluded-definition-id",
            sync_success_rate=0.979,
            number_of_connections=12,
        )
    ]


@pytest.fixture(scope="module")
def dummy_repo(dummy_repo_path, eligible_connectors, excluded_connectors) -> git.Repo:
    all_connectors = eligible_connectors + excluded_connectors
    connectors_dir = dummy_repo_path / "airbyte-integrations/connectors"
    connectors_dir.mkdir(parents=True)
    repo = git.Repo.init(dummy_repo_path)

    # set master branch instead of main
    repo.git.checkout(b="master")

    for connector in all_connectors:
        connector_dir = connectors_dir / connector.connector_technical_name
        connector_dir.mkdir()
        metadata_path = connector_dir / "metadata.yaml"
        metadata_path.touch()

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


def test_get_metadata_file_path(checkout_master, eligible_connectors, dummy_repo_path: Path):
    for connector in eligible_connectors:
        path = cloud_availability_updater.get_metadata_file_path(dummy_repo_path, connector)
        assert path.exists() and path.name == "metadata.yaml"


def test_checkout_new_branch(mocker, checkout_master, dummy_repo):
    new_branch = cloud_availability_updater.checkout_new_branch(dummy_repo, "test-branch")
    assert new_branch.name == dummy_repo.active_branch.name == "test-branch"


@pytest.mark.parametrize("expect_update", [True, False])
def test_enable_in_cloud(mocker, dummy_repo_path, expect_update, eligible_connectors):
    connector = eligible_connectors[0]
    connector_metadata_path = dummy_repo_path / f"airbyte-integrations/connectors/{connector.connector_technical_name}" / "metadata.yaml"
    with open(connector_metadata_path, "w") as definitions_mask:
        mask_yaml = yaml.safe_dump({"data": {"registries": {"cloud": {"enabled": not expect_update}}}})
        definitions_mask.write(mask_yaml)
    updated_path = cloud_availability_updater.enable_in_cloud(connector, connector_metadata_path)
    if not expect_update:
        assert updated_path is None
    else:
        with open(updated_path, "r") as definitions_mask:
            raw_content = definitions_mask.read()
            metadata_content = yaml.safe_load(raw_content)
        assert isinstance(metadata_content, dict)
        assert metadata_content["data"]["registries"]["cloud"]["enabled"] is True


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


@pytest.mark.parametrize("updated_files", [True, False])
def test_add_new_connector_to_cloud_catalog(mocker, updated_files, dummy_repo_path):
    mocker.patch.object(cloud_availability_updater, "get_metadata_file_path")
    mocker.patch.object(cloud_availability_updater, "enable_in_cloud", mocker.Mock(return_value=updated_files))
    mocker.patch.object(cloud_availability_updater, "commit_all_files")

    connector = mocker.Mock()
    repo = mocker.Mock()

    updated_connector = cloud_availability_updater.add_new_connector_to_cloud_catalog(dummy_repo_path, repo, connector)
    assert updated_connector == updated_files
    cloud_availability_updater.get_metadata_file_path.assert_called_with(dummy_repo_path, connector)
    cloud_availability_updater.enable_in_cloud.assert_called_once_with(
        connector, cloud_availability_updater.get_metadata_file_path.return_value
    )
    if updated_files:
        cloud_availability_updater.commit_all_files.assert_called_with(repo, f"🤖 Add {connector.connector_name} connector to cloud")


@pytest.mark.parametrize("pr_already_created", [True, False, True])
def test_create_pr(mocker, pr_already_created):
    mocker.patch.object(cloud_availability_updater, "requests")
    pr_post_response = mocker.Mock(json=mocker.Mock(return_value={"url": "pr_url", "number": "pr_number"}))
    cloud_availability_updater.requests.post.side_effect = [pr_post_response, mocker.Mock()]
    mocker.patch.object(cloud_availability_updater, "pr_already_created_for_branch", mocker.Mock(return_value=pr_already_created))
    mocker.patch.object(cloud_availability_updater, "GITHUB_API_COMMON_HEADERS", {"common": "headers"})
    expected_pr_url = "https://api.github.com/repos/airbytehq/airbyte/pulls"
    expected_pr_data = {
        "title": "my pr title",
        "body": "my pr body",
        "head": "my_awesome_branch",
        "base": "master",
    }
    expected_issue_url = "https://api.github.com/repos/airbytehq/airbyte/issues/pr_number/labels"
    expected_issue_data = {"labels": cloud_availability_updater.PR_LABELS}

    response = cloud_availability_updater.create_pr("my pr title", "my pr body", "my_awesome_branch", cloud_availability_updater.PR_LABELS)

    if not pr_already_created:
        expected_post_calls = [
            mocker.call(expected_pr_url, headers=cloud_availability_updater.GITHUB_API_COMMON_HEADERS, json=expected_pr_data),
            mocker.call(expected_issue_url, headers=cloud_availability_updater.GITHUB_API_COMMON_HEADERS, json=expected_issue_data),
        ]
        cloud_availability_updater.requests.post.assert_has_calls(expected_post_calls, any_order=False)
        assert response == pr_post_response
    else:
        assert response is None


@pytest.mark.parametrize("json_response, expected_result", [([], False), (["foobar"], True)])
def test_pr_already_created_for_connector(mocker, json_response, expected_result):
    mocker.patch.object(cloud_availability_updater.requests, "get")
    cloud_availability_updater.requests.get.return_value.json.return_value = json_response
    mocker.patch.object(cloud_availability_updater, "GITHUB_API_COMMON_HEADERS", {"common": "headers"})

    is_already_created = cloud_availability_updater.pr_already_created_for_branch("my-awesome-branch")
    expected_url = "https://api.github.com/repos/airbytehq/airbyte/pulls"
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


def test_get_authenticated_repo_url(mocker):
    mocker.patch.object(cloud_availability_updater, "AIRBYTE_GITHUB_REPO_URL", "https://foobar.com")
    repo_url = cloud_availability_updater.get_authenticated_repo_url("username", "token")
    assert repo_url == "https://username:token@foobar.com"


@pytest.mark.parametrize("response, expected_output", [([], False), (["foo"], True)])
def test_pr_already_created_for_branch(mocker, response, expected_output):
    mocker.patch.object(cloud_availability_updater, "requests")

    cloud_availability_updater.requests.get.return_value = mocker.Mock(json=mocker.Mock(return_value=response))
    output = cloud_availability_updater.pr_already_created_for_branch("foo")
    assert output == expected_output
    cloud_availability_updater.requests.get.return_value.raise_for_status.assert_called_once()
    cloud_availability_updater.requests.get.assert_called_with(
        cloud_availability_updater.AIRBYTE_PR_ENDPOINT,
        headers=cloud_availability_updater.GITHUB_API_COMMON_HEADERS,
        params={"head": f"{cloud_availability_updater.AIRBYTE_REPO_OWNER}:foo", "state": "open"},
    )


def test_add_labels_to_pr(mocker):
    mocker.patch.object(cloud_availability_updater, "requests")
    labels_to_add = ["foo", "bar"]
    response = cloud_availability_updater.add_labels_to_pr("1", labels_to_add)
    cloud_availability_updater.requests.post.assert_called_with(
        f"{cloud_availability_updater.AIRBYTE_ISSUES_ENDPOINT}/1/labels",
        headers=cloud_availability_updater.GITHUB_API_COMMON_HEADERS,
        json={"labels": labels_to_add},
    )
    cloud_availability_updater.requests.post.return_value.raise_for_status.assert_called_once()
    assert response == cloud_availability_updater.requests.post.return_value


def test_get_pr_body(mocker, eligible_connectors, excluded_connectors):
    pr_body = cloud_availability_updater.get_pr_body(eligible_connectors, excluded_connectors)
    assert "1 connectors available on Cloud!" in pr_body.split("/n")[0]
    assert "# Promoted connectors\n" in pr_body
    assert "# Excluded but eligible connectors\n" in pr_body
    assert "connector_technical_name" in pr_body
    assert "connector_version" in pr_body
    assert "connector_definition_id" in pr_body
    assert "source-pokeapi" in pr_body
    assert "pokeapi-definition-id" in pr_body
    assert "0.0.0" in pr_body
    assert "source-excluded" in pr_body
    assert "excluded-definition-id" in pr_body


@freezegun.freeze_time("2023-02-14")
@pytest.mark.parametrize("added_connectors", [True, False])
def test_batch_deploy_eligible_connectors_to_cloud_repo(
    mocker, dummy_repo_path, added_connectors, eligible_connectors, excluded_connectors
):
    all_connectors = eligible_connectors + excluded_connectors
    mocker.patch.object(cloud_availability_updater.tempfile, "mkdtemp", mocker.Mock(return_value=str(dummy_repo_path)))
    mocker.patch.object(cloud_availability_updater, "clone_airbyte_repo")
    mocker.patch.object(cloud_availability_updater, "set_git_identity")
    mocker.patch.object(cloud_availability_updater, "checkout_new_branch")
    mocker.patch.object(cloud_availability_updater, "add_new_connector_to_cloud_catalog")
    mocker.patch.object(cloud_availability_updater, "enable_in_cloud", side_effect=False)
    mocker.patch.object(cloud_availability_updater, "push_branch")
    mocker.patch.object(cloud_availability_updater, "get_pr_body")
    mocker.patch.object(cloud_availability_updater, "create_pr")
    mocker.patch.object(cloud_availability_updater, "shutil")

    if added_connectors:
        cloud_availability_updater.add_new_connector_to_cloud_catalog.side_effect = lambda _path, _repo, connector: (
            connector not in expected_excluded_connectors
        )
        expected_added_connectors = eligible_connectors
    else:
        cloud_availability_updater.add_new_connector_to_cloud_catalog.return_value = False

    expected_excluded_connectors = excluded_connectors

    mock_repo = cloud_availability_updater.set_git_identity.return_value
    expected_new_branch_name = "cloud-availability-updater/batch-deploy/20230214"
    expected_pr_title = "🤖 Cloud Availability updater: new connectors to deploy [20230214]"

    cloud_availability_updater.batch_deploy_eligible_connectors_to_cloud_repo(all_connectors)
    cloud_availability_updater.clone_airbyte_repo.assert_called_once_with(dummy_repo_path)
    cloud_availability_updater.set_git_identity.assert_called_once_with(cloud_availability_updater.clone_airbyte_repo.return_value)
    mock_repo.git.checkout.assert_called_with(cloud_availability_updater.AIRBYTE_MAIN_BRANCH_NAME)

    cloud_availability_updater.checkout_new_branch.assert_called_once_with(mock_repo, expected_new_branch_name)
    cloud_availability_updater.add_new_connector_to_cloud_catalog.assert_has_calls(
        [
            mocker.call(dummy_repo_path, cloud_availability_updater.set_git_identity.return_value, eligible_connectors[0]),
        ]
    )
    if added_connectors:
        cloud_availability_updater.push_branch.assert_called_once_with(mock_repo, expected_new_branch_name)
        cloud_availability_updater.create_pr.assert_called_once_with(
            expected_pr_title,
            cloud_availability_updater.get_pr_body.return_value,
            expected_new_branch_name,
            cloud_availability_updater.PR_LABELS,
        )
        cloud_availability_updater.get_pr_body.assert_called_with(expected_added_connectors, expected_excluded_connectors)
    else:
        cloud_availability_updater.push_branch.assert_not_called()
        cloud_availability_updater.create_pr.assert_not_called()
    cloud_availability_updater.shutil.rmtree.assert_called_with(dummy_repo_path)
