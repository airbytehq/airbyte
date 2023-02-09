#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, Optional

import git
import requests

from .constants import (
    AIRBYTE_PLATFORM_INTERNAL_GITHUB_REPO_URL,
    AIRBYTE_PLATFORM_INTERNAL_MAIN_BRANCH_NAME,
    AIRBYTE_PLATFORM_INTERNAL_PR_ENDPOINT,
    AIRBYTE_PLATFORM_INTERNAL_REPO_OWNER,
    GITHUB_API_COMMON_HEADERS,
)
from .models import ConnectorQAReport

logger = logging.getLogger(__name__)


def clone_airbyte_cloud_repo(local_repo_path: Path) -> git.Repo:
    logger.info(f"Cloning {AIRBYTE_PLATFORM_INTERNAL_GITHUB_REPO_URL} to {local_repo_path}")
    return git.Repo.clone_from(
        AIRBYTE_PLATFORM_INTERNAL_GITHUB_REPO_URL, local_repo_path, branch=AIRBYTE_PLATFORM_INTERNAL_MAIN_BRANCH_NAME
    )


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


def create_pr(connector: ConnectorQAReport, branch: str) -> Optional[requests.Response]:
    body = f"""The Cloud Availability Updater decided that it's the right time to make {connector.connector_name} available on Cloud!
    - Technical name: {connector.connector_technical_name}
    - Version: {connector.connector_version}
    - Definition ID: {connector.connector_definition_id}
    - OSS sync success rate: {connector.sync_success_rate}
    - OSS number of connections: {connector.number_of_connections}
    """
    data = {
        "title": f"🤖 Add {connector.connector_technical_name} to cloud",
        "body": body,
        "head": branch,
        "base": AIRBYTE_PLATFORM_INTERNAL_MAIN_BRANCH_NAME,
    }
    if not pr_already_created_for_branch(branch):
        response = requests.post(AIRBYTE_PLATFORM_INTERNAL_PR_ENDPOINT, headers=GITHUB_API_COMMON_HEADERS, json=data)
        response.raise_for_status()
        pr_url = response.json().get("url")
        logger.info(f"A PR was opened for {connector.connector_technical_name}: {pr_url}")
        return response
    else:
        logger.warning(f"A PR already exists for branch {branch}")


def deploy_new_connector_to_cloud_repo(airbyte_cloud_repo_path: Path, airbyte_cloud_repo: git.Repo, connector: ConnectorQAReport):
    """Updates the local definitions mask on Airbyte cloud repo.
    Calls the generateCloudConnectorCatalog gradle task.
    Commits these changes on a new branch.
    Pushes these new branch to the origin.

    Args:
        airbyte_cloud_repo_path (Path): The local path to Airbyte Cloud repository.
        airbyte_cloud_repo (git.Repo): The Airbyte Cloud repo instance.
        connector (ConnectorQAReport): The connector to add to a definitions mask.
    """
    airbyte_cloud_repo.git.checkout(AIRBYTE_PLATFORM_INTERNAL_MAIN_BRANCH_NAME)
    new_branch_name = f"cloud-availability-updater/deploy-{connector.connector_technical_name}"
    checkout_new_branch(airbyte_cloud_repo, new_branch_name)
    definitions_mask_path = get_definitions_mask_path(airbyte_cloud_repo_path, connector.connector_type)
    updated_files = update_definitions_mask(connector, definitions_mask_path)
    if updated_files:
        run_generate_cloud_connector_catalog(airbyte_cloud_repo_path)
        commit_all_files(airbyte_cloud_repo, f"🤖 Add {connector.connector_name} connector to cloud")
        push_branch(airbyte_cloud_repo, new_branch_name)
        create_pr(connector, new_branch_name)
        airbyte_cloud_repo.git.checkout(AIRBYTE_PLATFORM_INTERNAL_MAIN_BRANCH_NAME)


def deploy_eligible_connectors_to_cloud_repo(eligible_connectors: Iterable):
    cloud_repo_path = Path(tempfile.mkdtemp())
    airbyte_cloud_repo = clone_airbyte_cloud_repo(cloud_repo_path)
    for connector in eligible_connectors:
        deploy_new_connector_to_cloud_repo(cloud_repo_path, airbyte_cloud_repo, connector)
    shutil.rmtree(cloud_repo_path)
