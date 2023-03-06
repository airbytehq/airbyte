#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime

from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.pipelines.contexts import ConnectorTestContext
from ci_connector_ops.utils import Connector
from dagger import Directory


async def download(context: ConnectorTestContext, gcp_gsm_env_variable_name: str = "GCP_GSM_CREDENTIALS") -> Directory:
    gsm_secret = context.dagger_client.host().env_variable(gcp_gsm_env_variable_name).secret()
    secrets_path = "/" + str(context.connector.code_directory) + "/secrets"

    ci_credentials = await environments.with_ci_credentials(context, gsm_secret)
    return (
        ci_credentials.with_exec(["mkdir", "-p", secrets_path])
        .with_env_variable(
            "CACHEBUSTER", datetime.datetime.now().isoformat()
        )  # Secrets can be updated on GSM anytime, we can't cache this step...
        .with_exec(["ci_credentials", context.connector.technical_name, "write-to-storage"])
        .directory(secrets_path)
    )


async def upload(
    context: ConnectorTestContext, connector: Connector, secrets_dir: Directory, gcp_gsm_env_variable_name: str = "GCP_GSM_CREDENTIALS"
) -> int:
    gsm_secret = context.dagger_client.host().env_variable(gcp_gsm_env_variable_name).secret()
    secrets_path = "/" + str(connector.code_directory) + "/secrets"

    ci_credentials = await environments.with_ci_credentials(context, gsm_secret)

    return await (
        ci_credentials.with_directory(secrets_path, secrets_dir)
        .with_exec(["ci_credentials", connector.technical_name, "update-secrets"])
        .exit_code()
    )


async def get_connector_secret_dir(context: ConnectorTestContext) -> Directory:
    if context.use_remote_secrets:
        secrets_dir = await download(context)
    else:
        secrets_dir = context.get_connector_dir(include=["secrets"]).directory("secrets")
    return secrets_dir


async def upload_update_secrets(context: ConnectorTestContext) -> int:
    if context.use_remote_secrets and context.updated_secrets_dir is not None:
        return (
            await upload(
                context.dagger_client.pipeline(f"Teardown {context.connector.technical_name}"),
                context.connector,
                context.updated_secrets_dir,
            )
            == 0
        )
    else:
        return 1
