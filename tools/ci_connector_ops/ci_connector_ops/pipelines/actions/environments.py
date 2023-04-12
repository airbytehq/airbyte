#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This modules groups functions made to create reusable environments packaged in dagger containers."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional, Tuple

from ci_connector_ops.pipelines.utils import get_file_contents, get_version_from_dockerfile, should_enable_sentry, slugify
from dagger import CacheSharingMode, CacheVolume, Container, Directory, File, Secret

if TYPE_CHECKING:
    from ci_connector_ops.pipelines.contexts import ConnectorTestContext, PipelineContext

PYPROJECT_TOML_FILE_PATH = "pyproject.toml"

CONNECTOR_TESTING_REQUIREMENTS = [
    "pip==21.3.1",
    "mccabe==0.6.1",
    "flake8==4.0.1",
    "pyproject-flake8==0.0.1a2",
    "black==22.3.0",
    "isort==5.6.4",
    "pytest==6.2.5",
    "coverage[toml]==6.3.1",
    "pytest-custom_exit_code",
]

DEFAULT_PYTHON_EXCLUDE = ["**/.venv", "**/__pycache__"]
CI_CREDENTIALS_SOURCE_PATH = "tools/ci_credentials"
CI_CONNECTOR_OPS_SOURCE_PATH = "tools/ci_connector_ops"


def with_python_base(context: PipelineContext, python_image_name: str = "python:3.9-slim") -> Container:
    """Build a Python container with a cache volume for pip cache.

    Args:
        context (PipelineContext): The current test context, providing a dagger client and a repository directory.
        python_image_name (str, optional): The python image to use to build the python base environment. Defaults to "python:3.9-slim".

    Raises:
        ValueError: Raised if the python_image_name is not a python image.

    Returns:
        Container: The python base environment container.
    """
    if not python_image_name.startswith("python:3"):
        raise ValueError("You have to use a python image to build the python base environment")
    pip_cache: CacheVolume = context.dagger_client.cache_volume("pip_cache")

    base_container = (
        context.dagger_client.container()
        .from_(python_image_name)
        .with_mounted_cache("/root/.cache/pip", pip_cache, sharing=CacheSharingMode.LOCKED)
        .with_mounted_directory("/tools", context.get_repo_dir("tools", include=["ci_credentials", "ci_common_utils"], exclude=[".venv"]))
        .with_exec(["pip", "install", "--upgrade", "pip"])
    )

    return base_container


def with_testing_dependencies(context: PipelineContext) -> Container:
    """Build a testing environment by installing testing dependencies on top of a python base environment.

    Args:
        context (PipelineContext): The current test context, providing a dagger client and a repository directory.

    Returns:
        Container: The testing environment container.
    """
    python_environment: Container = with_python_base(context)
    pyproject_toml_file = context.get_repo_dir(".", include=[PYPROJECT_TOML_FILE_PATH]).file(PYPROJECT_TOML_FILE_PATH)
    return python_environment.with_exec(["pip", "install"] + CONNECTOR_TESTING_REQUIREMENTS).with_file(
        f"/{PYPROJECT_TOML_FILE_PATH}", pyproject_toml_file
    )


def with_python_package(
    context: PipelineContext,
    python_environment: Container,
    package_source_code_path: str,
    exclude: Optional[List] = None,
) -> Container:
    """Load a python package source code to a python environment container.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the python sources will be pulled.
        python_environment (Container): An existing python environment in which the package will be installed.
        package_source_code_path (str): The local path to the package source code.
        additional_dependency_groups (Optional[List]): extra_requires dependency of setup.py to install. Defaults to None.
        exclude (Optional[List]): A list of file or directory to exclude from the python package source code.

    Returns:
        Container: A python environment container with the python package source code.
    """
    if exclude:
        exclude = DEFAULT_PYTHON_EXCLUDE + exclude
    else:
        exclude = DEFAULT_PYTHON_EXCLUDE
    package_source_code_directory: Directory = context.get_repo_dir(package_source_code_path, exclude=exclude)
    container = python_environment.with_mounted_directory("/" + package_source_code_path, package_source_code_directory).with_workdir(
        "/" + package_source_code_path
    )
    return container


