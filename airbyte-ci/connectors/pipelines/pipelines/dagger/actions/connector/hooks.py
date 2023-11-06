#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import importlib.util

from dagger import Container
from dagger.engine._version import CLI_VERSION as dagger_engine_version
from pipelines.airbyte_ci.connectors.context import ConnectorContext


async def finalize_build(context: ConnectorContext, connector_container: Container) -> Container:
    """Finalize build by adding dagger engine version label and running finalize_build.sh or finalize_build.py if present in the connector directory."""
    connector_container = connector_container.with_label("io.dagger.engine_version", dagger_engine_version)
    connector_dir_with_finalize_script = await context.get_connector_dir(include=["finalize_build.sh", "finalize_build.py"])
    finalize_scripts = await connector_dir_with_finalize_script.entries()
    if not finalize_scripts:
        return connector_container

    # We don't want finalize scripts to override the entrypoint so we keep it in memory to reset it after finalization
    original_entrypoint = await connector_container.entrypoint()

    has_finalize_bash_script = "finalize_build.sh" in finalize_scripts
    has_finalize_python_script = "finalize_build.py" in finalize_scripts
    if has_finalize_python_script and has_finalize_bash_script:
        raise Exception("Connector has both finalize_build.sh and finalize_build.py, please remove one of them")

    if has_finalize_python_script:
        context.logger.info(f"{context.connector.technical_name} has a finalize_build.py script, running it to finalize build...")
        module_path = context.connector.code_directory / "finalize_build.py"
        connector_finalize_module_spec = importlib.util.spec_from_file_location(
            f"{context.connector.code_directory.name}_finalize", module_path
        )
        connector_finalize_module = importlib.util.module_from_spec(connector_finalize_module_spec)
        connector_finalize_module_spec.loader.exec_module(connector_finalize_module)
        try:
            connector_container = await connector_finalize_module.finalize_build(context, connector_container)
        except AttributeError:
            raise Exception("Connector has a finalize_build.py script but it doesn't have a finalize_build function.")

    if has_finalize_bash_script:
        context.logger.info(f"{context.connector.technical_name} has finalize_build.sh script, running it to finalize build...")
        connector_container = (
            connector_container.with_file("/tmp/finalize_build.sh", connector_dir_with_finalize_script.file("finalize_build.sh"))
            .with_entrypoint("sh")
            .with_exec(["/tmp/finalize_build.sh"])
        )

    return connector_container.with_entrypoint(original_entrypoint)
