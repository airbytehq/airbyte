#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

REQUIREMENTS = [
    "pip==21.3.1",
    "mccabe==0.6.1",
    "flake8==4.0.1",
    "pyproject-flake8==0.0.1a2",
    "black==22.3.0",
    "isort==5.6.4",
    "pytest==6.2.5",
    "coverage[toml]==6.3.1",
]


def get_connector_source_mount_args(client, connector_name):
    host_path = f"airbyte-integrations/connectors/{connector_name}"
    return "/" + host_path, client.host().directory(host_path, exclude=[".venv"])


def get_connector_acceptance_test_source_mount_args(client):
    host_path = "airbyte-integrations/bases/connector-acceptance-test"
    return "/" + host_path, client.host().directory(host_path, exclude=[".venv"])


def get_connector_builder(client, connector_name):
    connector_builder = client.container().from_("python:3.9-slim")
    for requirement in REQUIREMENTS:
        connector_builder = connector_builder.with_exec(["pip", "install", requirement])
    workdir, connector_source_host_path = get_connector_source_mount_args(client, connector_name)
    connector_builder = connector_builder.with_mounted_directory(workdir, connector_source_host_path)
    connector_builder = connector_builder.with_mounted_directory(*get_connector_acceptance_test_source_mount_args(client))
    return connector_builder.with_workdir(workdir)
