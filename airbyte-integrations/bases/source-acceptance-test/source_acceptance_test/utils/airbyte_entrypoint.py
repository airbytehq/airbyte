#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import docker
import flake8
import json
import logging
import pytest
import shutil
import sys
import tempfile
from dataclasses import dataclass
from docker.client import DockerClient
from docker.models.images import Image
from flake8.main.cli import main as flake8_main
from pathlib import Path
from typing import List

from .connector_runner import ConnectorRunner
from .input_config import InputConfig

logger = logging.getLogger(__name__)


def reset_logging():
    """Removes all previous default loggers"""
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s # %(message)s'
    )
    sys.excepthook = None


@dataclass
class AirbyteEntrypoint:
    """Base launch class"""

    config: InputConfig

    def run_flake8(self) -> bool:
        """"try to run the tool flake8 into source folder"""
        logger.info("try to run flake8....")
        try:
            flake8_main(["--exclude=.venv,models,.eggs",
                         "--extend-ignore=E203,E231,E501,W503",
                         str(self.config.source_dir)])
        except SystemExit as err:
            logger.warning(err.code)
            return err.code == 0
        return 0

    def _run_pytest(self, args: List[str]) -> bool:
        """"try to run the tool pytest into source folder"""
        args += "-r fEsx --capture=no -vv --log-level=WARNING --color=yes --force-sugar".split(" ")
        return pytest.main(args) == 0

    def run_integration_tests(self) -> bool:
        """"try to run integration tests into source folder"""
        return self._run_pytest([
            "integration_tests",
            "-p", "source_acceptance_test.plugin",
            "--acceptance-test-config", str(self.config.source_dir)
        ])

    def __run_in_docker(self) -> bool:
        """"try to run tests into a new docker container"""
        volumes = {
            "/var/run/docker.sock": {'bind': '/var/run/docker.sock', 'mode': 'rw'},
            "/tmp": {'bind': '/tmp', 'mode': 'rw'},
        }

        client = docker.from_env()
        if self.config.is_python:
            image = self.__build_py_test_image(client)
        else:
            raise Exception("don't support other language...")
        cmd = " ".join(sys.argv[1:])
        working_dir = image.attrs["Config"]["WorkingDir"] or "/airbyte/integration_code"
        cmd = cmd.replace(str(self.config.source_dir), working_dir)

        container = client.containers.run(
            image=image, detach=True,
            command=cmd,
            volumes=volumes, auto_remove=True
        )
        for line in ConnectorRunner.read(container, with_ext=False):
            print(line)
        exit_status = container.wait()
        logger.info(f"Result: {exit_status}")
        return exit_status["StatusCode"]

    def __build_py_test_image(self, client: DockerClient) -> Image:
        """Tries to build a image"""
        tmp_dir = Path(tempfile.mkdtemp())
        shutil.copyfile(str(self.config.source_dir / "acceptance-test-config.yml"),
                        str(tmp_dir / "acceptance-test-config.yml"))
        shutil.copyfile(str(self.config.source_dir / "setup.py"), str(tmp_dir / "setup.py"))
        if self.config.integration_tests and self.config.py_integration_tests_dir:
            shutil.copytree(str(self.config.source_dir / "integration_tests"), str(tmp_dir / "integration_tests"))
        if self.config.unit_tests and self.config.py_unit_tests_dir:
            shutil.copytree(str(self.config.source_dir / "unit_tests"), str(tmp_dir / "unit_tests"))
        if (self.config.source_dir / "secrets").is_dir():
            shutil.copytree(str(self.config.source_dir / "secrets"), str(tmp_dir / "secrets"))

        shutil.copytree("/airbyte/source_acceptance_test", str(tmp_dir / "source_acceptance_test"))

        dockerfile = tmp_dir / "Dockerfile"
        connector_image = self.config.get_acceptance_test_config()["connector_image"]
        # image = client.images.get(connector_image)
        logger.info(f"found the basic image: {connector_image}...")
        with open(dockerfile, "w") as file:
            file.write(f"FROM {connector_image}\n")
            file.write("ENV PYTHONPATH ${PYTHONPATH}:/airbyte/integration_code\n")
            file.write("COPY ./source_acceptance_test /source_acceptance_test\n")
            file.write("RUN pip install -e /source_acceptance_test\n")
            file.write("COPY ./ ./\n")
            file.write("RUN pip install -e .[tests]\n")
            file.write('ENTRYPOINT ["airbyte_py_tests"]\n')

        logger.info("start to build the new image with tests...")
        image, logs = client.images.build(
            path=str(tmp_dir),
            quiet=False,
            tag=connector_image + ".test"
        )
        for line in logs:
            logger.info(line)

        shutil.rmtree(str(tmp_dir))
        return image

    def main(self) -> int:
        """Launch function"""
        if self.config.linter_tests:
            if not self.config.is_python:
                logger.warning("flake8 is used for Python sources only")
            elif not self.run_flake8():
                return 1

        if self.config.get_acceptance_test_config() and (self.config.integration_tests or self.config.unit_tests):
            return self.__run_in_docker()

        # start default logic
        return 1 if self.run_integration_tests() else 0


def main():
    reset_logging()
    sys.exit(AirbyteEntrypoint(InputConfig.parse()).main())
