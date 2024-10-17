# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import shlex
import subprocess
import sys
from contextlib import suppress
from pathlib import Path
from shutil import rmtree
from typing import TYPE_CHECKING, Literal

from overrides import overrides
from rich import print  # noqa: A004  # Allow shadowing the built-in

from airbyte_cdk.sql import exceptions as exc
from airbyte_cdk.sql._executors.base import Executor
from airbyte_cdk.sql._util.meta import is_windows
from airbyte_cdk.sql._util.telemetry import EventState, log_install_state
from airbyte_cdk.sql._util.venv_util import get_bin_dir


if TYPE_CHECKING:
    from airbyte_cdk.sql.sources.registry import ConnectorMetadata


class VenvExecutor(Executor):
    def __init__(
        self,
        name: str | None = None,
        *,
        metadata: ConnectorMetadata | None = None,
        target_version: str | None = None,
        pip_url: str | None = None,
        install_root: Path | None = None,
    ) -> None:
        """Initialize a connector executor that runs a connector in a virtual environment.

        Args:
            name: The name of the connector.
            metadata: (Optional.) The metadata of the connector.
            target_version: (Optional.) The version of the connector to install.
            pip_url: (Optional.) The pip URL of the connector to install.
            install_root: (Optional.) The root directory where the virtual environment will be
                created. If not provided, the current working directory will be used.
        """
        super().__init__(name=name, metadata=metadata, target_version=target_version)

        if not pip_url and metadata and not metadata.pypi_package_name:
            raise exc.AirbyteConnectorNotPyPiPublishedError(
                connector_name=self.name,
                context={
                    "metadata": metadata,
                },
            )

        self.pip_url = pip_url or (
            metadata.pypi_package_name
            if metadata and metadata.pypi_package_name
            else f"airbyte-{self.name}"
        )
        self.install_root = install_root or Path.cwd()

    def _get_venv_name(self) -> str:
        return f".venv-{self.name}"

    def _get_venv_path(self) -> Path:
        return self.install_root / self._get_venv_name()

    def _get_connector_path(self) -> Path:
        suffix: Literal[".exe", ""] = ".exe" if is_windows() else ""
        return get_bin_dir(self._get_venv_path()) / (self.name + suffix)

    @property
    def interpreter_path(self) -> Path:
        suffix: Literal[".exe", ""] = ".exe" if is_windows() else ""
        return get_bin_dir(self._get_venv_path()) / ("python" + suffix)

    def _run_subprocess_and_raise_on_failure(self, args: list[str]) -> None:
        result = subprocess.run(
            args,
            check=False,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            raise exc.AirbyteSubprocessFailedError(
                run_args=args,
                exit_code=result.returncode,
                log_text=result.stderr.decode("utf-8"),
            )

    def uninstall(self) -> None:
        if self._get_venv_path().exists():
            rmtree(str(self._get_venv_path()))

        self.reported_version = None  # Reset the reported version from the previous installation

    @property
    def docs_url(self) -> str:
        """Get the URL to the connector's documentation."""
        return "https://docs.airbyte.com/integrations/sources/" + self.name.lower().replace(
            "source-", ""
        )

    def install(self) -> None:
        """Install the connector in a virtual environment.

        After installation, the installed version will be stored in self.reported_version.
        """
        self._run_subprocess_and_raise_on_failure(
            [sys.executable, "-m", "venv", str(self._get_venv_path())]
        )

        pip_path = str(get_bin_dir(self._get_venv_path()) / "pip")
        print(
            f"Installing '{self.name}' into virtual environment '{self._get_venv_path()!s}'.\n"
            f"Running 'pip install {self.pip_url}'...\n"
        )
        try:
            self._run_subprocess_and_raise_on_failure(
                args=[pip_path, "install", *shlex.split(self.pip_url)]
            )
        except exc.AirbyteSubprocessFailedError as ex:
            # If the installation failed, remove the virtual environment
            # Otherwise, the connector will be considered as installed and the user may not be able
            # to retry the installation.
            with suppress(exc.AirbyteSubprocessFailedError):
                self.uninstall()

            raise exc.AirbyteConnectorInstallationError from ex

        # Assuming the installation succeeded, store the installed version
        self.reported_version = self.get_installed_version(raise_on_error=False, recheck=True)
        log_install_state(self.name, state=EventState.SUCCEEDED)
        print(
            f"Connector '{self.name}' installed successfully!\n"
            f"For more information, see the {self.name} documentation:\n"
            f"{self.docs_url}#reference\n"
        )

    @overrides
    def get_installed_version(
        self,
        *,
        raise_on_error: bool = False,
        recheck: bool = False,
    ) -> str | None:
        """Detect the version of the connector installed.

        Returns the version string if it can be detected, otherwise None.

        If raise_on_error is True, raise an exception if the version cannot be detected.

        If recheck if False and the version has already been detected, return the cached value.

        In the venv, we run the following:
        > python -c "from importlib.metadata import version; print(version('<connector-name>'))"
        """
        if not recheck and self.reported_version:
            return self.reported_version

        connector_name = self.name
        if not self.interpreter_path.exists():
            # No point in trying to detect the version if the interpreter does not exist
            if raise_on_error:
                raise exc.AirbyteInternalError(
                    message="Connector's virtual environment interpreter could not be found.",
                    context={
                        "interpreter_path": self.interpreter_path,
                    },
                )
            return None

        try:
            package_name = (
                self.metadata.pypi_package_name
                if self.metadata and self.metadata.pypi_package_name
                else f"airbyte-{connector_name}"
            )
            return subprocess.check_output(
                [
                    self.interpreter_path,
                    "-c",
                    f"from importlib.metadata import version; print(version('{package_name}'))",
                ],
                universal_newlines=True,
                stderr=subprocess.PIPE,  # Don't print to stderr
            ).strip()
        except Exception:
            if raise_on_error:
                raise

            return None

    def ensure_installation(
        self,
        *,
        auto_fix: bool = True,
    ) -> None:
        """Ensure that the connector is installed in a virtual environment.

        If not yet installed and if install_if_missing is True, then install.

        Optionally, verify that the installed version matches the target version.

        Note: Version verification is not supported for connectors installed from a
        local path.
        """
        # Store the installed version (or None if not installed)
        if not self.reported_version:
            self.reported_version = self.get_installed_version()

        original_installed_version = self.reported_version

        reinstalled = False
        venv_name = f".venv-{self.name}"
        if not self._get_venv_path().exists():
            if not auto_fix:
                raise exc.AirbyteConnectorInstallationError(
                    message="Virtual environment does not exist.",
                    connector_name=self.name,
                    context={
                        "venv_path": self._get_venv_path(),
                    },
                )

            # If the venv path does not exist, install.
            self.install()
            reinstalled = True

        elif not self._get_connector_path().exists():
            if not auto_fix:
                raise exc.AirbyteConnectorInstallationError(
                    message="Could not locate connector executable within the virtual environment.",
                    connector_name=self.name,
                    context={
                        "connector_path": self._get_connector_path(),
                    },
                )

            # If the connector path does not exist, uninstall and re-install.
            # This is sometimes caused by a failed or partial installation.
            print(
                "Connector executable not found within the virtual environment "
                f"at {self._get_connector_path()!s}.\nReinstalling..."
            )
            self.uninstall()
            self.install()
            reinstalled = True

        # By now, everything should be installed. Raise an exception if not.

        connector_path = self._get_connector_path()
        if not connector_path.exists():
            raise exc.AirbyteConnectorInstallationError(
                message="Connector's executable could not be found within the virtual environment.",
                connector_name=self.name,
                context={
                    "connector_path": self._get_connector_path(),
                },
            ) from FileNotFoundError(connector_path)

        if self.enforce_version:
            version_after_reinstall: str | None = None
            if self.reported_version != self.target_version:
                if auto_fix and not reinstalled:
                    # If we haven't already reinstalled above, reinstall now.
                    self.install()
                    reinstalled = True

                if reinstalled:
                    version_after_reinstall = self.reported_version

                # Check the version again
                if self.reported_version != self.target_version:
                    raise exc.AirbyteConnectorInstallationError(
                        message="Connector's reported version does not match the target version.",
                        connector_name=self.name,
                        context={
                            "venv_name": venv_name,
                            "target_version": self.target_version,
                            "original_installed_version": original_installed_version,
                            "version_after_reinstall": version_after_reinstall,
                        },
                    )

    @property
    def _cli(self) -> list[str]:
        """Get the base args of the CLI executable."""
        return [str(self._get_connector_path())]