async def with_installed_python_package(
    context: PipelineContext,
    python_environment: Container,
    package_source_code_path: str,
    additional_dependency_groups: Optional[List] = None,
    exclude: Optional[List] = None,
) -> Container:
    """Install a python package in a python environment container.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the python sources will be pulled.
        python_environment (Container): An existing python environment in which the package will be installed.
        package_source_code_path (str): The local path to the package source code.
        additional_dependency_groups (Optional[List]): extra_requires dependency of setup.py to install. Defaults to None.
        exclude (Optional[List]): A list of file or directory to exclude from the python package source code.

    Returns:
        Container: A python environment container with the python package installed.
    """
    install_local_requirements_cmd = ["python", "-m", "pip", "install", "-r", "requirements.txt"]
    install_connector_package_cmd = ["python", "-m", "pip", "install", "."]

    container = with_python_package(context, python_environment, package_source_code_path, exclude=exclude)
    if requirements_txt := await get_file_contents(container, "requirements.txt"):
        for line in requirements_txt.split("\n"):
            if line.startswith("-e ."):
                local_dependency_path = package_source_code_path + "/" + line[3:]
                container = container.with_mounted_directory(
                    "/" + local_dependency_path, context.get_repo_dir(local_dependency_path, exclude=DEFAULT_PYTHON_EXCLUDE)
                )
        container = container.with_exec(install_local_requirements_cmd)

    container = container.with_exec(install_connector_package_cmd)

    if additional_dependency_groups:
        container = container.with_exec(
            install_connector_package_cmd[:-1] + [install_connector_package_cmd[-1] + f"[{','.join(additional_dependency_groups)}]"]
        )

    return container


def with_airbyte_connector(context: ConnectorTestContext) -> Container:
    """Load an airbyte connector source code in a testing environment.

    Args:
        context (ConnectorTestContext): The current test context, providing the repository directory from which the connector sources will be pulled.
    Returns:
        Container: A python environment container (with the connector source code).
    """
    connector_source_path = str(context.connector.code_directory)
    testing_environment: Container = with_testing_dependencies(context)
    return with_python_package(context, testing_environment, connector_source_path, exclude=["secrets"])


async def with_installed_airbyte_connector(context: ConnectorTestContext) -> Container:
    """Install an airbyte connector python package in a testing environment.

    Args:
        context (ConnectorTestContext): The current test context, providing the repository directory from which the connector sources will be pulled.
    Returns:
        Container: A python environment container (with the connector installed).
    """
    connector_source_path = str(context.connector.code_directory)
    testing_environment: Container = with_testing_dependencies(context)
    return await with_installed_python_package(
        context, testing_environment, connector_source_path, additional_dependency_groups=["dev", "tests", "main"], exclude=["secrets"]
    )


async def with_ci_credentials(context: PipelineContext, gsm_secret: Secret) -> Container:
    """Install the ci_credentials package in a python environment.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.
        gsm_secret (Secret): The secret holding GCP_GSM_CREDENTIALS env variable value.

    Returns:
        Container: A python environment with the ci_credentials package installed.
    """
    python_base_environment: Container = with_python_base(context)
    ci_credentials = await with_installed_python_package(context, python_base_environment, CI_CREDENTIALS_SOURCE_PATH)

    return ci_credentials.with_env_variable("VERSION", "dev").with_secret_variable("GCP_GSM_CREDENTIALS", gsm_secret).with_workdir("/")


def with_alpine_packages(base_container: Container, packages_to_install: List[str]) -> Container:
    """Installs packages using apk-get.
    Args:
        context (Container): A alpine based container.

    Returns:
        Container: A container with the packages installed.

    """
    package_install_command = ["apk", "add"]
    return base_container.with_exec(package_install_command + packages_to_install)


def with_debian_packages(base_container: Container, packages_to_install: List[str]) -> Container:
    """Installs packages using apt-get.
    Args:
        context (Container): A alpine based container.

    Returns:
        Container: A container with the packages installed.

    """
    update_packages_command = ["apt-get", "update"]
    package_install_command = ["apt-get", "install", "-y"]
    return base_container.with_exec(update_packages_command).with_exec(package_install_command + packages_to_install)


