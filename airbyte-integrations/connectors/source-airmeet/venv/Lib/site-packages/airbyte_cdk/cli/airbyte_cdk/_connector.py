# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""CLI command for `airbyte-cdk`."""

USAGE = """CLI command for `airbyte-cdk`.

This CLI interface allows you to interact with your connector, including
testing and running commands.

**Basic Usage:**

```bash
airbyte-cdk --help
airbyte-cdk connector --help
airbyte-cdk manifest --help
```

**Running Statelessly:**

You can run the latest version of this CLI, from any machine, using `pipx` or `uvx`:

```bash
# Run the latest version of the CLI:
pipx run airbyte-cdk connector --help
uvx airbyte-cdk connector --help

# Run from a specific CDK version:
pipx run airbyte-cdk==6.5.1 connector --help
uvx airbyte-cdk==6.5.1 connector --help
```

**Running within your virtualenv:**

You can also run from your connector's virtualenv:

```bash
poetry run airbyte-cdk connector --help
```

"""

import os
import sys
from pathlib import Path
from types import ModuleType

import rich_click as click

from airbyte_cdk.test.standard_tests.util import create_connector_test_suite

# from airbyte_cdk.test.standard_tests import pytest_hooks
from airbyte_cdk.utils.connector_paths import (
    find_connector_root_from_name,
    resolve_connector_name_and_directory,
)

click.rich_click.TEXT_MARKUP = "markdown"

pytest: ModuleType | None
try:
    import pytest
except ImportError:
    pytest = None
    # Handle the case where pytest is not installed.
    # This prevents import errors when running the script without pytest installed.
    # We will raise an error later if pytest is required for a given command.


TEST_FILE_TEMPLATE = '''
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""FAST Airbyte Standard Tests for the {connector_name} connector."""

#from airbyte_cdk.test.standard_tests import {base_class_name}
from airbyte_cdk.test.standard_tests.util import create_connector_test_suite
from pathlib import Path

pytest_plugins = [
    "airbyte_cdk.test.standard_tests.pytest_hooks",
]

TestSuite = create_connector_test_suite(
    connector_directory=Path(),
)

# Uncomment the following lines to create a custom test suite class:
#
# class TestSuite({base_class_name}):
#     """Test suite for the `{connector_name}` connector.
#
#     This class inherits from `{base_class_name}` and implements all of the tests in the suite.
#
#     As long as the class name starts with "Test", pytest will automatically discover and run the
#     tests in this class.
#     """
'''


@click.group(
    name="connector",
    help=__doc__.replace("\n", "\n\n"),  # Render docstring as help text (markdown)
)
def connector_cli_group() -> None:
    """Connector related commands."""
    pass


@connector_cli_group.command("test")
@click.argument(
    "connector",
    required=False,
    type=str,
    metavar="[CONNECTOR]",
)
@click.option(
    "--collect-only",
    is_flag=True,
    default=False,
    help="Only collect tests, do not run them.",
)
@click.option(
    "--pytest-arg",
    "pytest_args",  # ← map --pytest-arg into pytest_args
    type=str,
    multiple=True,
    help="Additional argument(s) to pass to pytest. Can be specified multiple times.",
)
@click.option(
    "--no-creds",
    is_flag=True,
    default=False,
    help="Skip tests that require credentials (marked with 'requires_creds').",
)
def connector_test(
    connector: str | Path | None = None,
    *,
    collect_only: bool = False,
    pytest_args: list[str] | None = None,
    no_creds: bool = False,
) -> None:
    """Run connector tests.

    This command runs the standard connector tests for a specific connector.

    [CONNECTOR] can be a connector name (e.g. 'source-pokeapi'), a path to a connector directory, or omitted to use the current working directory.
    If a string containing '/' is provided, it is treated as a path. Otherwise, it is treated as a connector name.

    If no connector name or directory is provided, we will look within the current working
    directory. If the current working directory is not a connector directory (e.g. starting
    with 'source-') and no connector name or path is provided, the process will fail.
    """
    click.echo("Connector test command executed.")
    connector_name, connector_directory = resolve_connector_name_and_directory(connector)

    pytest_args = pytest_args or []
    if collect_only:
        pytest_args.append("--collect-only")

    if no_creds:
        pytest_args.extend(["-m", "not requires_creds"])

    run_connector_tests(
        connector_name=connector_name,
        connector_directory=connector_directory,
        extra_pytest_args=pytest_args,
    )


def run_connector_tests(
    connector_name: str,
    connector_directory: Path,
    extra_pytest_args: list[str],
) -> None:
    if pytest is None:
        raise ImportError(
            "pytest is not installed. Please install pytest to run the connector tests."
        )

    connector_test_suite = create_connector_test_suite(
        connector_name=connector_name if not connector_directory else None,
        connector_directory=connector_directory,
    )

    pytest_args: list[str] = ["-p", "airbyte_cdk.test.standard_tests.pytest_hooks"]
    if connector_directory:
        pytest_args.append(f"--rootdir={connector_directory}")
        os.chdir(str(connector_directory))
    else:
        print("No connector directory provided. Running tests in the current directory.")

    file_text = TEST_FILE_TEMPLATE.format(
        base_class_name=connector_test_suite.__bases__[0].__name__,
        connector_name=connector_name,
    )
    test_file_path = Path() / ".tmp" / "integration_tests/test_airbyte_standards.py"
    test_file_path = test_file_path.resolve().absolute()
    test_file_path.parent.mkdir(parents=True, exist_ok=True)
    test_file_path.write_text(file_text)

    if extra_pytest_args:
        pytest_args.extend(extra_pytest_args)

    pytest_args.append(str(test_file_path))

    test_results_dir = connector_directory / "build" / "test-results"
    test_results_dir.mkdir(parents=True, exist_ok=True)
    junit_xml_path = test_results_dir / "standard-tests-junit.xml"
    pytest_args.extend(["--junitxml", str(junit_xml_path)])

    click.echo(f"Running tests from connector directory: {connector_directory}...")
    click.echo(f"Test file: {test_file_path}")
    click.echo(f"Pytest args: {pytest_args}")
    click.echo("Invoking Pytest...")
    exit_code = pytest.main(
        pytest_args,
        plugins=[],
    )
    sys.exit(exit_code)


__all__ = [
    "connector_cli_group",
]
