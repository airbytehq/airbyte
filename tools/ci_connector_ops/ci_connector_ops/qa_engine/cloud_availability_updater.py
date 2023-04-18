#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

import git
import requests
from pytablewriter import MarkdownTableWriter

from .constants import (
    AIRBYTE_PLATFORM_INTERNAL_GITHUB_REPO_URL,
    AIRBYTE_PLATFORM_INTERNAL_ISSUES_ENDPOINT,
    AIRBYTE_PLATFORM_INTERNAL_MAIN_BRANCH_NAME,
    AIRBYTE_PLATFORM_INTERNAL_PR_ENDPOINT,
    AIRBYTE_PLATFORM_INTERNAL_REPO_OWNER,
    GIT_USER_EMAIL,
    GIT_USERNAME,
    GIT_USERNAME_FOR_AUTH,
    GITHUB_API_COMMON_HEADERS,
    GITHUB_API_TOKEN,
    PR_LABELS,
)
from .models import ConnectorQAReport

logger = logging.getLogger(__name__)


def set_git_identity(repo: git.repo) -> git.repo:
    repo.git.config("--global", "user.email", GIT_USER_EMAIL)
    repo.git.config("--global", "user.name", GIT_USERNAME)
    return repo


def get_authenticated_repo_url(git_username: str, github_api_token: str) -> str:
    return AIRBYTE_PLATFORM_INTERNAL_GITHUB_REPO_URL.replace("https://", f"https://{git_username}:{github_api_token}@")


def clone_airbyte_cloud_repo(local_repo_path: Path) -> git.Repo:
    logger.info(f"Cloning {AIRBYTE_PLATFORM_INTERNAL_GITHUB_REPO_URL} to {local_repo_path}")
    authenticated_repo_url = get_authenticated_repo_url(GIT_USERNAME_FOR_AUTH, GITHUB_API_TOKEN)
    return git.Repo.clone_from(authenticated_repo_url, local_repo_path, branch=AIRBYTE_PLATFORM_INTERNAL_MAIN_BRANCH_NAME)


def get_definitions_mask_path(local_repo_path, definition_type: str) -> Path:
    definitions_mask_path = (
        local_repo_path / f"cloud-config/cloud-config-seed/src/main/resources/seed/{definition_type}_definitions_mask.yaml"
    )
    if not definitions_mask_path.exists():
        raise FileNotFoundError(f"Can't find the {definition_type} definitions mask")
    return definitions_mask_path


def checkout_new_branch(airbyte_cloud_repo: git.Repo, new_branch_name: str) -> git.Head:
    new_branch = airbyte_cloud_repo.create_head(new_branch_name)
    new_branch.checkout()
    logger.info(f"Checked out branch {new_branch_name}.")
    return new_branch


def update_definitions_mask(connector: ConnectorQAReport, definitions_mask_path: Path) -> Optional[Path]:
    with open(definitions_mask_path, "r") as definition_mask:
        connector_already_in_mask = connector.connector_definition_id in definition_mask.read()
    if connector_already_in_mask:
        logger.warning(f"{connector.connector_name}'s definition id is already in {definitions_mask_path}.")
        return None

    to_append = f"""# {connector.connector_name} (from cloud availability updater)
- {connector.connector_type}DefinitionId: {connector.connector_definition_id}
"""

    with open(definitions_mask_path, "a") as f:
        f.write(to_append)
    logger.info(f"Updated {definitions_mask_path} with {connector.connector_name}'s definition id.")
    return definitions_mask_path


def run_generate_cloud_connector_catalog(airbyte_cloud_repo_path: Path) -> str:
    result = subprocess.check_output(
        f"cd {airbyte_cloud_repo_path} && ./gradlew :cloud-config:cloud-config-seed:generateCloudConnectorCatalog", shell=True
    )
    logger.info("Ran generateCloudConnectorCatalog Gradle Task")
    return result.decode()


def commit_all_files(airbyte_cloud_repo: git.Repo, commit_message: str):
    airbyte_cloud_repo.git.add("--all")
    airbyte_cloud_repo.git.commit(m=commit_message)
    logger.info("Committed file changes.")


def push_branch(airbyte_cloud_repo: git.Repo, branch: str):
    airbyte_cloud_repo.git.push("--force", "--set-upstream", "origin", branch)
    logger.info(f"Pushed branch {branch} to origin")


def pr_already_created_for_branch(head_branch: str) -> bool:
    response = requests.get(
        AIRBYTE_PLATFORM_INTERNAL_PR_ENDPOINT,
        headers=GITHUB_API_COMMON_HEADERS,
        params={"head": f"{AIRBYTE_PLATFORM_INTERNAL_REPO_OWNER}:{head_branch}", "state": "open"},
    )
    response.raise_for_status()
    return len(response.json()) > 0


