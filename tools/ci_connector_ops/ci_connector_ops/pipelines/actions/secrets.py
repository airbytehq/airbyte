#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This modules groups functions made to download/upload secrets from/to a remote secret service and provide these secret in a dagger Directory."""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import anyio
from ci_connector_ops.pipelines.actions import environments
from dagger import Directory

if TYPE_CHECKING:
    from ci_connector_ops.pipelines.contexts import ConnectorTestContext


async def download(context: ConnectorTestContext, gcp_gsm_env_variable_name: str = "GCP_GSM_CREDENTIALS") -> Directory:
    """Use the ci-credentials tool to download the secrets stored for a specific connector to a Directory.

    Args:
        context (ConnectorTestContext): The context providing a connector object.
        gcp_gsm_env_variable_name (str, optional): The name of the environment variable holding credentials to connect to Google Secret Manager. Defaults to "GCP_GSM_CREDENTIALS".

    Returns:
        Directory: A directory with the downloaded secrets.
    """
    gsm_secret = context.dagger_client.host().env_variable(gcp_gsm_env_variable_name).secret()
    secrets_path = f"/{context.connector.code_directory}/secrets"

    ci_credentials = await environments.with_ci_credentials(context, gsm_secret)
    return (
        ci_credentials.with_exec(["mkdir", "-p", secrets_path])
        .with_env_variable(
            "CACHEBUSTER", datetime.datetime.now().isoformat()
        )  # Secrets can be updated on GSM anytime, we can't cache this step...
        .with_exec(["ci_credentials", context.connector.technical_name, "write-to-storage"])
        .directory(secrets_path)
    )


async def upload(context: ConnectorTestContext, gcp_gsm_env_variable_name: str = "GCP_GSM_CREDENTIALS") -> int:
    """Use the ci-credentials tool to upload the secrets stored in the context's updated_secrets-dir.

    Args:
        context (ConnectorTestContext): The context providing a connector object and the update secrets dir.
        gcp_gsm_env_variable_name (str, optional): The name of the environment variable holding credentials to connect to Google Secret Manager. Defaults to "GCP_GSM_CREDENTIALS".

    Returns:
        int: The exit code of the ci-credentials update-secrets command.
    """
    gsm_secret = context.dagger_client.host().env_variable(gcp_gsm_env_variable_name).secret()
    secrets_path = f"/{context.connector.code_directory}/secrets"

    ci_credentials = await environments.with_ci_credentials(context, gsm_secret)

    return await (
        ci_credentials.with_directory(secrets_path, context.updated_secrets_dir)
        .with_exec(["ci_credentials", context.connector.technical_name, "update-secrets"])
        .exit_code()
    )


async def get_connector_secret_dir(context: ConnectorTestContext) -> Directory:
    """Download the secrets from GSM or use the local secrets directory for a connector.

    Args:
        context (ConnectorTestContext): The context providing the connector directory and the use_remote_secrets flag.

    Returns:
        Directory: A directory with the downloaded connector secrets.
    """
    if context.use_remote_secrets:
        secrets_dir = await download(context)
    else:
        local_secrets_dir = anyio.Path(context.connector.code_directory) / "secrets"
        await local_secrets_dir.mkdir(exist_ok=True)
        secrets_dir = context.get_connector_dir(include=["secrets"]).directory("secrets")
    return secrets_dir
