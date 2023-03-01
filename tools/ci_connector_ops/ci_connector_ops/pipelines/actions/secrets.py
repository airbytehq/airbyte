#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import datetime

from ci_connector_ops.pipelines.actions import environments
from ci_connector_ops.utils import Connector
from dagger import Client, Directory


async def download(dagger_client: Client, connector: Connector, gcp_gsm_env_variable_name: str = "GCP_GSM_CREDENTIALS") -> Directory:
    gsm_secret = dagger_client.host().env_variable(gcp_gsm_env_variable_name).secret()
    secrets_path = "/" + str(connector.code_directory) + "/secrets"

    ci_credentials = await environments.with_ci_credentials(dagger_client, gsm_secret)
    return (
        ci_credentials.with_exec(["mkdir", "-p", secrets_path])
        .with_env_variable(
            "CACHEBUSTER", datetime.datetime.now().isoformat()
        )  # Secrets can be updated on GSM anytime, we can't cache this step...
        .with_exec(["ci_credentials", connector.technical_name, "write-to-storage"])
        .directory(secrets_path)
    )


async def upload(
    dagger_client: Client, connector: Connector, secrets_dir: Directory, gcp_gsm_env_variable_name: str = "GCP_GSM_CREDENTIALS"
) -> int:
    gsm_secret = dagger_client.host().env_variable(gcp_gsm_env_variable_name).secret()
    secrets_path = "/" + str(connector.code_directory) + "/secrets"

    ci_credentials = await environments.with_ci_credentials(dagger_client, gsm_secret)

    return await (
        ci_credentials.with_directory(secrets_path, secrets_dir)
        .with_exec(["ci_credentials", connector.technical_name, "update-secrets"])
        .exit_code()
    )
