#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This modules groups functions made to download/upload secrets from/to a remote secret service and provide these secret in a dagger Directory."""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from anyio import Path
from dagger import Secret
from pipelines.helpers.utils import get_file_contents, get_secret_host_variable

if TYPE_CHECKING:
    from typing import Callable, Dict

    from dagger import Container
    from pipelines.airbyte_ci.connectors.context import ConnectorContext


# List of overrides for the secrets masking logic.
# These keywords may have been marked as secrets, perhaps somewhat aggressively.
# Masking them, however, is annoying and pointless.
# This list should be extended (carefully) as needed.
NOT_REALLY_SECRETS = {
    "admin",
    "airbyte",
    "host",
}


async def get_secrets_to_mask(ci_credentials_with_downloaded_secrets: Container, connector_technical_name: str) -> list[str]:
    """This function will print the secrets to mask in the GitHub actions logs with the ::add-mask:: prefix.
    We're not doing it directly from the ci_credentials tool because its stdout is wrapped around the dagger logger,
    And GHA will only interpret lines starting with ::add-mask:: as secrets to mask.
    """
    secrets_to_mask = []
    if secrets_to_mask_file := await get_file_contents(ci_credentials_with_downloaded_secrets, "/tmp/secrets_to_mask.txt"):
        for secret_to_mask in secrets_to_mask_file.splitlines():
            if secret_to_mask in NOT_REALLY_SECRETS or secret_to_mask in connector_technical_name:
                # Don't mask secrets which are also common words or connector name.
                continue
            # We print directly to stdout because the GHA runner will mask only if the log line starts with "::add-mask::"
            # If we use the dagger logger, or context logger, the log line will start with other stuff and will not be masked
            print(f"::add-mask::{secret_to_mask}")
            secrets_to_mask.append(secret_to_mask)
    return secrets_to_mask


async def download(context: ConnectorContext, gcp_gsm_env_variable_name: str = "GCP_GSM_CREDENTIALS") -> Dict[str, Secret]:
    """Use the ci-credentials tool to download the secrets stored for a specific connector to a Directory.

    Args:
        context (ConnectorContext): The context providing a connector object.
        gcp_gsm_env_variable_name (str, optional): The name of the environment variable holding credentials to connect to Google Secret Manager. Defaults to "GCP_GSM_CREDENTIALS".

    Returns:
        dict[str, Secret]: A dict mapping the secret file name to the dagger Secret object.
    """
    # temp - fix circular import
    from pipelines.dagger.containers.internal_tools import with_ci_credentials

    gsm_secret = get_secret_host_variable(context.dagger_client, gcp_gsm_env_variable_name)
    secrets_path = f"/{context.connector.code_directory}/secrets"
    ci_credentials = await with_ci_credentials(context, gsm_secret)
    with_downloaded_secrets = (
        ci_credentials.with_exec(["mkdir", "-p", secrets_path])
        .with_env_variable(
            "CACHEBUSTER", datetime.datetime.now().isoformat()
        )  # Secrets can be updated on GSM anytime, we can't cache this step...
        .with_exec(["ci_credentials", context.connector.technical_name, "write-to-storage"])
    )
    # We don't want to print secrets in the logs when running locally.
    if context.is_ci:
        context.secrets_to_mask = await get_secrets_to_mask(with_downloaded_secrets, context.connector.technical_name)
    connector_secrets = {}
    for secret_file in await with_downloaded_secrets.directory(secrets_path).entries():
        secret_plaintext = await with_downloaded_secrets.directory(secrets_path).file(secret_file).contents()
        # We have to namespace secrets as Dagger derives session wide secret ID from their name
        unique_secret_name = f"{context.connector.technical_name}_{secret_file}"
        connector_secrets[secret_file] = context.dagger_client.set_secret(unique_secret_name, secret_plaintext)

    return connector_secrets


