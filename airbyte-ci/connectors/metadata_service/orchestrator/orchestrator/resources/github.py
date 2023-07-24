from typing import List
from dagster import StringSource, InitResourceContext, resource
from github import Github, Repository, ContentFile
from datetime import datetime, timedelta


@resource(
    config_schema={"github_token": StringSource},
)
def github_client(resource_context: InitResourceContext) -> Github:
    github_token = resource_context.resource_config["github_token"]
    return Github(github_token)


@resource(
    required_resource_keys={"github_client"},
    config_schema={"connector_repo_name": StringSource},
)
def github_connector_repo(resource_context: InitResourceContext) -> Repository:
    connector_repo_name = resource_context.resource_config["connector_repo_name"]
    resource_context.log.info(f"retrieving repo instance for {connector_repo_name}")

    github_client = resource_context.resources.github_client
    return github_client.get_repo(connector_repo_name)


@resource(
    required_resource_keys={"github_connector_repo"},
    config_schema={"connectors_path": StringSource},
)
def github_connectors_directory(resource_context: InitResourceContext) -> List[ContentFile.ContentFile]:
    connectors_path = resource_context.resource_config["connectors_path"]
    resource_context.log.info(f"retrieving github contents of {connectors_path}")

    github_connector_repo = resource_context.resources.github_connector_repo
    return github_connector_repo.get_contents(connectors_path)


@resource(
    required_resource_keys={"github_connector_repo"},
    config_schema={
        "workflow_id": StringSource,
        "branch": StringSource,
        "status": StringSource,
    },
)
def github_workflow_runs(resource_context: InitResourceContext) -> List[ContentFile.ContentFile]:
    MAX_DAYS_LOOK_BACK = 3
    max_look_back_date = (datetime.now() - timedelta(days=MAX_DAYS_LOOK_BACK)).isoformat()

    workflow_id = resource_context.resource_config["workflow_id"]
    branch = resource_context.resource_config["branch"]
    status = resource_context.resource_config["status"]

    github_connector_repo = resource_context.resources.github_connector_repo

    resource_context.log.info(f"retrieving github workflow runs for {workflow_id} on {branch} with status {status}")

    params = {"status": status, "branch": branch, "created": f">{max_look_back_date}"}

    # Make a request to the /actions/workflows/{workflow_id}/runs endpoint
    # Note: We must do this as pygithub does not support all required
    #       parameters for this endpoint
    status, data = github_connector_repo._requester.requestJsonAndCheck(
        "GET", f"{github_connector_repo.url}/actions/workflows/{workflow_id}/runs", parameters=params
    )

    workflow_runs = data.get("workflow_runs", [])

    return workflow_runs
