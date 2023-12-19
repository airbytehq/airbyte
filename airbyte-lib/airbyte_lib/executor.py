# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os
import subprocess
import sys
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import IO, List

from airbyte_lib.registry import ConnectorMetadata


class Executor(ABC):
    def __init__(self, metadata: ConnectorMetadata, target_version: str = "latest"):
        self.metadata = metadata
        self.target_version = target_version if target_version != "latest" else metadata.latest_available_version

    @abstractmethod
    @contextmanager
    def execute(self, args: List[str]) -> IO[str]:
        pass

    @abstractmethod
    def ensure_installation(self):
        pass


def _stream_from_subprocess(args: List[str]) -> IO[str]:
    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )

    try:
        yield process.stdout
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
    def _get_venv_name(self):
        return f".venv-{self.metadata.name}"

    def _get_connector_path(self):
        return Path(self._get_venv_name(), "bin", self.metadata.name)

    def _run_subprocess_and_raise_on_failure(self, args: List[str]):
        result = subprocess.run(args)
        if result.returncode != 0:
            raise Exception(f"Install process exited with code {result.returncode}")

    def _install(self):
        venv_name = self._get_venv_name()
        self._run_subprocess_and_raise_on_failure([sys.executable, "-m", "venv", venv_name])

        pip_path = os.path.join(venv_name, "bin", "pip")

        # TODO this is a temporary install path that will be replaced with a proper package name once they are published. At this point we are also using the version
        package_to_install = f"../airbyte-integrations/connectors/{self.metadata.name}"
        self._run_subprocess_and_raise_on_failure([pip_path, "install", "-e", package_to_install])

    def _get_installed_version(self):
        """
        In the venv, run the following: python -c "from importlib.metadata import version; print(version('<connector-name>'))"
        """
        venv_name = self._get_venv_name()
        connector_name = self.metadata.name
        return subprocess.check_output(
            [os.path.join(venv_name, "bin", "python"), "-c", f"from importlib.metadata import version; print(version('{connector_name}'))"],
            universal_newlines=True,
        ).strip()

    def ensure_installation(self):
        venv_name = f".venv-{self.metadata.name}"
        venv_path = Path(venv_name)
        if not venv_path.exists():
            self._install()

        connector_path = self._get_connector_path()
        if not connector_path.exists():
            raise Exception(f"Could not find connector {self.metadata.name} in venv {venv_name}")

        installed_version = self._get_installed_version()
        if installed_version != self.target_version:
            # If the version doesn't match, reinstall
            self._install()

            # Check the version again
            version_after_install = self._get_installed_version()
            if version_after_install != self.target_version:
                raise Exception(
                    f"Failed to install connector {self.metadata.name} version {self.target_version}. Installed version is {version_after_install}"
                )

    @contextmanager
    def execute(self, args: List[str]) -> IO[str]:
        connector_path = self._get_connector_path()

        return _stream_from_subprocess([str(connector_path)] + args)


class PathExecutor(Executor):
    def ensure_installation(self):
        try:
            self.execute(["spec"])
        except Exception as e:
            raise Exception(f"Connector {self.metadata.name} is not available - executing it failed: {e}")

    @contextmanager
    def execute(self, args: List[str]) -> IO[str]:
        return _stream_from_subprocess([self.metadata.name] + args)
