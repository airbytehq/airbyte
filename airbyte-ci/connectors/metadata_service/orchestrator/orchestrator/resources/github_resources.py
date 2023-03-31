from typing import List
from dagster import StringSource, InitResourceContext, resource
from github import Github, Repository, ContentFile


@resource
def github_client() -> Github:
    return Github()


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
