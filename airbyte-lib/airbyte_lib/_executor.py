# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import subprocess
import sys
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, NoReturn

from airbyte_lib import exceptions as exc
from airbyte_lib.telemetry import SourceTelemetryInfo, SourceType


if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, Iterator

    from airbyte_lib.registry import ConnectorMetadata


_LATEST_VERSION = "latest"


class Executor(ABC):
    def __init__(
        self,
        metadata: ConnectorMetadata,
        target_version: str | None = None,
    ) -> None:
        self.metadata = metadata
        self.enforce_version = target_version is not None
        if target_version is None or target_version == _LATEST_VERSION:
            self.target_version = metadata.latest_available_version
        else:
            self.target_version = target_version

    @abstractmethod
    def execute(self, args: list[str]) -> Iterator[str]:
        pass

    @abstractmethod
    def ensure_installation(self) -> None:
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
            raise exc.AirbyteSubprocessFailedError(exit_code=exit_code)


class VenvExecutor(Executor):
    def __init__(
        self,
        metadata: ConnectorMetadata,
        target_version: str | None = None,
        pip_url: str | None = None,
        *,
        install_if_missing: bool = False,
    ) -> None:
        super().__init__(metadata, target_version)
        self.install_if_missing = install_if_missing

        # This is a temporary install path that will be replaced with a proper package
        # name once they are published.
        # TODO: Replace with `f"airbyte-{self.metadata.name}"`
        self.pip_url = pip_url or f"../airbyte-integrations/connectors/{self.metadata.name}"

    def _get_venv_name(self) -> str:
        return f".venv-{self.metadata.name}"

    def _get_connector_path(self) -> Path:
        return Path(self._get_venv_name(), "bin", self.metadata.name)

    def _run_subprocess_and_raise_on_failure(self, args: list[str]) -> None:
        result = subprocess.run(args, check=False)
        if result.returncode != 0:
            raise exc.AirbyteConnectorInstallationError from exc.AirbyteSubprocessFailedError(
                exit_code=result.returncode
            )

    def uninstall(self) -> None:
        venv_name = self._get_venv_name()
        if Path(venv_name).exists():
            self._run_subprocess_and_raise_on_failure(["rm", "-rf", venv_name])

    def install(self) -> None:
        venv_name = self._get_venv_name()
        self._run_subprocess_and_raise_on_failure([sys.executable, "-m", "venv", venv_name])

        pip_path = str(Path(venv_name) / "bin" / "pip")

        self._run_subprocess_and_raise_on_failure([pip_path, "install", "-e", self.pip_url])

    def _get_installed_version(self) -> str:
        """Detect the version of the connector installed.

        In the venv, we run the following:
        > python -c "from importlib.metadata import version; print(version('<connector-name>'))"
        """
        venv_name = self._get_venv_name()
        connector_name = self.metadata.name
        return subprocess.check_output(
            [
                Path(venv_name) / "bin" / "python",
                "-c",
                f"from importlib.metadata import version; print(version('{connector_name}'))",
            ],
            universal_newlines=True,
        ).strip()

    def ensure_installation(
        self,
    ) -> None:
        """Ensure that the connector is installed in a virtual environment.

        If not yet installed and if install_if_missing is True, then install.

        Optionally, verify that the installed version matches the target version.

        Note: Version verification is not supported for connectors installed from a
        local path.
        """
        venv_name = f".venv-{self.metadata.name}"
        venv_path = Path(venv_name)
        if not venv_path.exists():
            if not self.install_if_missing:
                raise exc.AirbyteConnectorNotFoundError(
                    message="Connector not available and venv does not exist.",
                    guidance=(
                        "Please ensure the connector is pre-installed or consider enabling "
                        "`install_if_missing=True`."
                    ),
                    context={
                        "connector_name": self.metadata.name,
                        "venv_name": venv_name,
                    },
                )
            self.install()

        connector_path = self._get_connector_path()
        if not connector_path.exists():
            raise exc.AirbyteConnectorNotFoundError(
                connector_name=self.metadata.name,
                context={
                    "venv_name": venv_name,
                },
            ) from FileNotFoundError(connector_path)

        if self.enforce_version:
            installed_version = self._get_installed_version()
            if installed_version != self.target_version:
                # If the version doesn't match, reinstall
                self.install()

                # Check the version again
                version_after_install = self._get_installed_version()
                if version_after_install != self.target_version:
                    raise exc.AirbyteConnectorInstallationError(
                        connector_name=self.metadata.name,
                        context={
                            "venv_name": venv_name,
                            "target_version": self.target_version,
                            "installed_version": installed_version,
                            "version_after_install": version_after_install,
                        },
                    )

    def execute(self, args: list[str]) -> Iterator[str]:
        connector_path = self._get_connector_path()

        with _stream_from_subprocess([str(connector_path), *args]) as stream:
            yield from stream

    def get_telemetry_info(self) -> SourceTelemetryInfo:
        return SourceTelemetryInfo(self.metadata.name, SourceType.VENV, self.target_version)


class PathExecutor(Executor):
    def ensure_installation(self) -> None:
        try:
            self.execute(["spec"])
        except Exception as e:
            raise exc.AirbyteConnectorNotFoundError(
                connector_name=self.metadata.name,
            ) from e

    def install(self) -> NoReturn:
        raise exc.AirbyteConnectorInstallationError(
            message="Connector cannot be installed because it is not managed by airbyte-lib.",
            connector_name=self.metadata.name,
        )

    def uninstall(self) -> NoReturn:
        raise exc.AirbyteConnectorInstallationError(
            message="Connector cannot be uninstalled because it is not managed by airbyte-lib.",
            connector_name=self.metadata.name,
        )

    def execute(self, args: list[str]) -> Iterator[str]:
        with _stream_from_subprocess([self.metadata.name, *args]) as stream:
            yield from stream

    def get_telemetry_info(self) -> SourceTelemetryInfo:
        return SourceTelemetryInfo(self.metadata.name, SourceType.LOCAL_INSTALL, version=None)