def with_pip_packages(base_container: Container, packages_to_install: List[str]) -> Container:
    """Installs packages using pip
    Args:
        context (Container): A container with python installed

    Returns:
        Container: A container with the pip packages installed.

    """
    package_install_command = ["python", "-m", "pip", "install"]
    return base_container.with_exec(package_install_command + packages_to_install)


async def with_ci_connector_ops(context: PipelineContext) -> Container:
    """Installs the ci_connector_ops package in a Container running Python > 3.10 with git..

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_connector_sources sources will be pulled.

    Returns:
        Container: A python environment container with ci_connector_ops installed.
    """
    python_base_environment: Container = with_python_base(context, "python:3-alpine")
    python_with_git = with_alpine_packages(python_base_environment, ["gcc", "libffi-dev", "musl-dev", "git"])
    return await with_installed_python_package(context, python_with_git, CI_CONNECTOR_OPS_SOURCE_PATH, exclude=["pipelines"])


def with_dockerd_service(
    context: ConnectorTestContext, shared_volume: Optional(Tuple[str, CacheVolume]) = None, docker_service_name: Optional[str] = None
) -> Container:
    """Create a container running dockerd, exposing its 2375 port, can be used as the docker host for docker-in-docker use cases.

    Args:
        context (ConnectorTestContext): The current connector test context.
        shared_volume (Optional, optional): A tuple in the form of (mounted path, cache volume) that will be mounted to the dockerd container. Defaults to None.
        docker_service_name (Optional[str], optional): The name of the docker service, appended to volume name, useful context isolation. Defaults to None.

    Returns:
        Container: The container running dockerd as a service.
    """
    docker_lib_volume_name = f"{slugify(context.connector.technical_name)}-docker-lib"
    if docker_service_name:
        docker_lib_volume_name = f"{docker_lib_volume_name}-{slugify(docker_service_name)}"
    dind = (
        context.dagger_client.container()
        .from_("docker:23.0.1-dind")
        .with_mounted_cache(
            "/var/lib/docker",
            context.dagger_client.cache_volume(docker_lib_volume_name),
            sharing=CacheSharingMode.SHARED,
        )
    )
    if shared_volume is not None:
        dind = dind.with_mounted_cache(*shared_volume)
    return dind.with_exposed_port(2375).with_exec(
        ["dockerd", "--log-level=error", "--host=tcp://0.0.0.0:2375", "--tls=false"], insecure_root_capabilities=True
    )


def with_bound_docker_host(
    context: ConnectorTestContext,
    container: Container,
    shared_volume: Optional(Tuple[str, CacheVolume]) = None,
    docker_service_name: Optional[str] = None,
) -> Container:
    """Bind a container to a docker host. It will use the dockerd service as a docker host.

    Args:
        context (ConnectorTestContext): The current connector test context.
        container (Container): The container to bind to the docker host.
        shared_volume (Optional, optional): A tuple in the form of (mounted path, cache volume) that will be both mounted to the container and the dockerd container. Defaults to None.
        docker_service_name (Optional[str], optional): The name of the docker service, useful context isolation. Defaults to None.

    Returns:
        Container: The container bound to the docker host.
    """
    dockerd = with_dockerd_service(context, shared_volume, docker_service_name)
    docker_hostname = f"dockerhost-{slugify(context.connector.technical_name)}"
    if docker_service_name:
        docker_hostname = f"{docker_hostname}-{slugify(docker_service_name)}"
    bound = container.with_env_variable("DOCKER_HOST", f"tcp://{docker_hostname}:2375").with_service_binding(docker_hostname, dockerd)
    if shared_volume:
        bound = bound.with_mounted_cache(*shared_volume)
    return bound


def with_docker_cli(
    context: ConnectorTestContext, shared_volume: Optional(Tuple[str, CacheVolume]) = None, docker_service_name: Optional[str] = None
) -> Container:
    """Create a container with the docker CLI installed and bound to a persistent docker host.

    Args:
        context (ConnectorTestContext): The current connector test context.
        shared_volume (Optional, optional): A tuple in the form of (mounted path, cache volume) that will be both mounted to the container and the dockerd container. Defaults to None.
        docker_service_name (Optional[str], optional): The name of the docker service, useful context isolation. Defaults to None.

    Returns:
        Container: A docker cli container bound to a docker host.
    """
    docker_cli = context.dagger_client.container().from_("docker:23.0.1-cli")
    return with_bound_docker_host(context, docker_cli, shared_volume, docker_service_name)


