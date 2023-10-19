#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import anyio
import click
from pipelines.airbyte_ci.test.pipeline import run_test


@click.command()
@click.argument("poetry_package_path")
@click.option("--test-directory", default="tests", help="The directory containing the tests to run.")
def test(
    poetry_package_path: str,
    test_directory: str,
):
    """Runs the tests for the given airbyte-ci package.

    Args:
        poetry_package_path (str): Path to the poetry package to test, relative to airbyte-ci directory.
        test_directory (str): The directory containing the tests to run.
    """
    success = anyio.run(run_test, poetry_package_path, test_directory)
    if not success:
        click.Abort()
