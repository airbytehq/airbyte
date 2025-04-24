#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import importlib.util
from importlib import metadata
from importlib.abc import Loader

from dagger import Container

from pipelines.airbyte_ci.connectors.context import ConnectorContext


def get_dagger_sdk_version() -> str:
    try:
        return metadata.version("dagger-io")
    except metadata.PackageNotFoundError:
        return "n/a"


async def finalize_build(context: ConnectorContext, connector_container: Container) -> Container:
    """Finalize build by adding dagger engine version label and running finalize_build.sh or finalize_build.py if present in the connector directory."""
    original_user = (await connector_container.with_exec(["whoami"]).stdout()).strip()
    # Switch to root to finalize the build with superuser permissions
    connector_container = connector_container.with_user("root")
    connector_container = connector_container.with_label("io.dagger.engine_version", get_dagger_sdk_version())
    connector_dir_with_finalize_script = await context.get_connector_dir(include=["finalize_build.sh", "finalize_build.py"])
    finalize_scripts = await connector_dir_with_finalize_script.entries()
    if not finalize_scripts:
        return connector_container

    # We don't want finalize scripts to override the entrypoint so we keep it in memory to reset it after finalization
    original_entrypoint = await connector_container.entrypoint()
    if not original_entrypoint:
        original_entrypoint = []

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
        if connector_finalize_module_spec is None:
            raise Exception("Connector has a finalize_build.py script but it can't be loaded.")
        connector_finalize_module = importlib.util.module_from_spec(connector_finalize_module_spec)
        if not isinstance(connector_finalize_module_spec.loader, Loader):
            raise Exception("Connector has a finalize_build.py script but it can't be loaded.")
        connector_finalize_module_spec.loader.exec_module(connector_finalize_module)
        try:
            connector_container = await connector_finalize_module.finalize_build(context, connector_container)
        except AttributeError:
            raise Exception("Connector has a finalize_build.py script but it doesn't have a finalize_build function.")

    if has_finalize_bash_script:
        context.logger.info(f"{context.connector.technical_name} has finalize_build.sh script, running it to finalize build...")
        connector_container = (
            connector_container.with_file("/tmp/finalize_build.sh", connector_dir_with_finalize_script.file("finalize_build.sh"))
            .with_entrypoint(["sh"])
            .with_exec(["/tmp/finalize_build.sh"], use_entrypoint=True)
        )
    # Switch back to the original user
    connector_container = connector_container.with_exec(["chown", "-R", f"{original_user}:{original_user}", "/tmp"])
    connector_container = connector_container.with_user(original_user)
    return connector_container.with_entrypoint(original_entrypoint)
