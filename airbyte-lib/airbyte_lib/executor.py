# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
import subprocess
import sys
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Generator, Iterable, List

from airbyte_lib.registry import ConnectorMetadata

_LATEST_VERSION = "latest"


class Executor(ABC):
    def __init__(
        self,
        metadata: ConnectorMetadata,
        target_version: str | None = None,
    ) -> None:
        self.metadata = metadata
        if target_version is None or target_version == _LATEST_VERSION:
            self.target_version = metadata.latest_available_version
        else:
            self.target_version = target_version

    @abstractmethod
    def execute(self, args: List[str]) -> Iterable[str]:
        pass

    @abstractmethod
    def ensure_installation(self):
        pass

    @abstractmethod
    def install(self):
        pass


@contextmanager
def _stream_from_subprocess(args: List[str]) -> Generator[Iterable[str], None, None]:
    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )

    def _stream_from_file(file: IO[str]):
        while True:
            line = file.readline()
            if not line:
                break
            yield line

    if process.stdout is None:
        raise Exception("Failed to start subprocess")
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
        if exit_code != 0 and exit_code != -15:
            raise Exception(f"Process exited with code {exit_code}")


class VenvExecutor(Executor):
    """Executor that runs the connector in a virtual environment."""

    def __init__(
        self,
        metadata: ConnectorMetadata,
        target_version: str | None = None,
        install_if_missing: bool = False,
        pip_url: str | None = None,
        install_root: str | None = None,
    ) -> None:
        super().__init__(metadata, target_version)
        self.install_if_missing = install_if_missing

        # This is a temporary install path that will be replaced with a proper package
        # name once they are published.
        # TODO: Replace with `f"airbyte-{self.metadata.name}"`
        self.pip_url = (
            pip_url or f"../airbyte-integrations/connectors/{self.metadata.name}"
        )
        self.install_root = install_root or "."

    @property
    def venv_name(self) -> str:
        return f".venv-{self.metadata.name}"

    @property
    def venv_path(self) -> Path:
        return Path(self.install_root, self.venv_name)

    def _get_connector_path(self):
        return Path(self.venv_name, "bin", self.metadata.name)

    def _run_subprocess_and_raise_on_failure(self, args: List[str]):
        result = subprocess.run(
            args,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            error_message = (
                f"Install process exited with code {result.returncode}. "
                f"Process STDERR log:\n{result.stderr}"
            )
            raise RuntimeError(error_message)

    def install(self):
        self._run_subprocess_and_raise_on_failure(
            [sys.executable, "-m", "venv", str(self.venv_path.absolute())]
        )

        pip_path = os.path.join(self.venv_path, "bin", "pip")
        pip_cmd = [pip_path, "install"]
        if "/" in self.pip_url and "git+" not in self.pip_url:
            # If the pip url is a local path, add the --editable flag
            pip_cmd += ["-e"]
        pip_cmd += [self.pip_url]

        self._run_subprocess_and_raise_on_failure(pip_cmd)

    def _get_installed_version(self):
        """
        In the venv, run the following: python -c "from importlib.metadata import version; print(version('<connector-name>'))"
        """
        connector_name = self.metadata.name
        return subprocess.check_output(
            [
                os.path.join(self.venv_name, "bin", "python"),
                "-c",
                f"from importlib.metadata import version; print(version('{connector_name}'))",
            ],
            universal_newlines=True,
        ).strip()

    def ensure_installation(
        self,
        verify_version: bool = False,
    ):
        """
        Ensure that the connector is installed in a virtual environment.
        If not yet installed and if install_if_missing is True, then install.

        Optionally, verify that the installed version matches the target version.

        Note: Version verification is not supported for connectors installed from a
        local path.
        """
        venv_name = f".venv-{self.metadata.name}"
        venv_path = self.venv_path
        if not venv_path.exists():
            if not self.install_if_missing:
                raise Exception(
                    f"Connector {self.metadata.name} is not available - venv {venv_name} does not exist"
                )
            self.install()

        connector_path = self._get_connector_path()
        if not connector_path.exists():
            raise FileNotFoundError(
                f"Could not find connector '{self.metadata.name}' "
                f"in venv '{venv_name}' with connector path '{connector_path}'."
            )

        if verify_version:
            installed_version = self._get_installed_version()
            if installed_version != self.target_version:
                # If the version doesn't match, reinstall
                self.install()

                # Check the version again
                version_after_install = self._get_installed_version()
                if version_after_install != self.target_version:
                    raise Exception(
                        f"Failed to install connector {self.metadata.name} version {self.target_version}. Installed version is {version_after_install}"
                    )

    def execute(self, args: List[str]) -> Iterable[str]:
        connector_path = self._get_connector_path()

        with _stream_from_subprocess([str(connector_path)] + args) as stream:
            yield from stream


class PathExecutor(Executor):
    def ensure_installation(self):
        try:
            self.execute(["spec"])
        except Exception as e:
            raise Exception(
                f"Connector {self.metadata.name} is not available - executing it failed: {e}"
            )

    def install(self):
        raise Exception(
            f"Connector {self.metadata.name} is not available - cannot install it"
        )

    def execute(self, args: List[str]) -> Iterable[str]:
        with _stream_from_subprocess([self.metadata.name] + args) as stream:
            yield from stream
