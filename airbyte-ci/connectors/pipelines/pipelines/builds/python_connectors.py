#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import importlib.util
from pathlib import Path

from dagger import CacheVolume, Container, QueryError
from pipelines.actions.environments import find_local_python_dependencies
from pipelines.bases import StepResult, StepStatus
from pipelines.builds.base_images.python import ALL_BASE_IMAGES
from pipelines.builds.common import BuildConnectorImageBase, BuildConnectorImageForAllPlatformsBase
from pipelines.contexts import ConnectorContext


class BuildConnectorImage(BuildConnectorImageBase):
    """
    A step to build a Python connector image.
    A spec command is run on the container to validate it was built successfully.
    """

    entrypoint = ["python", "/airbyte/integration_code/main.py"]

    async def _run(self) -> StepResult:
        connector_base_image = self.context.connector.metadata["connectorBaseImage"]
        if connector_base_image not in ALL_BASE_IMAGES:
            return StepResult(
                self,
                StepStatus.FAILURE,
                f"Connector base image {connector_base_image} does not exists. " f"Supported connector base images are {ALL_BASE_IMAGES}",
            )
        base: Container = ALL_BASE_IMAGES[connector_base_image]
        connector: Container = self._build_from_base(base)
        try:
            return await self.get_step_result(connector.with_exec(["spec"]))
        except QueryError as e:
            return StepResult(self, StepStatus.FAILURE, stderr=str(e))

    async def _build_from_base(self, base: Container):
        pip_cache: CacheVolume = self.context.dagger_client.cache_volume("pip_cache")
        snake_case_name = self.context.connector.technical_name.replace("-", "_")

        setup_dependencies_to_mount = await find_local_python_dependencies(
            self.context,
            str(self.context.connector.code_directory),
            search_dependencies_in_setup_py=True,
            search_dependencies_in_requirements_txt=False,
        )

        with_setup_file: Container = (
            base.with_env_variable("DAGGER_BUILD", "True")
            .with_workdir("/airbyte/integration_code")
            .with_mounted_cache("/root/.cache/pip", pip_cache)
            .with_file("setup.py", (await self.context.get_connector_dir(include="setup.py")).file("setup.py"))
        )
        with_local_dependencies = with_setup_file

        for dependency_path in setup_dependencies_to_mount:
            in_container_dependency_path = f"/local_dependencies/{Path(dependency_path).name}"
            with_local_dependencies = with_local_dependencies.with_mounted_directory(
                in_container_dependency_path, self.context.get_repo_dir(dependency_path)
            )
        with_main = with_local_dependencies.with_file("main.py", self.context.connector.code_directory.file("main.py"))
        with_connector_code = with_main.with_directory(
            snake_case_name, (await self.context.get_connector_dir(include=snake_case_name)).directory(snake_case_name)
        )
        connector_container = (
            with_connector_code.with_env_variable("AIRBYTE_ENTRYPOINT", " ".join(self.entrypoint))
            .with_entrypoint(self.entrypoint)
            .with_label("io.airbyte.version", self.context.metadata["dockerImageTag"])
            .with_label("io.airbyte.name", self.context.metadata["dockerRepository"])
        )
        return await self.finalize_build(self.context, connector_container)

    @staticmethod
    async def finalize_build(context: ConnectorContext, connector_container: Container) -> Container:
        """Finalize build by running finalize_build.sh or finalize_build.py if present in the connector directory."""
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


class BuildConnectorImageForAllPlatforms(BuildConnectorImageForAllPlatformsBase):
    """Build a Python connector image for all platforms."""

    async def _run(self) -> StepResult:
        build_results_per_platform = {}
        for platform in self.ALL_PLATFORMS:
            build_connector_step_result = await BuildConnectorImage(self.context, platform).run()
            if build_connector_step_result.status is not StepStatus.SUCCESS:
                return build_connector_step_result
            build_results_per_platform[platform] = build_connector_step_result.output_artifact
        return self.get_success_result(build_results_per_platform)


async def run_connector_build(context: ConnectorContext) -> StepResult:
    return await BuildConnectorImageForAllPlatforms(context).run()
