#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import datetime
from pathlib import Path

import freezegun
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


@pytest.mark.parametrize("updated_files", [True, False])
def test_add_new_connector_to_cloud_catalog(mocker, updated_files):
    mocker.patch.object(cloud_availability_updater, "get_definitions_mask_path")
    mocker.patch.object(cloud_availability_updater, "update_definitions_mask", mocker.Mock(return_value=updated_files))
    mocker.patch.object(cloud_availability_updater, "run_generate_cloud_connector_catalog")
    mocker.patch.object(cloud_availability_updater, "commit_all_files")

    connector = mocker.Mock()
    repo = mocker.Mock()
    repo_path = mocker.Mock()

    updated_connector = cloud_availability_updater.add_new_connector_to_cloud_catalog(repo_path, repo, connector)
    assert updated_connector == updated_files
    cloud_availability_updater.get_definitions_mask_path.assert_called_with(repo_path, connector.connector_type)
    cloud_availability_updater.update_definitions_mask.assert_called_once_with(
        connector, cloud_availability_updater.get_definitions_mask_path.return_value
    )
    if updated_files:
        cloud_availability_updater.run_generate_cloud_connector_catalog.assert_called_once_with(repo_path)
        cloud_availability_updater.commit_all_files.assert_called_with(repo, f"🤖 Add {connector.connector_name} connector to cloud")


@pytest.mark.parametrize("pr_already_created", [True, False, True])
def test_create_pr(mocker, pr_already_created):
    mocker.patch.object(cloud_availability_updater, "requests")
    pr_post_response = mocker.Mock(json=mocker.Mock(return_value={"url": "pr_url", "number": "pr_number"}))
    cloud_availability_updater.requests.post.side_effect = [pr_post_response, mocker.Mock()]
    mocker.patch.object(cloud_availability_updater, "pr_already_created_for_branch", mocker.Mock(return_value=pr_already_created))
    mocker.patch.object(cloud_availability_updater, "GITHUB_API_COMMON_HEADERS", {"common": "headers"})
    expected_pr_url = "https://api.github.com/repos/airbytehq/airbyte-platform-internal/pulls"
    expected_pr_data = {
        "title": "my pr title",
        "body": "my pr body",
        "head": "my_awesome_branch",
        "base": "master",
    }
    expected_issue_url = "https://api.github.com/repos/airbytehq/airbyte-platform-internal/issues/pr_number/labels"
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


def test_get_authenticated_repo_url(mocker):
    mocker.patch.object(cloud_availability_updater, "AIRBYTE_PLATFORM_INTERNAL_GITHUB_REPO_URL", "https://foobar.com")
    repo_url = cloud_availability_updater.get_authenticated_repo_url("username", "token")
    assert repo_url == "https://username:token@foobar.com"


@pytest.mark.slow
def test_clone_airbyte_cloud_repo(mocker, tmp_path):
    mocker.patch.object(
        cloud_availability_updater, "get_authenticated_repo_url", mocker.Mock(return_value="https://github.com/airbytehq/airbyte.git")
    )
    mocker.patch.object(cloud_availability_updater, "AIRBYTE_PLATFORM_INTERNAL_MAIN_BRANCH_NAME", "master")
    repo = cloud_availability_updater.clone_airbyte_cloud_repo(tmp_path)
    assert repo
    assert len(repo.heads) == 1
    assert repo.heads[0].name == "master"


def test_run_generate_cloud_connector_catalog(mocker, tmp_path):
    mocker.patch.object(cloud_availability_updater, "subprocess")

    result = cloud_availability_updater.run_generate_cloud_connector_catalog(tmp_path)
    cloud_availability_updater.subprocess.check_output.assert_called_once_with(
        f"cd {tmp_path} && ./gradlew :cloud-config:cloud-config-seed:generateCloudConnectorCatalog", shell=True
    )
    assert result == cloud_availability_updater.subprocess.check_output.return_value.decode.return_value


@pytest.mark.parametrize("response, expected_output", [([], False), (["foo"], True)])
def test_pr_already_created_for_branch(mocker, response, expected_output):
    mocker.patch.object(cloud_availability_updater, "requests")

    cloud_availability_updater.requests.get.return_value = mocker.Mock(json=mocker.Mock(return_value=response))
    output = cloud_availability_updater.pr_already_created_for_branch("foo")
    assert output == expected_output
    cloud_availability_updater.requests.get.return_value.raise_for_status.assert_called_once()
    cloud_availability_updater.requests.get.assert_called_with(
        cloud_availability_updater.AIRBYTE_PLATFORM_INTERNAL_PR_ENDPOINT,
        headers=cloud_availability_updater.GITHUB_API_COMMON_HEADERS,
        params={"head": f"{cloud_availability_updater.AIRBYTE_PLATFORM_INTERNAL_REPO_OWNER}:foo", "state": "open"},
    )


