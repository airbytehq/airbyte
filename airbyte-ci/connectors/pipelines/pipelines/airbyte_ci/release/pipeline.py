import sys
import anyio
import dagger
from pipelines.dagger.actions.remote_storage import upload_to_gcs

PLATFORMS_TO_BUILD = {
    "airbyte_ci_debian": "python:3.10-slim",
    "airbyte_ci_macos": "arm64v8/python:3.10-slim",
}

DIRECTORIES_TO_MOUNT = [".git", "airbyte-ci"]

async def create_airbyte_ci_release(
    dagger_client: dagger.Client,
    ci_gcs_credentials_secret: dagger.Secret,
    ci_artifact_bucket_name: str,
    image: str,
    output_filename: str
):
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
            output_filename,
            "--onefile",
            "pipelines/cli/airbyte_ci.py",
        ])
        .with_exec([f"./dist/{output_filename}", "--version"])
        .with_exec(["ls", "-la", "dist"])
    )

    await upload_to_gcs(
        dagger_client=dagger_client,
        file_to_upload=container.file(f"./dist/{output_filename}"),
        key=f"airbyte-ci-releases/{output_filename}",
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
            for output_filename, image in PLATFORMS_TO_BUILD.items():
                tg_main.start_soon(
                    create_airbyte_ci_release,
                    dagger_client,
                    ci_gcs_credentials_secret,
                    ci_artifact_bucket_name,
                    image,
                    output_filename
                )

        return True

