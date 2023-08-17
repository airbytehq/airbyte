#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import anyio
from dagger import Container, Platform
from pipelines.bases import Report, StepResult, StepStatus
from pipelines.builds.common import BuildImageForAllPlatformsBase, LoadContainerToLocalDockerHost
from pipelines.consts import DOCKER_VERSION, LOCAL_BUILD_PLATFORM, PYTHON_3_10_IMAGE
from pipelines.contexts import PipelineContext


class BuildCat(BuildImageForAllPlatformsBase):

    POETRY_VERSION = "1.5.1"
    CAT_TZ = "Etc/UTC"

    async def _run(self) -> StepResult:
        build_results_per_platform = {}
        for platform in self.ALL_PLATFORMS:
            build_results_per_platform[platform] = await self.get_step_result(
                await self.get_container(self.dagger_client, self.context, platform)
            )
        return self.get_success_result(build_results_per_platform)

    @staticmethod
    async def get_container(dagger_client, context, build_platform: Platform = LOCAL_BUILD_PLATFORM) -> Container:
        python_base = dagger_client.container(platform=build_platform).from_(PYTHON_3_10_IMAGE)
        cat_directory = await context.get_repo_dir("airbyte-integrations/bases/connector-acceptance-test")
        return (
            python_base.with_env_variable("ACCEPTANCE_TEST_DOCKER_CONTAINER", "1")
            .with_env_variable("DOCKER_VERSION", DOCKER_VERSION)
            .with_exec(["apt-get", "update"])
            .with_exec(["echo", BuildCat.CAT_TZ, ">", "/etc/timezone"])
            .with_exec(["pip", "install", "--upgrade", "pip"])
            .with_exec(["apt-get", "install", "tzdata", "bash", "curl"])
            .with_exec(["sh", "-c", "curl -fsSL https://get.docker.com | sh"])
            .with_exec(["pip", "install", f"poetry=={BuildCat.POETRY_VERSION}"])
            .with_workdir("/app")
            .with_directory("/app", cat_directory)
            .with_exec(["poetry", "install"])
            .with_workdir("/test_input")
            .with_entrypoint(
                [
                    "poetry",
                    "run",
                    "--directory",
                    "/app",
                    "pytest",
                    "-p",
                    "connector_acceptance_test.plugin",
                    "-r",
                    "fEsx",
                    "--show-capture=log",
                ]
            )
        )


async def run_cat_build_pipeline(context: PipelineContext, semaphore: anyio.Semaphore) -> Report:
    """Run a build pipeline for CAT"""

    step_results = []
    async with semaphore:
        async with context:
            build_result = await BuildCat(context).run()
            step_results.append(build_result)
            if context.is_local and build_result.status is StepStatus.SUCCESS:
                connector_to_load_to_local_docker_host = build_result.output_artifact[LOCAL_BUILD_PLATFORM].output_artifact
                image_name = "airbyte/connector-acceptance-test"
                load_image_result = await LoadContainerToLocalDockerHost(context, connector_to_load_to_local_docker_host, image_name).run()
                step_results.append(load_image_result)
            context.report = Report(context, step_results, name="BUILD CAT RESULTS")
        return context.report
