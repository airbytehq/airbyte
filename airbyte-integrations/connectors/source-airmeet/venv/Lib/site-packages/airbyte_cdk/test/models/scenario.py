# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Run acceptance tests in PyTest.

These tests leverage the same `acceptance-test-config.yml` configuration files as the
acceptance tests in CAT, but they run in PyTest instead of CAT. This allows us to run
the acceptance tests in the same local environment as we are developing in, speeding
up iteration cycles.
"""

from __future__ import annotations

import json
import tempfile
from contextlib import contextmanager, suppress
from pathlib import Path  # noqa: TC003  # Pydantic needs this (don't move to 'if typing' block)
from typing import TYPE_CHECKING, Any, Literal, cast

import yaml
from pydantic import BaseModel, ConfigDict

from airbyte_cdk.test.models.outcome import ExpectedOutcome

if TYPE_CHECKING:
    from collections.abc import Generator


class ConnectorTestScenario(BaseModel):
    """Acceptance test scenario, as a Pydantic model.

    This class represents an acceptance test scenario, which is a single test case
    that can be run against a connector. It is used to deserialize and validate the
    acceptance test configuration file.
    """

    # Allows the class to be hashable, which PyTest will require
    # when we use to parameterize tests.
    model_config = ConfigDict(frozen=True)

    class AcceptanceTestExpectRecords(BaseModel):
        path: Path
        exact_order: bool = False

    class AcceptanceTestFileTypes(BaseModel):
        skip_test: bool
        bypass_reason: str

    class AcceptanceTestEmptyStream(BaseModel):
        name: str
        bypass_reason: str | None = None

        # bypass reason does not affect equality
        def __hash__(self) -> int:
            return hash(self.name)

    config_path: Path | None = None
    config_dict: dict[str, Any] | None = None

    _id: str | None = None  # Used to override the default ID generation

    configured_catalog_path: Path | None = None
    empty_streams: list[AcceptanceTestEmptyStream] | None = None
    timeout_seconds: int | None = None
    expect_records: AcceptanceTestExpectRecords | None = None
    file_types: AcceptanceTestFileTypes | None = None
    status: Literal["succeed", "failed", "exception"] | None = None

    def get_config_dict(
        self,
        *,
        connector_root: Path,
        empty_if_missing: bool,
    ) -> dict[str, Any]:
        """Return the config dictionary.

        If a config dictionary has already been loaded, return it. Otherwise, load
        the config file and return the dictionary.

        If `self.config_dict` and `self.config_path` are both `None`:
        - return an empty dictionary if `empty_if_missing` is True
        - raise a ValueError if `empty_if_missing` is False
        """
        if self.config_dict is not None:
            return self.config_dict

        if self.config_path is not None:
            config_path = self.config_path
            if not config_path.is_absolute():
                # We usually receive a relative path here. Let's resolve it.
                config_path = (connector_root / self.config_path).resolve().absolute()

            return cast(
                dict[str, Any],
                yaml.safe_load(config_path.read_text()),
            )

        if empty_if_missing:
            return {}

        raise ValueError("No config dictionary or path provided.")

    @property
    def expected_outcome(self) -> ExpectedOutcome:
        """Whether the test scenario expects an exception to be raised.

        Returns True if the scenario expects an exception, False if it does not,
        and None if there is no set expectation.
        """
        return ExpectedOutcome.from_status_str(self.status)

    @property
    def id(self) -> str:
        """Return a unique identifier for the test scenario.

        This is used by PyTest to identify the test scenario.
        """
        if self._id:
            return self._id

        if self.config_path:
            return self.config_path.stem

        return str(hash(self))

    def __str__(self) -> str:
        return f"'{self.id}' Test Scenario"

    @contextmanager
    def with_temp_config_file(
        self,
        connector_root: Path,
    ) -> Generator[Path, None, None]:
        """Yield a temporary JSON file path containing the config dict and delete it on exit."""
        config = self.get_config_dict(
            empty_if_missing=True,
            connector_root=connector_root,
        )
        with tempfile.NamedTemporaryFile(
            prefix="config-",
            suffix=".json",
            mode="w",
            delete=False,  # Don't fail if cannot delete the file on exit
            encoding="utf-8",
        ) as temp_file:
            temp_file.write(json.dumps(config))
            temp_file.flush()
            # Allow the file to be read by other processes
            temp_path = Path(temp_file.name)
            temp_path.chmod(temp_path.stat().st_mode | 0o444)
            yield temp_path

        # attempt cleanup, ignore errors
        with suppress(OSError):
            temp_path.unlink()

    def without_expected_outcome(self) -> ConnectorTestScenario:
        """Return a copy of the scenario that does not expect failure or success.

        This is useful when running multiple steps, to defer the expectations to a later step.
        """
        return ConnectorTestScenario(
            **self.model_dump(exclude={"status"}),
        )

    def with_expecting_failure(self) -> ConnectorTestScenario:
        """Return a copy of the scenario that expects failure.

        This is useful when deriving new scenarios from existing ones.
        """
        if self.status == "failed":
            return self

        return ConnectorTestScenario(
            **self.model_dump(exclude={"status"}),
            status="failed",
        )

    def with_expecting_success(self) -> ConnectorTestScenario:
        """Return a copy of the scenario that expects success.

        This is useful when deriving new scenarios from existing ones.
        """
        if self.status == "succeed":
            return self

        return ConnectorTestScenario(
            **self.model_dump(exclude={"status"}),
            status="succeed",
        )

    @property
    def requires_creds(self) -> bool:
        """Return True if the scenario requires credentials to run."""
        return bool(self.config_path and "secrets" in self.config_path.parts)
