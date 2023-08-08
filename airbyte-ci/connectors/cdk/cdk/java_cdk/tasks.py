"""CI Workflow tasks for Airbyte Java CDK"""

import os

import pygit2
from aircmd.actions.environments import with_gradle
from aircmd.models.base import PipelineContext
from aircmd.models.utils import load_settings, make_pass_decorator
from dagger import Client, Container
from prefect import task
from prefect.artifacts import create_link_artifact

from .settings import JavaCDKSettings

pass_pipeline_context = make_pass_decorator(PipelineContext, ensure=True)
pass_global_settings = make_pass_decorator(JavaCDKSettings, ensure=True)


@task
async def build_java_cdk_task(client: Client, settings: JavaCDKSettings, ctx: PipelineContext, scan: bool = False) -> Container:
    files_from_host = [
        "./build.gradle",
        "./gradlew",
        "./gradle",
        "./airbyte-cdk/java/**",
        "./publish-repositories.gradle",
        "./gradle.properties",
        "./deps.toml",
        "./build.gradle",
        "./settings.gradle",
        "./.env",
        "./.env.dev",
    ]

    repo = pygit2.Repository(".")
    repo_root = os.path.dirname(os.path.dirname(repo.path))
    print(repo_root)
    mount_dir = client.host().directory(repo_root, include=files_from_host)

    gradle_command = ["./gradlew", ":airbyte-cdk:java:airbyte-cdk:assemble", "publishToMavenLocal", "--build-cache"]

    result = (
        with_gradle(client, ctx, settings, bind_to_docker_host=False)
        .with_mounted_directory("/airbyte", mount_dir)
        .with_(load_settings(settings))
        .with_exec(gradle_command + ["--scan"] if scan else gradle_command)
        .with_exec(["rsync", "-az", "/root/.gradle/", "/root/gradle-cache"])
    )

    if scan:
        await create_link_artifact(
            key="gradle-build-scan",
            link=result.file("/airbyte/scan-journal.log").contents().split(" - ")[2].strip(),
            description="Gradle build scan",
        )

    return result.sync()


@task
async def test_java_cdk_task(
    build_result: Container,
    client: Client,
    settings: JavaCDKSettings,
    ctx: PipelineContext,
    scan: bool = False,
) -> Container:
    files_from_container = [
        "./build.gradle",
        "./gradlew",
        "./gradle",
        "./airbyte-cdk/java/**",
        "./publish-repositories.gradle",
        "./gradle.properties",
        "./deps.toml",
        "./build.gradle",
        "./settings.gradle",
        "./.env",
        "./.env.dev",
    ]

    gradle_command = ["./gradlew", ":airbyte-cdk:java:airbyte-cdk:test", "--build-cache"]

    result = (
        with_gradle(client, ctx, settings, bind_to_docker_host=False)
        .with_directory("/airbyte", build_result.directory("/airbyte"), include=files_from_container)  # test src and build files
        .with_directory("/root/.m2/repository", build_result.directory("/root/.m2/repository"))  # maven local jar files
        .with_(load_settings(settings))
        .with_exec(gradle_command + ["--scan"] if scan else gradle_command)
        .with_exec(["rsync", "-az", "/root/.gradle/", "/root/gradle-cache"])  # sync gradle cache for future runs
    )

    if scan:
        await create_link_artifact(
            key="gradle-build-scan",
            link=result.file("/airbyte/scan-journal.log").contents().split(" - ")[2].strip(),
            description="Gradle build scan",
        )

    return result.sync()


@task
async def publish_java_cdk_task(
    build_result: Container, client: Client, settings: JavaCDKSettings, ctx: PipelineContext, scan: bool = False
) -> Container:
    # TODO: something here that will publish to maven repo from inside the build container, using the jar files
    # from the build container
    pass
