# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import shlex
import subprocess
import sys
from abc import ABC, abstractmethod
from contextlib import contextmanager, suppress
from pathlib import Path
from shutil import rmtree
from typing import IO, TYPE_CHECKING, Any, NoReturn, cast

from rich import print

from airbyte_lib import exceptions as exc
from airbyte_lib.registry import ConnectorMetadata
from airbyte_lib.telemetry import SourceTelemetryInfo, SourceType


if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Iterator


_LATEST_VERSION = "latest"


class Executor(ABC):
    def __init__(
        self,
        *,
        name: str | None = None,
        metadata: ConnectorMetadata | None = None,
        target_version: str | None = None,
    ) -> None:
        """Initialize a connector executor.

        The 'name' param is required if 'metadata' is None.
        """
        if not name and not metadata:
            raise exc.AirbyteLibInternalError(message="Either name or metadata must be provided.")

        self.name: str = name or cast(ConnectorMetadata, metadata).name  # metadata is not None here
        self.metadata: ConnectorMetadata | None = metadata
        self.enforce_version: bool = target_version is not None

        self.reported_version: str | None = None
        self.target_version: str | None = None
        if target_version:
            if metadata and target_version == _LATEST_VERSION:
                self.target_version = metadata.latest_available_version
            else:
                self.target_version = target_version

    @abstractmethod
    def execute(self, args: list[str]) -> Iterator[str]:
        pass

    @abstractmethod
    def ensure_installation(self, *, auto_fix: bool = True) -> None:
        _ = auto_fix
        pass

    @abstractmethod
    def install(self) -> None:
        pass

    @abstractmethod
    def get_telemetry_info(self) -> SourceTelemetryInfo:
        pass

    @abstractmethod
    def uninstall(self) -> None:
        pass


@contextmanager
def _stream_from_subprocess(args: list[str]) -> Generator[Iterable[str], None, None]:
    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )

    def _stream_from_file(file: IO[str]) -> Generator[str, Any, None]:
        while True:
            line = file.readline()
            if not line:
                break
            yield line

    if process.stdout is None:
        raise exc.AirbyteSubprocessError(
            message="Subprocess did not return a stdout stream.",
            context={
                "args": args,
                "returncode": process.returncode,
            },
        )
    try:
        yield _stream_from_file(process.stdout)
    finally:
        # Close the stdout stream
        if process.stdout:
            process.stdout.close()

        # Terminate the process if it is still running
        if process.poll() is None:  # Check if the process is still running
            process.terminate()
            try:
                # Wait for a short period to allow process to terminate gracefully
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # If the process does not terminate within the timeout, force kill it
                process.kill()

        # Now, the process is either terminated or killed. Check the exit code.
        exit_code = process.wait()

        # If the exit code is not 0 or -15 (SIGTERM), raise an exception
        if exit_code not in (0, -15):
            raise exc.AirbyteSubprocessFailedError(
                run_args=args,
                exit_code=exit_code,
            )


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
        return self._get_venv_path() / "bin" / self.name

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
        # TODO: Refactor installation so that this can just live in the Source class.
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

        pip_path = str(self._get_venv_path() / "bin" / "pip")
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
        self.reported_version = self._get_installed_version(raise_on_error=False, recheck=True)
        print(
            f"Connector '{self.name}' installed successfully!\n"
            f"For more information, see the {self.name} documentation:\n"
            f"{self.docs_url}#reference\n"
        )

    def _get_installed_version(
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
                raise exc.AirbyteLibInternalError(
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

    @property
    def interpreter_path(self) -> Path:
        return self._get_venv_path() / "bin" / "python"

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
            self.reported_version = self._get_installed_version()

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

    def execute(self, args: list[str]) -> Iterator[str]:
        connector_path = self._get_connector_path()

        with _stream_from_subprocess([str(connector_path), *args]) as stream:
            yield from stream

    def get_telemetry_info(self) -> SourceTelemetryInfo:
        return SourceTelemetryInfo(
            name=self.name,
            type=SourceType.VENV,
            version=self.reported_version,
        )


class PathExecutor(Executor):
    def __init__(
        self,
        name: str | None = None,
        *,
        path: Path,
        target_version: str | None = None,
    ) -> None:
        """Initialize a connector executor that runs a connector from a local path.

        If path is simply the name of the connector, it will be expected to exist in the current
        PATH or in the current working directory.
        """
        self.path: Path = path
        name = name or path.name
        super().__init__(name=name, target_version=target_version)

    def ensure_installation(
        self,
        *,
        auto_fix: bool = True,
    ) -> None:
        """Ensure that the connector executable can be found.

        The auto_fix parameter is ignored for this executor type.
        """
        _ = auto_fix
        try:
            self.execute(["spec"])
        except Exception as e:
            # TODO: Improve error handling. We should try to distinguish between
            #       a connector that is not installed and a connector that is not
            #       working properly.
            raise exc.AirbyteConnectorExecutableNotFoundError(
                connector_name=self.name,
            ) from e

    def install(self) -> NoReturn:
        raise exc.AirbyteConnectorInstallationError(
            message="Connector cannot be installed because it is not managed by airbyte-lib.",
            connector_name=self.name,
        )

    def uninstall(self) -> NoReturn:
        raise exc.AirbyteConnectorInstallationError(
            message="Connector cannot be uninstalled because it is not managed by airbyte-lib.",
            connector_name=self.name,
        )

    def execute(self, args: list[str]) -> Iterator[str]:
        with _stream_from_subprocess([str(self.path), *args]) as stream:
            yield from stream

    def get_telemetry_info(self) -> SourceTelemetryInfo:
        return SourceTelemetryInfo(
            str(self.name),
            SourceType.LOCAL_INSTALL,
            version=self.reported_version,
        )