async def with_connector_acceptance_test(context: ConnectorTestContext, connector_under_test_image_tar: File) -> Container:
    """Create a container to run connector acceptance tests, bound to a persistent docker host.

    Args:
        context (ConnectorTestContext): The current connector test context.
        connector_under_test_image_tar (File): The file containing the tar archive the image of the connector under test.
    Returns:
        Container: A container with connector acceptance tests installed.
    """
    connector_under_test_image_name = context.connector.acceptance_test_config["connector_image"]
    await load_image_to_docker_host(context, connector_under_test_image_tar, connector_under_test_image_name, docker_service_name="cat")

    if context.connector_acceptance_test_image.endswith(":dev"):
        cat_container = context.connector_acceptance_test_source_dir.docker_build()
    else:
        cat_container = context.dagger_client.container().from_(context.connector_acceptance_test_image)
    shared_tmp_volume = ("/tmp", context.dagger_client.cache_volume("share-tmp-cat"))

    return (
        with_bound_docker_host(context, cat_container, shared_tmp_volume, docker_service_name="cat")
        .with_entrypoint([])
        .with_exec(["pip", "install", "pytest-custom_exit_code"])
        .with_mounted_directory("/test_input", context.get_connector_dir(exclude=["secrets", ".venv"]))
        .with_directory("/test_input/secrets", context.secrets_dir)
        .with_workdir("/test_input")
        .with_entrypoint(["python", "-m", "pytest", "-p", "connector_acceptance_test.plugin", "--suppress-tests-failed-exit-code"])
        .with_exec(["--acceptance-test-config", "/test_input"])
    )


def with_gradle(
    context: ConnectorTestContext,
    sources_to_include: List[str] = None,
    bind_to_docker_host: bool = True,
    docker_service_name: Optional[str] = "gradle",
) -> Container:
    """Create a container with Gradle installed and bound to a persistent docker host.

    Args:
        context (ConnectorTestContext): The current connector test context.
        sources_to_include (List[str], optional): List of additional source path to mount to the container. Defaults to None.
        bind_to_docker_host (bool): Whether to bind the gradle container to a docker host.
        docker_service_name (Optional[str], optional): The name of the docker service, useful context isolation. Defaults to "gradle".

    Returns:
        Container: A container with Gradle installed and Java sources from the repository.
    """
    airbyte_gradle_cache: CacheVolume = context.dagger_client.cache_volume(f"{context.connector.technical_name}_airbyte_gradle_cache")
    root_gradle_cache: CacheVolume = context.dagger_client.cache_volume(f"{context.connector.technical_name}_root_gradle_cache")

    include = [
        ".root",
        ".env",
        "build.gradle",
        "deps.toml",
        "gradle.properties",
        "gradle",
        "gradlew",
        "LICENSE_SHORT",
        "publish-repositories.gradle",
        "settings.gradle",
        "build.gradle",
        "tools/gradle",
        "spotbugs-exclude-filter-file.xml",
        "buildSrc",
        "tools/bin/build_image.sh",
        "tools/lib/lib.sh",
    ]

    if sources_to_include:
        include += sources_to_include

    shared_tmp_volume = ("/tmp", context.dagger_client.cache_volume("share-tmp-gradle"))

    openjdk_with_docker = (
        context.dagger_client.container()
        # Use openjdk image because it's based on Debian. Alpine with Gradle and Python causes filesystem crash.
        .from_("openjdk:17.0.1-jdk-slim")
        .with_exec(["apt-get", "update"])
        .with_exec(["apt-get", "install", "-y", "curl", "jq"])
        .with_env_variable("VERSION", "23.0.1")
        .with_exec(["sh", "-c", "curl -fsSL https://get.docker.com | sh"])
        .with_exec(["mkdir", "/root/.gradle"])
        .with_mounted_cache("/root/.gradle", root_gradle_cache, sharing=CacheSharingMode.LOCKED)
        .with_exec(["mkdir", "/airbyte"])
        .with_mounted_directory("/airbyte", context.get_repo_dir(".", include=include))
        .with_mounted_cache("/airbyte/.gradle", airbyte_gradle_cache, sharing=CacheSharingMode.LOCKED)
        .with_workdir("/airbyte")
    )
    if bind_to_docker_host:
        return with_bound_docker_host(context, openjdk_with_docker, shared_tmp_volume, docker_service_name=docker_service_name)
    else:
        return openjdk_with_docker


