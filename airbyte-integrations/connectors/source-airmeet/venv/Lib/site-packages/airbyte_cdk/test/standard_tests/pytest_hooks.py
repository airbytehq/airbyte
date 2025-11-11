# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Pytest hooks for Airbyte CDK tests.

These hooks are used to customize the behavior of pytest during test discovery and execution.

To use these hooks within a connector, add the following lines to the connector's `conftest.py`
file, or to another file that is imported during test discovery:

```python
pytest_plugins = [
    "airbyte_cdk.test.standard_tests.pytest_hooks",
]
```
"""

from typing import Literal, cast

import pytest


@pytest.fixture
def connector_image_override(request: pytest.FixtureRequest) -> str | None:
    """Return the value of --connector-image, or None if not set."""
    return cast(str | None, request.config.getoption("--connector-image"))


@pytest.fixture
def read_from_streams(
    request: pytest.FixtureRequest,
) -> Literal["all", "none", "default"] | list[str]:
    """Specify if the test should read from streams.

    The input can be one of the following:
    - [Omitted] - Default to False, meaning no streams will be read.
    - `--read-from-streams`: Read from all suggested streams.
    - `--read-from-streams=true`: Read from all suggested streams.
    - `--read-from-streams=suggested`: Read from all suggested streams.
    - `--read-from-streams=default`: Read from all suggested streams.
    - `--read-from-streams=all`: Read from all streams.
    - `--read-from-streams=stream1,stream2`: Read from the specified streams only.
    - `--read-from-streams=false`: Do not read from any streams.
    - `--read-from-streams=none`: Do not read from any streams.
    """
    input_val: str = request.config.getoption(
        "--read-from-streams",
        default="default",  # type: ignore
    )  # type: ignore

    if isinstance(input_val, str):
        if input_val.lower() == "false":
            return "none"
        if input_val.lower() in ["true", "suggested", "default"]:
            # Default to 'default' (suggested) streams if the input is 'true', 'suggested', or
            # 'default'.
            # This is the default behavior if the option is not set.
            return "default"
        if input_val.lower() == "all":
            # This will sometimes fail if the account doesn't have permissions
            # to premium or restricted stream data.
            return "all"

        # If the input is a comma-separated list, split it into a list.
        # This will return a one-element list if the input is a single stream name.
        return input_val.split(",")

    # Else, probably a bool; return it as is.
    return input_val or "none"


@pytest.fixture
def read_scenarios(
    request: pytest.FixtureRequest,
) -> list[str] | Literal["all", "default"]:
    """Return the value of `--read-scenarios`.

    This argument is ignored if `--read-from-streams` is False or not set.

    The input can be one of the following:
    - [Omitted] - Default to 'config.json', meaning the default scenario will be read.
    - `--read-scenarios=all`: Read all scenarios.
    - `--read-scenarios=none`: Read no scenarios. (Overrides `--read-from-streams`, if set.)
    - `--read-scenarios=scenario1,scenario2`: Read the specified scenarios only.

    """
    input_val = cast(
        str,
        request.config.getoption(
            "--read-scenarios",
            default="default",  # type: ignore
        ),
    )

    if input_val.lower() == "default":
        # Default config scenario is always 'config.json'.
        return "default"

    if input_val.lower() == "none":
        # Default config scenario is always 'config.json'.
        return []

    return (
        [
            scenario_name.strip().lower().removesuffix(".json")
            for scenario_name in input_val.split(",")
        ]
        if input_val
        else []
    )


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add --connector-image to pytest's CLI."""
    parser.addoption(
        "--connector-image",
        action="store",
        default=None,
        help="Use this pre-built connector Docker image instead of building one.",
    )
    parser.addoption(
        "--read-from-streams",
        action="store",
        default=None,
        help=read_from_streams.__doc__,
    )
    parser.addoption(
        "--read-scenarios",
        action="store",
        default="default",
        help=read_scenarios.__doc__,
    )


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """A helper for pytest_generate_tests hook.

    If a test method (in a class subclassed from our base class)
    declares an argument 'scenario', this function retrieves the
    'scenarios' attribute from the test class and parametrizes that
    test with the values from 'scenarios'.

    ## Usage

    ```python
    from airbyte_cdk.test.standard_tests.connector_base import (
        generate_tests,
        ConnectorTestSuiteBase,
    )

    def pytest_generate_tests(metafunc):
        generate_tests(metafunc)

    class TestMyConnector(ConnectorTestSuiteBase):
        ...

    ```
    """
    # Check if the test function requires an 'scenario' argument
    if "scenario" in metafunc.fixturenames:
        # Retrieve the test class
        test_class = metafunc.cls
        if test_class is None:
            return

        # Check that the class is compatible with our test suite
        scenarios_attr = getattr(test_class, "get_scenarios", None)
        if scenarios_attr is None:
            raise ValueError(
                f"Test class {test_class} does not have a 'scenarios' attribute. "
                "Please define the 'scenarios' attribute in the test class."
            )

        # Get the scenarios defined or discovered in the test class
        scenarios = test_class.get_scenarios()

        # Create pytest.param objects with special marks as needed
        parametrized_scenarios = [
            pytest.param(
                scenario,
                marks=[pytest.mark.requires_creds] if scenario.requires_creds else [],
            )
            for scenario in scenarios
        ]

        # Parametrize the 'scenario' argument with the scenarios
        metafunc.parametrize(
            "scenario",
            parametrized_scenarios,
            ids=[str(scenario) for scenario in scenarios],
        )
