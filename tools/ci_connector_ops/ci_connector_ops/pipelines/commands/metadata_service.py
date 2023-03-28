import click
import anyio
import dagger

from ci_connector_ops.pipelines.actions.environments import with_poetry_module
from ci_connector_ops.pipelines.utils import (
    DAGGER_CONFIG,
    with_exit_code,
)

async def run_metadata_lib_test_pipeline():
    async with dagger.Connection(DAGGER_CONFIG) as dagger_client:
        print(f"Running metadata lib test pipeline...")
        metadata_lib_module = with_poetry_module(dagger_client, "airbyte-ci/connectors/metadata_service/lib")
        return await with_exit_code(metadata_lib_module.with_exec(["poetry", "run", "pytest"]))

@click.group(help="Commands related to the metadata service.")
@click.pass_context
def metadata_service(ctx):
    pass

@metadata_service.command(help="Run unit tests for the metadata service library.")
@click.pass_context
def test_metadata_service_lib(ctx):
    # TODO create a top level ci group
    # TODO rename this command group to test_connectors
    # TODO move this command to test_metadata_lib
    anyio.run(run_metadata_lib_test_pipeline)