async def load_image_to_docker_host(
    context: ConnectorTestContext, tar_file: File, image_tag: str, docker_service_name: Optional[str] = None
):
    """Load a docker image tar archive to the docker host.

    Args:
        context (ConnectorTestContext): The current connector test context.
        tar_file (File): The file object holding the docker image tar archive.
        image_tag (str): The tag to create on the image if it has no tag.
        docker_service_name (str): Name of the docker service, useful for context isolation.
    """
    # Hacky way to make sure the image is always loaded
    tar_name = f"{str(uuid.uuid4())}.tar"
    docker_cli = with_docker_cli(context, docker_service_name=docker_service_name).with_mounted_file(tar_name, tar_file)
    image_load_output = await docker_cli.with_exec(["docker", "load", "--input", tar_name]).stdout()
    # Not tagged images only have a sha256 id the load output shares.
    if "sha256:" in image_load_output:
        image_id = image_load_output.replace("\n", "").replace("Loaded image ID: sha256:", "")
        await docker_cli.with_exec(["docker", "tag", image_id, image_tag]).exit_code()


def with_poetry(context: PipelineContext) -> Container:
    """Install poetry in a python environment.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.
    Returns:
        Container: A python environment with poetry installed.
    """
    python_base_environment: Container = with_python_base(context, "python:3.9")
    python_with_git = with_debian_packages(python_base_environment, ["git"])
    python_with_poetry = with_pip_packages(python_with_git, ["poetry"])

    poetry_cache: CacheVolume = context.dagger_client.cache_volume("poetry_cache")
    poetry_with_cache = python_with_poetry.with_mounted_cache("/root/.cache/pypoetry", poetry_cache, sharing=CacheSharingMode.PRIVATE)

    return poetry_with_cache


def with_pipx(base_python_container: Container) -> Container:
    """Installs pipx in a python container.

    Args:
       base_python_container (Container): The container to install pipx on.

    Returns:
        Container: A python environment with pipx installed.
    """
    python_with_pipx = with_pip_packages(base_python_container, ["pipx"]).with_env_variable("PIPX_BIN_DIR", "/usr/local/bin")

    return python_with_pipx


def with_poetry_module(context: PipelineContext, parent_dir: Directory, module_path: str) -> Container:
    """Sets up a Poetry module.

    Args:
        context (PipelineContext): The current test context, providing the repository directory from which the ci_credentials sources will be pulled.
    Returns:
        Container: A python environment with dependencies installed using poetry.
    """
    poetry_install_dependencies_cmd = ["poetry", "install"]

    python_with_poetry = with_poetry(context)
    return (
        python_with_poetry.with_mounted_directory("/src", parent_dir)
        .with_workdir(f"/src/{module_path}")
        .with_exec(poetry_install_dependencies_cmd)
    )


def with_pipx_module(context: PipelineContext, parent_dir_path: str, module_path: str, include: List[str]) -> Container:
    """Installs a pipx module

    Args:
        context (PipelineContext): The current pipeline context
    Returns:
        Container: A python environment with dependencies installed using pipx.
    """
    pipx_include = [module_path] + include
    pipx_install_dependencies_cmd = ["pipx", "install", module_path]
    src = context.get_repo_dir(parent_dir_path, exclude=DEFAULT_PYTHON_EXCLUDE, include=pipx_include)

    python_base_environment = with_python_base(context, "python:3.9")
    python_with_pipx = with_pipx(python_base_environment)

    return python_with_pipx.with_mounted_directory("/src", src).with_workdir("/src").with_exec(pipx_install_dependencies_cmd)


