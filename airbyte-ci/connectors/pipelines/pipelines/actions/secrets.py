#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This modules groups functions made to download/upload secrets from/to a remote secret service and provide these secret in a dagger Directory."""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from dagger import Secret
from pipelines.actions import environments
from pipelines.utils import get_file_contents, get_secret_host_variable

if TYPE_CHECKING:
    from dagger import Container
    from pipelines.contexts import ConnectorContext


async def get_secrets_to_mask(ci_credentials_with_downloaded_secrets: Container) -> list[str]:
    """This function will print the secrets to mask in the GitHub actions logs with the ::add-mask:: prefix.
    We're not doing it directly from the ci_credentials tool because its stdout is wrapped around the dagger logger,
    And GHA will only interpret lines starting with ::add-mask:: as secrets to mask.
    """
    secrets_to_mask = []
    if secrets_to_mask_file := await get_file_contents(ci_credentials_with_downloaded_secrets, "/tmp/secrets_to_mask.txt"):
        for secret_to_mask in secrets_to_mask_file.splitlines():
            # We print directly to stdout because the GHA runner will mask only if the log line starts with "::add-mask::"
            # If we use the dagger logger, or context logger, the log line will start with other stuff and will not be masked
            print(f"::add-mask::{secret_to_mask}")
            secrets_to_mask.append(secret_to_mask)
    return secrets_to_mask


async def download(context: ConnectorContext, gcp_gsm_env_variable_name: str = "GCP_GSM_CREDENTIALS") -> dict[str, Secret]:
    """Use the ci-credentials tool to download the secrets stored for a specific connector to a Directory.

    Args:
        context (ConnectorContext): The context providing a connector object.
        gcp_gsm_env_variable_name (str, optional): The name of the environment variable holding credentials to connect to Google Secret Manager. Defaults to "GCP_GSM_CREDENTIALS".

    Returns:
        Directory: A directory with the downloaded secrets.
    """
    gsm_secret = get_secret_host_variable(context.dagger_client, gcp_gsm_env_variable_name)
    secrets_path = f"/{context.connector.code_directory}/secrets"
    ci_credentials = await environments.with_ci_credentials(context, gsm_secret)
    with_downloaded_secrets = (
        ci_credentials.with_exec(["mkdir", "-p", secrets_path])
        .with_env_variable(
            "CACHEBUSTER", datetime.datetime.now().isoformat()
        )  # Secrets can be updated on GSM anytime, we can't cache this step...
        .with_exec(["ci_credentials", context.connector.technical_name, "write-to-storage"])
    )
    # We don't want to print secrets in the logs when running locally.
    if context.is_ci:
        context.secrets_to_mask = await get_secrets_to_mask(with_downloaded_secrets)
    connector_secrets = {}
    for secret_file in await with_downloaded_secrets.directory(secrets_path).entries():
        secret_plaintext = await with_downloaded_secrets.directory(secrets_path).file(secret_file).contents()
        # We have to namespace secrets as Dagger derives session wide secret ID from their name
        unique_secret_name = f"{context.connector.technical_name}_{secret_file}"
        connector_secrets[secret_file] = context.dagger_client.set_secret(unique_secret_name, secret_plaintext)

    return connector_secrets


async def upload(context: ConnectorContext, gcp_gsm_env_variable_name: str = "GCP_GSM_CREDENTIALS"):
    """Use the ci-credentials tool to upload the secrets stored in the context's updated_secrets-dir.

    Args:
        context (ConnectorContext): The context providing a connector object and the update secrets dir.
        gcp_gsm_env_variable_name (str, optional): The name of the environment variable holding credentials to connect to Google Secret Manager. Defaults to "GCP_GSM_CREDENTIALS".

    Returns:
        container (Container): The executed ci-credentials update-secrets command.

    Raises:
        ExecError: If the command returns a non-zero exit code.
    """
    gsm_secret = get_secret_host_variable(context.dagger_client, gcp_gsm_env_variable_name)
    secrets_path = f"/{context.connector.code_directory}/secrets"

    ci_credentials = await environments.with_ci_credentials(context, gsm_secret)

    return await ci_credentials.with_directory(secrets_path, context.updated_secrets_dir).with_exec(
        ["ci_credentials", context.connector.technical_name, "update-secrets"]
    )


async def get_connector_secrets(context: ConnectorContext) -> dict[str, Secret]:
    """Download the secrets from GSM or use the local secrets directory for a connector.

    Args:
        context (ConnectorContext): The context providing the connector directory and the use_remote_secrets flag.

    Returns:
        Directory: A directory with the downloaded connector secrets.
    """
    if context.use_remote_secrets:
        connector_secrets = await download(context)
    else:
        raise NotImplementedError("Local secrets are not implemented yet. See https://github.com/airbytehq/airbyte/issues/25621")
    return connector_secrets
