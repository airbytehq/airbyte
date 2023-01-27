#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import os
import logging
from pathlib import Path
import subprocess
from typing import Iterable, Optional

import git
from github import Github

from .models import ConnectorQAReport

logging.basicConfig(level="INFO")

AIRBYTE_CLOUD_REPO_PATH = Path(os.environ["AIRBYTE_CLOUD_REPO_PATH"])
GITHUB_ACCESS_TOKEN = os.environ["GITHUB_ACCESS_TOKEN"]
AIRBYTE_CLOUD_REPO = git.Repo(AIRBYTE_CLOUD_REPO_PATH)
PATH_TO_DEFINITIONS_MASKS = {
    "source": AIRBYTE_CLOUD_REPO_PATH / "cloud-config/cloud-config-seed/src/main/resources/seed/source_definitions_mask.yaml",
    "destination": AIRBYTE_CLOUD_REPO_PATH / "cloud-config/cloud-config-seed/src/main/resources/seed/destination_definitions_mask.yaml"
}

def checkout_new_branch(connector: ConnectorQAReport) -> git.Head:
    new_branch_name = f"cloud-availability-updater/{connector.connector_technical_name}-to-cloud"
    new_branch = AIRBYTE_CLOUD_REPO.create_head(new_branch_name)
    new_branch.checkout()
    logging.info(f"Checked out branch {new_branch_name}.")
    return new_branch

def update_definition_mask(connector: ConnectorQAReport) -> Optional[Path]:
    definition_mask_path = PATH_TO_DEFINITIONS_MASKS[connector.connector_type]
    with open(definition_mask_path, "r") as definition_mask:
        connector_already_in_mask = connector.connector_definition_id in definition_mask.read()
    if connector_already_in_mask:
        logging.warning(f"{connector.connector_name}'s definition id is already in {definition_mask_path}.")
        return None

    to_append = f"""# {connector.connector_name} (from cloud availability updater)
- {connector.connector_type}DefinitionId: {connector.connector_definition_id}
"""

    with open(definition_mask_path, "a") as f:
        f.write(to_append)
    logging.info(f"Updated {definition_mask_path} with {connector.connector_name}'s definition id.")
    return definition_mask_path

def run_generate_cloud_connector_catalog() -> str:
    result = subprocess.check_output(
        f"cd {AIRBYTE_CLOUD_REPO_PATH} && ./gradlew :cloud-config:cloud-config-seed:generateCloudConnectorCatalog", 
        shell=True
        )
    logging.info("Ran generateCloudConnectorCatalog Gradle Task")
    return result.decode()

def commit_files(connector: ConnectorQAReport):
    AIRBYTE_CLOUD_REPO.git.add('--all')
    AIRBYTE_CLOUD_REPO.git.commit(m=f"🤖 Add {connector.connector_technical_name} to cloud")
    logging.info(f"Committed file changes.")

def push_branch(branch, dry_run=True):
    if not dry_run:
        AIRBYTE_CLOUD_REPO.git.push("--set-upstream", "origin", branch)
        logging.info(f"Pushed branch {branch} to origin")

def create_pr(connector: ConnectorQAReport, branch: str, dry_run=True):
    g = Github(GITHUB_ACCESS_TOKEN)

    repo = g.get_repo("airbytehq/airbyte-cloud")
    body = f"""
    The Cloud Availability Updater decided that it's the right time to make {connector.connector_name} available on Cloud!
    ```
    {connector}
    ```
    """
    if not dry_run:
        return repo.create_pull(title=f"🤖 Add {connector.connector_technical_name} to cloud", body=body, head=branch, base="master")
    
def deploy_eligible_connector(connector: ConnectorQAReport, dry_run=True):
    AIRBYTE_CLOUD_REPO.heads.master.checkout()
    new_branch = checkout_new_branch(connector)
    update_definition_mask(connector)
    run_generate_cloud_connector_catalog()
    commit_files(connector)
    push_branch(new_branch, dry_run=dry_run)
    create_pr(connector, new_branch, dry_run=dry_run)

def deploy_eligible_connectors(connectors_eligible_for_cloud: Iterable[ConnectorQAReport]):
    for connector in connectors_eligible_for_cloud:
        deploy_eligible_connector(connector)
    AIRBYTE_CLOUD_REPO.heads.master.checkout()