def with_integration_base(context: PipelineContext, jdk_version: str = "17.0.4") -> Container:
    """Create an integration base container.

    Reproduce with Dagger the Dockerfile defined here: airbyte-integrations/bases/base/Dockerfile
    """
    base_sh = context.get_repo_dir("airbyte-integrations/bases/base", include=["base.sh"]).file("base.sh")

    return (
        context.dagger_client.container()
        .from_(f"amazoncorretto:{jdk_version}")
        .with_workdir("/airbyte")
        .with_file("base.sh", base_sh)
        .with_env_variable("AIRBYTE_ENTRYPOINT", "/airbyte/base.sh")
        .with_label("io.airbyte.version", "0.1.0")
        .with_label("io.airbyte.name", "airbyte/integration-base")
    )


async def with_java_base(context: PipelineContext, jdk_version: str = "17.0.4") -> Container:
    """Create a java base container.

    Reproduce with Dagger the Dockerfile defined here: airbyte-integrations/bases/base-java/Dockerfile_
    """
    datadog_java_agent = context.dagger_client.http("https://dtdg.co/latest-java-tracer")
    javabase_sh = context.get_repo_dir("airbyte-integrations/bases/base-java", include=["javabase.sh"]).file("javabase.sh")
    dockerfile = context.get_repo_dir("airbyte-integrations/bases/base-java", include=["Dockerfile"]).file("Dockerfile")
    java_base_version = await get_version_from_dockerfile(dockerfile)

    return (
        with_integration_base(context, jdk_version)
        .with_exec(["yum", "install", "-y", "tar", "openssl"])
        .with_exec(["yum", "clean", "all"])
        .with_workdir("/airbyte")
        .with_file("dd-java-agent.jar", datadog_java_agent)
        .with_file("javabase.sh", javabase_sh)
        .with_env_variable("AIRBYTE_SPEC_CMD", "/airbyte/javabase.sh --spec")
        .with_env_variable("AIRBYTE_CHECK_CMD", "/airbyte/javabase.sh --check")
        .with_env_variable("AIRBYTE_DISCOVER_CMD", "/airbyte/javabase.sh --discover")
        .with_env_variable("AIRBYTE_READ_CMD", "/airbyte/javabase.sh --read")
        .with_env_variable("AIRBYTE_WRITE_CMD", "/airbyte/javabase.sh --write")
        .with_env_variable("AIRBYTE_ENTRYPOINT", "/airbyte/base.sh")
        .with_label("io.airbyte.version", java_base_version)
        .with_label("io.airbyte.name", "airbyte/integration-base-java")
    )


async def with_airbyte_java_connector(context: ConnectorTestContext, connector_java_tar_file: File):
    dockerfile = context.get_connector_dir(include=["Dockerfile"]).file("Dockerfile")
    connector_version = await get_version_from_dockerfile(dockerfile)
    application = context.connector.technical_name
    java_base = await with_java_base(context)
    enable_sentry = await should_enable_sentry(dockerfile)

    return (
        java_base.with_workdir("/airbyte")
        .with_env_variable("APPLICATION", application)
        .with_file(f"{application}.tar", connector_java_tar_file)
        .with_exec(["tar", "xf", f"{application}.tar", "--strip-components=1"])
        .with_exec(["rm", "-rf", f"{application}.tar"])
        .with_label("io.airbyte.version", connector_version)
        .with_label("io.airbyte.name", f"airbyte/{application}")
        .with_env_variable("ENABLE_SENTRY", str(enable_sentry).lower())
        .with_entrypoint("/airbyte/base.sh")
    )


def with_normalization(context, normalization_dockerfile_name: str) -> Container:
    normalization_directory = context.get_repo_dir("airbyte-integrations/bases/base-normalization")
    sshtunneling_file = context.get_repo_dir(
        "airbyte-connector-test-harnesses/acceptance-test-harness/src/main/resources", include="sshtunneling.sh"
    ).file("sshtunneling.sh")
    normalization_directory_with_build = normalization_directory.with_new_directory("build")
    normalization_directory_with_sshtunneling = normalization_directory_with_build.with_file("build/sshtunneling.sh", sshtunneling_file)
    return normalization_directory_with_sshtunneling.docker_build(normalization_dockerfile_name)
