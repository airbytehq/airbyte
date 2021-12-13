import docker
import flake8
import logging
import pytest
import shutil
import sys
import tempfile
from docker.client import DockerClient
from docker.models.images import Image
from flake8.main.cli import main as flake8_main
from pathlib import Path
from typing import List

from .airbyte_entrypoint import AirbyteEntrypoint, reset_logging
from .input_config import InputConfig

logger = logging.getLogger(__name__)


class AirbytePyEntrypoint(AirbyteEntrypoint):

    def run_integration_and_acceptance_tests(self) -> bool:
        return self._run_pytest([
            "integration_tests",
            "-p", "integration_tests.acceptance",
            "--acceptance-test-config", str(self.config.source_dir)
        ])

    def run_unit_tests(self) -> bool:
        return self._run_pytest([
            str(self.config.source_dir / "unit_tests"), Ж
        ])

    def main(self) -> int:
        if self.config.integration_tests and not self.run_integration_and_acceptance_tests():
            return 1
        if self.config.unit_tests and not self.run_unit_tests():
            return 1
        logger.info("finished...")
        return 0


def main():
    reset_logging()
    sys.exit(AirbytePyEntrypoint(InputConfig.parse()).main())
