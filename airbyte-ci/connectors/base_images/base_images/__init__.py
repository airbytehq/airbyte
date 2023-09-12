#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import sys
from itertools import product
from pathlib import Path
from typing import List

import anyio
import dagger
from base_images import consts, errors, utils
from rich.console import Console
from rich.status import Status

console = Console()

try:
    from base_images import python_bases  # , java_bases
except errors.BaseImageVersionError as e:
    # This error occurs if a base image version class name does not follow semver.
    # We handle the error for nice console output.
    # It might happen if a developer implement a new version class without following our required class name convention.
    console.log(f":cross_mark: {e}", style="bold red")
    sys.exit(1)

ALL_BASE_IMAGES = {**python_bases.ALL_BASE_IMAGES}  # , **java_bases.ALL_BASE_IMAGES}


async def run_all_sanity_checks(status: Status) -> bool:
    """
    Runs sanity checks on all the base images.
    Sanity checks are declared in the base image version classes by implementing the run_sanity_checks function.
    Sanity checks are command executed on the base image container, we check the output of these command to make sure the base image is working as expected.
    """
    sanity_check_errors: List[errors.SanityCheckError] = []
    dagger_config = dagger.Config(log_output=sys.stderr) if consts.DEBUG else dagger.Config()
    async with dagger.Connection(dagger_config) as dagger_client:
        for platform, BaseImageVersion in product(consts.SUPPORTED_PLATFORMS, ALL_BASE_IMAGES.values()):
            status.update(f":mag_right: Running sanity checks on {BaseImageVersion.name_with_tag} for {platform}")
            try:
                await BaseImageVersion(dagger_client, platform).run_sanity_checks_for_version()
                console.log(
                    f":white_check_mark: Successfully ran sanity check on {BaseImageVersion.name_with_tag} for {platform}", highlight=False
                )
            except errors.SanityCheckError as sanity_check_error:
                console.log(
                    f":cross_mark: Sanity check failure on {BaseImageVersion.name_with_tag} for {platform}: {sanity_check_error}",
                    style="bold red",
                    highlight=False,
                )
                sanity_check_errors.append(sanity_check_error)

    return not sanity_check_errors


def build():
    """
    This function is called by the build command, currently via poetry run build.
    It's currently meant to be run locally by developers to generate the changelog and run sanity checks.
    It can eventually be run in CI to generate the changelog and run sanity checks.

    1. Run sanity checks on all the base images.
    2. Write the changelog for the python base image.

    This function calls Dagger to run the sanity checks.
    If you don't have the base base image locally it will be pulled, which can take a while.
    Subsequent runs will be faster as the base images layers and sanity checks layers will be cached locally.
    """
    try:
        with console.status("Building the project", spinner="bouncingBall") as status:
            status.update("Running sanity checks on all the base images")
            if not anyio.run(run_all_sanity_checks, status):
                console.log(":bomb: Sanity checks failed, aborting the build.", style="bold red")
                sys.exit(1)
            console.log(":tada: Successfully ran sanity checks on all the base images.")
            python_changelog_path = Path(consts.PROJECT_DIR / "CHANGELOG_PYTHON_CONNECTOR_BASE_IMAGE.md")
            status.update(f"Writing the changelog to {python_changelog_path}")
            utils.write_changelog_file(
                python_changelog_path, python_bases.AirbytePythonConnectorBaseImage.image_name, python_bases.ALL_BASE_IMAGES
            )
            console.log(
                f":memo: Wrote the updated changelog to {python_changelog_path}. [bold red]Please commit and push it![/bold red]",
            )
    except KeyboardInterrupt:
        console.log(":bomb: Aborted the build.", style="bold red")
        sys.exit(1)