async def upload(context: ConnectorContext, gcp_gsm_env_variable_name: str = "GCP_GSM_CREDENTIALS") -> Container:
    """Use the ci-credentials tool to upload the secrets stored in the context's updated_secrets-dir.

    Args:
        context (ConnectorContext): The context providing a connector object and the update secrets dir.
        gcp_gsm_env_variable_name (str, optional): The name of the environment variable holding credentials to connect to Google Secret Manager. Defaults to "GCP_GSM_CREDENTIALS".

    Returns:
        container (Container): The executed ci-credentials update-secrets command.

    Raises:
        ExecError: If the command returns a non-zero exit code.
    """
    assert context.updated_secrets_dir is not None, "The context's updated_secrets_dir must be set to upload secrets."
    # temp - fix circular import
    from pipelines.dagger.containers.internal_tools import with_ci_credentials

    gsm_secret = get_secret_host_variable(context.dagger_client, gcp_gsm_env_variable_name)
    secrets_path = f"/{context.connector.code_directory}/secrets"

    ci_credentials = await with_ci_credentials(context, gsm_secret)

    return await ci_credentials.with_directory(secrets_path, context.updated_secrets_dir).with_exec(
        ["ci_credentials", context.connector.technical_name, "update-secrets"]
    )


async def load_from_local(context: ConnectorContext) -> Dict[str, Secret]:
    """Load the secrets from the local secrets directory for a connector.

    Args:
        context (ConnectorContext): The context providing the connector directory.

    Returns:
        dict[str, Secret]: A dict mapping the secret file name to the dagger Secret object.
    """
    connector_secrets: Dict[str, Secret] = {}
    local_secrets_path = Path(context.connector.code_directory / "secrets")
    if not await local_secrets_path.is_dir():
        context.logger.warning(f"Local secrets directory {local_secrets_path} does not exist, no secrets will be loaded.")
        return connector_secrets
    async for secret_file in local_secrets_path.iterdir():
        secret_plaintext = await secret_file.read_text()
        unique_secret_name = f"{context.connector.technical_name}_{secret_file.name}"
        connector_secrets[secret_file.name] = context.dagger_client.set_secret(unique_secret_name, secret_plaintext)
    if not connector_secrets:
        context.logger.warning(f"Local secrets directory {local_secrets_path} is empty, no secrets will be loaded.")
    return connector_secrets


async def get_connector_secrets(context: ConnectorContext) -> dict[str, Secret]:
    """Download the secrets from GSM or use the local secrets directory for a connector.

    Args:
        context (ConnectorContext): The context providing the connector directory and the use_remote_secrets flag.

    Returns:
        dict[str, Secret]: A dict mapping the secret file name to the dagger Secret object.
    """
    if context.use_remote_secrets:
        connector_secrets = await download(context)
    else:
        connector_secrets = await load_from_local(context)
    return connector_secrets


async def mounted_connector_secrets(context: ConnectorContext, secret_directory_path: str) -> Callable[[Container], Container]:
    """Returns an argument for a dagger container's with_ method which mounts all connector secrets in it.

    Args:
        context (ConnectorContext): The context providing a connector object and its secrets.
        secret_directory_path (str): Container directory where the secrets will be mounted, as files.

    Returns:
        fn (Callable[[Container], Container]): A function to pass as argument to the connector container's with_ method.
    """
    connector_secrets = await context.get_connector_secrets()
    java_log_scrub_pattern_secret = context.java_log_scrub_pattern_secret

    def with_secrets_mounted_as_dagger_secrets(container: Container) -> Container:
        if java_log_scrub_pattern_secret:
            # This LOG_SCRUB_PATTERN environment variable is used by our log4j test configuration
            # to scrub secrets from the log messages. Although we already ensure that github scrubs them
            # from its runner logs, this is required to prevent the secrets from leaking into gradle scans,
            # test reports or any other build artifacts generated by a java connector test.
            container = container.with_secret_variable("LOG_SCRUB_PATTERN", java_log_scrub_pattern_secret)
        container = container.with_exec(["mkdir", "-p", secret_directory_path], skip_entrypoint=True)
        for secret_file_name, secret in connector_secrets.items():
            container = container.with_mounted_secret(f"{secret_directory_path}/{secret_file_name}", secret)
        return container

    return with_secrets_mounted_as_dagger_secrets
