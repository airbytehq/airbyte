import importlib
import sys
import anyio
import dagger
from pipelines import main_logger
from pipelines.dagger.actions.remote_storage import upload_to_gcs

PLATFORMS_TO_BUILD = {
    "amd64": "python:3.10-slim",
    "arm64": "arm64v8/python:3.10-slim",
}

DIRECTORIES_TO_MOUNT = ["airbyte-ci"]

CURRENT_VERSION = importlib.metadata.version("pipelines")


async def create_airbyte_ci_release(
    dagger_client: dagger.Client,
    ci_gcs_credentials_secret: dagger.Secret,
    ci_artifact_bucket_name: str,
    image: str,
    platform_name: str
):
    """
    Build the airbyte-ci binary for a given platform

    Args:
        dagger_client (dagger.Client): The dagger client
        ci_gcs_credentials_secret (dagger.Secret): The GCS credentials to use for uploading the binary
        ci_artifact_bucket_name (str): The name of the bucket to upload the binary to
        image (str): The docker image to use for building the binary
        platform_name (str): The name of the platform to build the binary for (e.g. amd64, arm64)
    """
    artifact_name = f"airbyte-ci-{platform_name}"
    main_logger.info(f"Building {artifact_name} on {image}")

    container = await (
        dagger_client
        .container()
        .from_(image)
        .with_exec(["apt-get", "update"])
        .with_exec(["apt-get", "install", "-y", "git", "binutils"])
        .with_exec(["pip", "install", "poetry"])
        .with_mounted_directory(
            "/airbyte",
            dagger_client.host().directory(
                ".",
                exclude=["**/__pycache__", "**/.pytest_cache", "**/.venv", "**.log", "**/.gradle"],
                include=DIRECTORIES_TO_MOUNT,
            ),
        )
        .with_workdir(f"/airbyte/airbyte-ci/connectors/pipelines")
        .with_exec(["poetry", "install", "--with", "dev"])
        .with_exec(["poetry",
            "run",
            "pyinstaller",
            "--collect-all",
            "pipelines",
            "--collect-all",
            "beartype",
            "--collect-all",
            "dagger",
            "--hidden-import",
            "strawberry",
            "--name",
            artifact_name,
            "--onefile",
            "pipelines/cli/airbyte_ci.py",
        ])
        .with_exec([f"./dist/{artifact_name}", "--version"])
        .with_exec(["ls", "-la", "dist"])
    )

    binary_file = container.file(f"./dist/{artifact_name}")
    gcs_folder_name = "airbyte-ci-releases"
    file_paths_to_upload = [
        f"{gcs_folder_name}/{artifact_name}-latest",
        f"{gcs_folder_name}/{artifact_name}-{CURRENT_VERSION}",
    ]

    for file_path in file_paths_to_upload:
        await upload_to_gcs(
            dagger_client=dagger_client,
            file_to_upload=binary_file,
            key=file_path,
            bucket=ci_artifact_bucket_name,
            gcs_credentials=ci_gcs_credentials_secret,
        )

async def run_release(ci_artifact_bucket_name: str, ci_gcs_credentials: str):
    """
    Build the airbyte-ci binary
    """
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as dagger_client:
        ci_gcs_credentials_secret = dagger_client.set_secret("ci_gcs_credentials", ci_gcs_credentials)

        async with anyio.create_task_group() as tg_main:
            for platform_name, image in PLATFORMS_TO_BUILD.items():
                tg_main.start_soon(
                    create_airbyte_ci_release,
                    dagger_client,
                    ci_gcs_credentials_secret,
                    ci_artifact_bucket_name,
                    image,
                    platform_name
                )

        return True

