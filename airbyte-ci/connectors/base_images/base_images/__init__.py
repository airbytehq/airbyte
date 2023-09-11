#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import sys
from itertools import product
from pathlib import Path

import anyio
import dagger
from base_images import common, consts, utils
from rich.console import Console
from rich.status import Status

console = Console()

try:
    from base_images import python_bases  # , java_bases
except common.BaseImageVersionError as e:
    console.log(f":cross_mark: {e}", style="bold red")
    sys.exit(1)

ALL_BASE_IMAGES = {**python_bases.ALL_BASE_IMAGES}  # , **java_bases.ALL_BASE_IMAGES}


async def run_all_sanity_checks(status: Status) -> bool:
    """
    Runs sanity checks on all the base images.
    """
    errors = []
    async with dagger.Connection(dagger.Config()) as dagger_client:
        for platform, BaseImageVersion in product(consts.SUPPORTED_PLATFORMS, ALL_BASE_IMAGES.values()):
            status.update(f":mag_right: Running sanity checks on {BaseImageVersion.name_with_tag} for {platform}")
            try:
                await BaseImageVersion(dagger_client, platform).run_sanity_checks()
                console.log(
                    f":white_check_mark: Successfully ran sanity check on {BaseImageVersion.name_with_tag} for {platform}", highlight=False
                )
            except common.SanityCheckError as sanity_check_error:
                console.log(
                    f":cross_mark: Sanity check failure on {BaseImageVersion.name_with_tag} for {platform}: {sanity_check_error}",
                    style="bold red",
                    highlight=False,
                )
                errors.append(sanity_check_error)

    return not errors


def build():
    """
    Runs sanity checks on all the base images and writes the changelog.
    """
    with console.status("Building the project", spinner="hamburger") as status:
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
