#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dagger import Container, Secret

from pipelines.airbyte_ci.connectors.context import PipelineContext
from pipelines.consts import INTERNAL_TOOL_PATHS
from pipelines.dagger.actions.python.pipx import with_installed_pipx_package
from pipelines.dagger.containers.python import with_python_base


async def with_ci_credentials(context: PipelineContext, gsm_secret: Secret) -> Container:
    """Install the ci_credentials package in a python environment.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.
        gsm_secret (Secret): The secret holding GCP_GSM_CREDENTIALS env variable value.

    Returns:
        Container: A python environment with the ci_credentials package installed.
    """
    python_base_environment: Container = with_python_base(context)
    ci_credentials = await with_installed_pipx_package(context, python_base_environment, INTERNAL_TOOL_PATHS.CI_CREDENTIALS.value)
    ci_credentials = ci_credentials.with_env_variable("VERSION", "dagger_ci")
    return ci_credentials.with_secret_variable("GCP_GSM_CREDENTIALS", gsm_secret).with_workdir("/")


async def with_connector_ops(context: PipelineContext) -> Container:
    """Installs the connector_ops package in a Container running Python > 3.10 with git..

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_connector_sources sources will be pulled.

    Returns:
        Container: A python environment container with connector_ops installed.
    """
    python_base_environment: Container = with_python_base(context)

    return await with_installed_pipx_package(context, python_base_environment, INTERNAL_TOOL_PATHS.CONNECTOR_OPS.value)