def add_labels_to_pr(pr_number: str, labels_to_add: List) -> requests.Response:
    url = AIRBYTE_PLATFORM_INTERNAL_ISSUES_ENDPOINT + f"/{pr_number}/labels"
    response = requests.post(url, headers=GITHUB_API_COMMON_HEADERS, json={"labels": labels_to_add})
    response.raise_for_status()
    logger.info(f"Labels {labels_to_add} added to PR {pr_number}")
    return response


def create_pr(pr_title: str, pr_body: str, branch: str, labels: Optional[List]) -> Optional[requests.Response]:
    data = {
        "title": pr_title,
        "body": pr_body,
        "head": branch,
        "base": AIRBYTE_PLATFORM_INTERNAL_MAIN_BRANCH_NAME,
    }
    if not pr_already_created_for_branch(branch):
        response = requests.post(AIRBYTE_PLATFORM_INTERNAL_PR_ENDPOINT, headers=GITHUB_API_COMMON_HEADERS, json=data)
        response.raise_for_status()
        pr_url = response.json().get("url")
        pr_number = response.json().get("number")
        logger.info(f"A PR was opened: {pr_url}")
        if labels:
            add_labels_to_pr(pr_number, labels)
        return response
    else:
        logger.warning(f"A PR already exists for branch {branch}")


def get_pr_body(eligible_connectors: List[ConnectorQAReport], excluded_connectors: List[ConnectorQAReport]) -> str:
    body = (
        f"The Cloud Availability Updater decided that it's the right time to make the following {len(eligible_connectors)} connectors available on Cloud!"
        + "\n\n"
    )
    headers = ["connector_technical_name", "connector_version", "connector_definition_id", "sync_success_rate", "number_of_connections"]

    writer = MarkdownTableWriter(
        max_precision=2,
        table_name="Promoted connectors",
        headers=headers,
        value_matrix=[[connector.dict()[h] for h in headers] for connector in eligible_connectors],
    )
    body += writer.dumps()
    body += "\n"

    writer = MarkdownTableWriter(
        table_name="Excluded but eligible connectors",
        max_precision=2,
        headers=headers,
        value_matrix=[[connector.dict()[h] for h in headers] for connector in excluded_connectors],
    )

    body += writer.dumps()
    body += "\n ☝️ These eligible connectors are already in the definitions masks. They might have been explicitly pinned or excluded. We're not adding these for safety."
    return body


def add_new_connector_to_cloud_catalog(airbyte_cloud_repo_path: Path, airbyte_cloud_repo: git.Repo, connector: ConnectorQAReport) -> bool:
    """Updates the local definitions mask on Airbyte cloud repo.
    Calls the generateCloudConnectorCatalog gradle task.
    Commits these changes

    Args:
        airbyte_cloud_repo_path (Path): The local path to Airbyte Cloud repository.
        airbyte_cloud_repo (git.Repo): The Airbyte Cloud repo instance.
        connector (ConnectorQAReport): The connector to add to a definitions mask.
    Returns:
        bool: Whether the connector was added or not.
    """
    definitions_mask_path = get_definitions_mask_path(airbyte_cloud_repo_path, connector.connector_type)
    updated_files = update_definitions_mask(connector, definitions_mask_path)
    if updated_files:
        run_generate_cloud_connector_catalog(airbyte_cloud_repo_path)
        commit_all_files(airbyte_cloud_repo, f"🤖 Add {connector.connector_name} connector to cloud")
        return True
    return False


def batch_deploy_eligible_connectors_to_cloud_repo(eligible_connectors: Iterable):
    cloud_repo_path = Path(tempfile.mkdtemp())
    airbyte_cloud_repo = clone_airbyte_cloud_repo(cloud_repo_path)
    airbyte_cloud_repo = set_git_identity(airbyte_cloud_repo)
    current_date = datetime.utcnow().strftime("%Y%m%d")
    airbyte_cloud_repo.git.checkout(AIRBYTE_PLATFORM_INTERNAL_MAIN_BRANCH_NAME)

    new_branch_name = f"cloud-availability-updater/batch-deploy/{current_date}"
    checkout_new_branch(airbyte_cloud_repo, new_branch_name)

    added_connectors = []
    explicitly_disabled_connectors = []
    for connector in eligible_connectors:
        added = add_new_connector_to_cloud_catalog(cloud_repo_path, airbyte_cloud_repo, connector)
        if added:
            added_connectors.append(connector)
        else:
            explicitly_disabled_connectors.append(connector)
    if added_connectors:
        push_branch(airbyte_cloud_repo, new_branch_name)
        create_pr(
            f"🤖 Cloud Availability updater: new connectors to deploy [{current_date}]",
            get_pr_body(added_connectors, explicitly_disabled_connectors),
            new_branch_name,
            PR_LABELS,
        )
    shutil.rmtree(cloud_repo_path)
