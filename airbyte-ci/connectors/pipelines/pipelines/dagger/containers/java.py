#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime

from dagger import CacheVolume, Container, File, Platform
from pipelines.airbyte_ci.connectors.context import ConnectorContext, PipelineContext
from pipelines.consts import AMAZONCORRETTO_IMAGE
from pipelines.dagger.actions.connector.hooks import finalize_build
from pipelines.dagger.actions.connector.normalization import DESTINATION_NORMALIZATION_BUILD_CONFIGURATION, with_normalization
from pipelines.helpers.utils import sh_dash_c


def with_integration_base(context: PipelineContext, build_platform: Platform) -> Container:
    return (
        context.dagger_client.container(platform=build_platform)
        .from_("amazonlinux:2022.0.20220831.1")
        .with_workdir("/airbyte")
        .with_file("base.sh", context.get_repo_dir("airbyte-integrations/bases/base", include=["base.sh"]).file("base.sh"))
        .with_env_variable("AIRBYTE_ENTRYPOINT", "/airbyte/base.sh")
        .with_label("io.airbyte.version", "0.1.0")
        .with_label("io.airbyte.name", "airbyte/integration-base")
    )


def with_integration_base_java(context: PipelineContext, build_platform: Platform) -> Container:
    integration_base = with_integration_base(context, build_platform)
    yum_packages_to_install = [
        "tar",  # required to untar java connector binary distributions.
        "openssl",  # required because we need to ssh and scp sometimes.
        "findutils",  # required for xargs, which is shipped as part of findutils.
    ]
    return (
        context.dagger_client.container(platform=build_platform)
        # Use a linux+jdk base image with long-term support, such as amazoncorretto.
        .from_(AMAZONCORRETTO_IMAGE)
        # Bust the cache on a daily basis to get fresh packages.
        .with_env_variable("DAILY_CACHEBUSTER", datetime.datetime.now().strftime("%Y-%m-%d"))
        # Install a bunch of packages as early as possible.
        .with_exec(
            sh_dash_c(
                [
                    # Update first, but in the same .with_exec step as the package installation.
                    # Otherwise, we risk caching stale package URLs.
                    "yum update -y --security",
                    #
                    f"yum install -y {' '.join(yum_packages_to_install)}",
                    # Remove any dangly bits.
                    "yum clean all",
                ]
            )
        )
        # Add what files we need to the /airbyte directory.
        # Copy base.sh from the airbyte/integration-base image.
        .with_directory("/airbyte", integration_base.directory("/airbyte"))
        .with_workdir("/airbyte")
        # Download a utility jar from the internet.
        .with_file("dd-java-agent.jar", context.dagger_client.http("https://dtdg.co/latest-java-tracer"))
        # Copy javabase.sh from the git repo.
        .with_file("javabase.sh", context.get_repo_dir("airbyte-integrations/bases/base-java", include=["javabase.sh"]).file("javabase.sh"))
        # Set a bunch of env variables used by base.sh.
        .with_env_variable("AIRBYTE_SPEC_CMD", "/airbyte/javabase.sh --spec")
        .with_env_variable("AIRBYTE_CHECK_CMD", "/airbyte/javabase.sh --check")
        .with_env_variable("AIRBYTE_DISCOVER_CMD", "/airbyte/javabase.sh --discover")
        .with_env_variable("AIRBYTE_READ_CMD", "/airbyte/javabase.sh --read")
        .with_env_variable("AIRBYTE_WRITE_CMD", "/airbyte/javabase.sh --write")
        .with_env_variable("AIRBYTE_ENTRYPOINT", "/airbyte/base.sh")
        # Set image labels.
        .with_label("io.airbyte.version", "0.1.2")
        .with_label("io.airbyte.name", "airbyte/integration-base-java")
    )


