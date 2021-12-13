#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import docker
import logging
import pytest
import shutil
import sys
import tempfile
from docker.client import DockerClient
from docker.models.images import Image
from pathlib import Path
from typing import List

from .airbyte_entrypoint import AirbyteEntrypoint, reset_logging
from .input_config import InputConfig

logger = logging.getLogger(__name__)


class AirbytePyEntrypoint(AirbyteEntrypoint):

    def run_integration_tests(self) -> bool:
        """Run integration and acceptance tests together"""
        return self._run_pytest([
            "integration_tests",
            "-p", "integration_tests.acceptance",
            "--acceptance-test-config", str(self.config.source_dir)
        ])


def main():
    reset_logging()
    sys.exit(AirbytePyEntrypoint(InputConfig.parse()).main())
