#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import os
import logging
from pathlib import Path
import subprocess
from typing import Optional

import git

from .models import ConnectorQAReport
from .constants import (
    AIRBYTE_CLOUD_GITHUB_REPO_URL, 
    AIRBYTE_CLOUD_MAIN_BRANCH_NAME
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def clone_airbyte_cloud_repo(local_repo_path: Path) -> git.Repo:
    logging.info(f"Cloning {AIRBYTE_CLOUD_GITHUB_REPO_URL} to {local_repo_path}")
    return git.Repo.clone_from(AIRBYTE_CLOUD_GITHUB_REPO_URL, local_repo_path, branch=AIRBYTE_CLOUD_MAIN_BRANCH_NAME)

def get_definitions_mask_path(local_repo_path, definition_type: str) -> Path:
    definitions_mask_path = local_repo_path / f"cloud-config/cloud-config-seed/src/main/resources/seed/{definition_type}_definitions_mask.yaml"
    if not definitions_mask_path.exists():
        raise FileNotFoundError(f"Can't find the {definition_type} definitions mask")
    return definitions_mask_path

def checkout_new_branch(airbyte_cloud_repo: git.Repo, new_branch_name: str) -> git.Head:
    new_branch = airbyte_cloud_repo.create_head(new_branch_name)
    new_branch.checkout()
    logging.info(f"Checked out branch {new_branch_name}.")
    return new_branch

def update_definitions_mask(connector: ConnectorQAReport, definitions_mask_path: Path) -> Optional[Path]:
    with open(definitions_mask_path, "r") as definition_mask:
        connector_already_in_mask = connector.connector_definition_id in definition_mask.read()
    if connector_already_in_mask:
        logging.warning(f"{connector.connector_name}'s definition id is already in {definitions_mask_path}.")
        return None

    to_append = f"""# {connector.connector_name} (from cloud availability updater)
- {connector.connector_type}DefinitionId: {connector.connector_definition_id}
"""

    with open(definitions_mask_path, "a") as f:
        f.write(to_append)
    logging.info(f"Updated {definitions_mask_path} with {connector.connector_name}'s definition id.")
    return definitions_mask_path

def run_generate_cloud_connector_catalog(airbyte_cloud_repo_path: Path) -> str:
    result = subprocess.check_output(
        f"cd {airbyte_cloud_repo_path} && ./gradlew :cloud-config:cloud-config-seed:generateCloudConnectorCatalog", 
        shell=True
        )
    logging.info("Ran generateCloudConnectorCatalog Gradle Task")
    return result.decode()

def commit_all_files(airbyte_cloud_repo: git.Repo, commit_message: str):
    airbyte_cloud_repo.git.add('--all')
    airbyte_cloud_repo.git.commit(m=commit_message)
    logging.info(f"Committed file changes.")

def push_branch(airbyte_cloud_repo: git.Repo, branch:str):
    airbyte_cloud_repo.git.push("--set-upstream", "origin", branch)
    logging.info(f"Pushed branch {branch} to origin")

def deploy_new_connector_to_cloud_repo(
    airbyte_cloud_repo_path: Path,
    airbyte_cloud_repo: git.Repo,
    connector: ConnectorQAReport
 ):
    """Updates the local definitions mask on Airbyte cloud repo.
    Calls the generateCloudConnectorCatalog gradle task.
    Commits these changes on a new branch.
    Pushes these new branch to the origin.

    Args:
        airbyte_cloud_repo_path (Path): The local path to Airbyte Cloud repository.
        airbyte_cloud_repo (git.Repo): The Airbyte Cloud repo instance.
        connector (ConnectorQAReport): The connector to add to a definitions mask.
    """
    airbyte_cloud_repo.git.checkout(AIRBYTE_CLOUD_MAIN_BRANCH_NAME)
    new_branch_name = f"cloud-availability-updater/deploy-{connector.connector_technical_name}"
    checkout_new_branch(airbyte_cloud_repo, new_branch_name)
    definitions_mask_path = get_definitions_mask_path(airbyte_cloud_repo_path, connector.connector_type)
    update_definitions_mask(connector, definitions_mask_path)
    run_generate_cloud_connector_catalog(airbyte_cloud_repo_path)
    commit_all_files(
        airbyte_cloud_repo, 
        f"🤖 Add {connector.connector_name} connector to cloud"
    )
    push_branch(airbyte_cloud_repo, new_branch_name)
    airbyte_cloud_repo.git.checkout(AIRBYTE_CLOUD_MAIN_BRANCH_NAME)
