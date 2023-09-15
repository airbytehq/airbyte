from pipelines.actions.environments.python.common import with_python_base
from pipelines.actions.environments.python.pyproject_based import with_installed_pipx_package
from pipelines.consts import CI_CREDENTIALS_SOURCE_PATH, CONNECTOR_OPS_SOURCE_PATHSOURCE_PATH
from pipelines.contexts import PipelineContext


from dagger import Container, Secret


async def with_ci_credentials(context: PipelineContext, gsm_secret: Secret) -> Container:
    """Install the ci_credentials package in a python environment.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.
        gsm_secret (Secret): The secret holding GCP_GSM_CREDENTIALS env variable value.

    Returns:
        Container: A python environment with the ci_credentials package installed.
    """
    python_base_environment: Container = with_python_base(context)
    ci_credentials = await with_installed_pipx_package(context, python_base_environment, CI_CREDENTIALS_SOURCE_PATH)
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

    return await with_installed_pipx_package(context, python_base_environment, CONNECTOR_OPS_SOURCE_PATHSOURCE_PATH)
