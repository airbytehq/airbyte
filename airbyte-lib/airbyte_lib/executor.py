from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
import subprocess
from typing import List, IO
from airbyte_lib.registry import ConnectorMetadata
from pathlib import Path
import subprocess
from typing import List, IO
from abc import ABC, abstractmethod
from contextlib import contextmanager



class Executor(ABC):
    def __init__(self, metadata: ConnectorMetadata):
        self.metadata = metadata

    @abstractmethod
    @contextmanager
    def execute(self, args: List[str]) -> IO[str]:
        pass


class VenvExecutor(Executor):
    def __init__(self, metadata: ConnectorMetadata):
        super().__init__(metadata)

    @contextmanager
    def execute(self, args: List[str]) -> IO[str]:
        venv_name = f".venv-{self.metadata.name}"
        venv_path = Path(venv_name)
        if not venv_path.exists():
            raise Exception(f"Could not find venv {venv_name}")

        connector_path = Path(venv_path, "bin", self.metadata.name)
        if not connector_path.exists():
            raise Exception(
                f"Could not find connector {self.metadata.name} in venv {venv_name}"
            )

        process = subprocess.Popen(
            [str(connector_path)] + args,
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

