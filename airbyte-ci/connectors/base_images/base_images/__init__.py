#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import sys

from base_images.errors import BaseImageVersionError
from rich.console import Console

console = Console()

try:
    from base_images import python  # , java_bases
except BaseImageVersionError as e:
    # This error occurs if a base image version class name does not follow semver.
    # We handle the error for nice console output.
    # It might happen if a developer implement a new version class without following our required class name convention.
    console.log(f":cross_mark: {e}", style="bold red")
    sys.exit(1)

PYTHON_BASE_IMAGES = python.ALL_BASE_IMAGES
LATEST_PYTHON_BASE_IMAGE = next(iter(PYTHON_BASE_IMAGES.values()))
ALL_BASE_IMAGES = {**python.ALL_BASE_IMAGES}  # , **java_bases.ALL_BASE_IMAGES}