def test_add_labels_to_pr(mocker):
    mocker.patch.object(cloud_availability_updater, "requests")
    labels_to_add = ["foo", "bar"]
    response = cloud_availability_updater.add_labels_to_pr("1", labels_to_add)
    cloud_availability_updater.requests.post.assert_called_with(
        f"{cloud_availability_updater.AIRBYTE_PLATFORM_INTERNAL_ISSUES_ENDPOINT}/1/labels",
        headers=cloud_availability_updater.GITHUB_API_COMMON_HEADERS,
        json={"labels": labels_to_add},
    )
    cloud_availability_updater.requests.post.return_value.raise_for_status.assert_called_once()
    assert response == cloud_availability_updater.requests.post.return_value


def test_get_pr_body(mocker):
    eligible_connectors = [
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

    excluded_connectors = [
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

    pr_body = cloud_availability_updater.get_pr_body(eligible_connectors, excluded_connectors)
    assert "1 connectors available on Cloud!" in pr_body.split("/n")[0]
    assert "# Promoted connectors\n" in pr_body
    assert "# Excluded but eligible connectors\n" in pr_body
    assert "connector_technical_name" in pr_body
    assert "connector_version" in pr_body
    assert "connector_definition_id" in pr_body
    assert "sync_success_rate" in pr_body
    assert "number_of_connections" in pr_body
    assert "source-pokeapi" in pr_body
    assert "pokeapi-definition-id" in pr_body
    assert "0.0.0" in pr_body
    assert "0.99" in pr_body
    assert "source-excluded" in pr_body
    assert "excluded-definition-id" in pr_body
    assert "0.98" in pr_body


@freezegun.freeze_time("2023-02-14")
@pytest.mark.parametrize("added_connectors", [True, False])
def test_batch_deploy_eligible_connectors_to_cloud_repo(mocker, tmp_path, added_connectors):
    mocker.patch.object(cloud_availability_updater.tempfile, "mkdtemp", mocker.Mock(return_value=str(tmp_path)))
    mocker.patch.object(cloud_availability_updater, "clone_airbyte_cloud_repo")
    mocker.patch.object(cloud_availability_updater, "set_git_identity")
    mocker.patch.object(cloud_availability_updater, "checkout_new_branch")
    mocker.patch.object(cloud_availability_updater, "add_new_connector_to_cloud_catalog")
    mocker.patch.object(cloud_availability_updater, "push_branch")
    mocker.patch.object(cloud_availability_updater, "get_pr_body")
    mocker.patch.object(cloud_availability_updater, "create_pr")
    mocker.patch.object(cloud_availability_updater, "shutil")

    eligible_connectors = [mocker.Mock(should_be_added=True), mocker.Mock(should_be_added=True), mocker.Mock(should_be_added=False)]
    if added_connectors:
        cloud_availability_updater.add_new_connector_to_cloud_catalog.side_effect = [
            connector.should_be_added for connector in eligible_connectors
        ]
        expected_added_connectors = eligible_connectors[:2]
    else:
        cloud_availability_updater.add_new_connector_to_cloud_catalog.return_value = False

    expected_excluded_connectors = eligible_connectors[-1:]
    mock_repo = cloud_availability_updater.set_git_identity.return_value
    expected_new_branch_name = "cloud-availability-updater/batch-deploy/20230214"
    expected_pr_title = "🤖 Cloud Availability updater: new connectors to deploy [20230214]"

    cloud_availability_updater.batch_deploy_eligible_connectors_to_cloud_repo(eligible_connectors)
    cloud_availability_updater.clone_airbyte_cloud_repo.assert_called_once_with(tmp_path)
    cloud_availability_updater.set_git_identity.assert_called_once_with(cloud_availability_updater.clone_airbyte_cloud_repo.return_value)
    mock_repo.git.checkout.assert_called_with(cloud_availability_updater.AIRBYTE_PLATFORM_INTERNAL_MAIN_BRANCH_NAME)

    cloud_availability_updater.checkout_new_branch.assert_called_once_with(mock_repo, expected_new_branch_name)
    cloud_availability_updater.add_new_connector_to_cloud_catalog.assert_has_calls(
        [
            mocker.call(tmp_path, cloud_availability_updater.set_git_identity.return_value, eligible_connectors[0]),
            mocker.call(tmp_path, cloud_availability_updater.set_git_identity.return_value, eligible_connectors[1]),
            mocker.call(tmp_path, cloud_availability_updater.set_git_identity.return_value, eligible_connectors[2]),
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
    cloud_availability_updater.shutil.rmtree.assert_called_with(tmp_path)
