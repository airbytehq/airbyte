# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import io
import os
import subprocess
import sys
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Generator, Iterable, List

import docker
from airbyte_lib.registry import ConnectorMetadata
from docker.models.containers import Container
from docker.types import Mount


class Executor(ABC):
    def __init__(self, metadata: ConnectorMetadata, target_version: str = "latest"):
        self.metadata = metadata
        self.target_version = target_version if target_version != "latest" else metadata.latest_available_version

    @abstractmethod
    @contextmanager
    def execute(self, args: List[str], files: List[str]) -> Iterable[str]:
        pass

    @abstractmethod
    def ensure_installation(self):
        pass


@contextmanager
def _stream_from_subprocess(args: List[str]) -> Iterable[str]:
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

    def execute(self, args: List[str], files: List[str]) -> Iterable[str]:
        connector_path = self._get_connector_path()

        return _stream_from_subprocess([str(connector_path)] + args)


class PathExecutor(Executor):
    def ensure_installation(self):
        try:
            self.execute(["spec"])
        except Exception as e:
            raise Exception(f"Connector {self.metadata.name} is not available - executing it failed: {e}")

    def execute(self, args: List[str], files: List[str]) -> Iterable[str]:
        return _stream_from_subprocess([self.metadata.name] + args)


class DockerExecutor(Executor):
    def __init__(self, metadata: ConnectorMetadata, target_version: str = "latest"):
        super().__init__(metadata, target_version)
        self.client = docker.from_env()

    def _get_image_name(self):
        return f"{self.metadata.dockerRepository}:{self.target_version}"

    def ensure_installation(self):
        try:
            self.client.images.pull(self._get_image_name())
        except Exception as e:
            raise Exception(f"Failed to pull Docker image {self._get_image_name()}: {str(e)}")

    @contextmanager
    def execute(self, args: List[str], files: List[str]) -> IO[str]:
        command = args

        mounts = [Mount(file, file, read_only=True, type="bind") for file in files]
        container: Container = self.client.containers.run(
            self._get_image_name(), command, mounts=mounts, detach=True, stderr=True, stdout=True
        )

        def buffer_logs() -> Generator[str, None, None]:
            """
            Buffer the logs from the container and yield them line by line.
            This is necessary because the strings returned by container.logs() are not guaranteed to be newline-separated - they can be split in the middle of a line.
            """
            log_stream = container.logs(stream=True)
            log_buffer = ""
            for chunk in log_stream:
                log_buffer += chunk.decode("utf-8")
                while "\n" in log_buffer:
                    line, log_buffer = log_buffer.split("\n", 1)
                    yield line
            if log_buffer:  # In case there's remaining data without a newline
                yield log_buffer

        try:
            yield buffer_logs()
        finally:
            container.remove(force=True)