def with_integration_base_java_and_normalization(context: ConnectorContext, build_platform: Platform) -> Container:
    yum_packages_to_install = [
        "python3",
        "python3-devel",
        "jq",
        "sshpass",
        "git",
    ]

    additional_yum_packages = DESTINATION_NORMALIZATION_BUILD_CONFIGURATION[context.connector.technical_name]["yum_packages"]
    yum_packages_to_install += additional_yum_packages

    dbt_adapter_package = DESTINATION_NORMALIZATION_BUILD_CONFIGURATION[context.connector.technical_name]["dbt_adapter"]
    assert isinstance(dbt_adapter_package, str)
    normalization_integration_name = DESTINATION_NORMALIZATION_BUILD_CONFIGURATION[context.connector.technical_name]["integration_name"]
    assert isinstance(normalization_integration_name, str)

    pip_cache: CacheVolume = context.dagger_client.cache_volume("pip_cache")

    return (
        with_integration_base_java(context, build_platform)
        # Bust the cache on a daily basis to get fresh packages.
        .with_env_variable("DAILY_CACHEBUSTER", datetime.datetime.now().strftime("%Y-%m-%d"))
        .with_exec(
            sh_dash_c(
                [
                    "yum update -y --security",
                    f"yum install -y {' '.join(yum_packages_to_install)}",
                    "yum clean all",
                    "alternatives --install /usr/bin/python python /usr/bin/python3 60",
                ]
            )
        )
        .with_mounted_cache("/root/.cache/pip", pip_cache)
        .with_exec(
            sh_dash_c(
                [
                    "python -m ensurepip --upgrade",
                    # Workaround for https://github.com/yaml/pyyaml/issues/601
                    "pip3 install 'Cython<3.0' 'pyyaml~=5.4' --no-build-isolation",
                    # Required for dbt https://github.com/dbt-labs/dbt-core/issues/7075
                    "pip3 install 'pytz~=2023.3'",
                    f"pip3 install {dbt_adapter_package}",
                    # amazon linux 2 isn't compatible with urllib3 2.x, so force 1.x
                    "pip3 install 'urllib3<2'",
                ]
            )
        )
        .with_directory("airbyte_normalization", with_normalization(context, build_platform).directory("/airbyte"))
        .with_workdir("airbyte_normalization")
        .with_exec(sh_dash_c(["mv * .."]))
        .with_workdir("/airbyte")
        .with_exec(["rm", "-rf", "airbyte_normalization"], use_entrypoint=True)
        .with_workdir("/airbyte/normalization_code")
        .with_exec(["pip3", "install", "."], use_entrypoint=True)
        .with_workdir("/airbyte/normalization_code/dbt-template/")
        .with_exec(["dbt", "deps"], use_entrypoint=True)
        .with_workdir("/airbyte")
        .with_file(
            "run_with_normalization.sh",
            context.get_repo_dir("airbyte-integrations/bases/base-java", include=["run_with_normalization.sh"]).file(
                "run_with_normalization.sh"
            ),
        )
        .with_env_variable("AIRBYTE_NORMALIZATION_INTEGRATION", normalization_integration_name)
        .with_env_variable("AIRBYTE_ENTRYPOINT", "/airbyte/run_with_normalization.sh")
    )


async def with_airbyte_java_connector(context: ConnectorContext, connector_java_tar_file: File, build_platform: Platform) -> Container:
    application = context.connector.technical_name

    build_stage = (
        with_integration_base_java(context, build_platform)
        .with_workdir("/airbyte")
        .with_env_variable("APPLICATION", context.connector.technical_name)
        .with_file(f"{application}.tar", connector_java_tar_file)
        .with_exec(
            sh_dash_c(
                [
                    f"tar xf {application}.tar --strip-components=1",
                    f"rm -rf {application}.tar",
                ]
            )
        )
    )

    if (
        context.connector.supports_normalization
        and DESTINATION_NORMALIZATION_BUILD_CONFIGURATION[context.connector.technical_name]["supports_in_connector_normalization"]
    ):
        base = with_integration_base_java_and_normalization(context, build_platform)
        entrypoint = ["/airbyte/run_with_normalization.sh"]
    else:
        base = with_integration_base_java(context, build_platform)
        entrypoint = ["/airbyte/base.sh"]

    connector_container = (
        base.with_workdir("/airbyte")
        .with_env_variable("APPLICATION", application)
        .with_mounted_directory("built_artifacts", build_stage.directory("/airbyte"))
        .with_exec(sh_dash_c(["mv built_artifacts/* ."]))
        .with_entrypoint(entrypoint)
    )
    return await finalize_build(context, connector_container)
