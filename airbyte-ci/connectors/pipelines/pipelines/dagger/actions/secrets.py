#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This modules groups functions made to download/upload secrets from/to a remote secret service and provide these secret in a dagger Directory."""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Callable

from anyio import Path
from dagger import Secret
from pipelines.helpers.utils import get_file_contents, get_secret_host_variable

if TYPE_CHECKING:
    from dagger import Container
    from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext


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
    # temp - fix circular import
    from pipelines.dagger.containers.internal_tools import with_ci_credentials

    gsm_secret = get_secret_host_variable(context.dagger_client, gcp_gsm_env_variable_name)
    secrets_path = f"/{context.connector.code_directory}/secrets"

    ci_credentials = await with_ci_credentials(context, gsm_secret)

    return await ci_credentials.with_directory(secrets_path, context.updated_secrets_dir).with_exec(
        ["ci_credentials", context.connector.technical_name, "update-secrets"]
    )


async def load_from_local(context: ConnectorContext) -> dict[str, Secret]:
    """Load the secrets from the local secrets directory for a connector.

    Args:
        context (ConnectorContext): The context providing the connector directory.

    Returns:
        dict[str, Secret]: A dict mapping the secret file name to the dagger Secret object.
    """
    connector_secrets = {}
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


async def mounted_connector_secrets(context: PipelineContext, secret_directory_path: str) -> Callable[[Container], Container]:
    # By default, mount the secrets properly as dagger secret files.
    #
    # This will cause the contents of these files to be scrubbed from the logs. This scrubbing comes at the cost of
    # unavoidable latency in the log output, see next paragraph for details as to why. This is fine in a CI environment
    # however this becomes a nuisance locally: the developer wants the logs to be displayed to them in an as timely
    # manner as possible. Since the secrets aren't really secret in that case anyway, we mount them in the container as
    # regular files instead.
    #
    # The buffering behavior that comes into play when logs are scrubbed is both unavoidable and not configurable.
    # It's fundamentally unavoidable because dagger needs to match a bunch of regexes (one per secret) and therefore
    # needs to buffer at least as many bytes as the longest of all possible matches. Still, this isn't that long in
    # practice in our case. The real problem is that the buffering is not configurable: dagger relies on a golang
    # library called transform [1] to perform the regexp matching on a stream and this library hard-codes a buffer
    # size of 4096 bytes for each regex [2].
    #
    # Remove the special local case whenever dagger implements scrubbing differently [3,4].
    #
    # [1] https://golang.org/x/text/transform
    # [2] https://cs.opensource.google/go/x/text/+/refs/tags/v0.13.0:transform/transform.go;l=130
    # [3] https://github.com/dagger/dagger/blob/v0.6.4/cmd/shim/main.go#L294
    # [4] https://github.com/airbytehq/airbyte/issues/30394
    #
    if context.is_local:
        # Special case for local development.
        # Query dagger for the contents of the secrets and mount these strings as files in the container.
        contents = {}
        for secret_file_name, secret in context.connector_secrets.items():
            contents[secret_file_name] = await secret.plaintext()

        def with_secrets_mounted_as_regular_files(container: Container) -> Container:
            container = container.with_exec(["mkdir", "-p", secret_directory_path], skip_entrypoint=True)
            for secret_file_name, secret_content_str in contents.items():
                container = container.with_new_file(f"{secret_directory_path}/{secret_file_name}", secret_content_str, permissions=0o600)
            return container

        return with_secrets_mounted_as_regular_files

    def with_secrets_mounted_as_dagger_secrets(container: Container) -> Container:
        container = container.with_exec(["mkdir", "-p", secret_directory_path], skip_entrypoint=True)
        for secret_file_name, secret in context.connector_secrets.items():
            container = container.with_mounted_secret(f"{secret_directory_path}/{secret_file_name}", secret)
        return container

    return with_secrets_mounted_as_dagger_secrets
