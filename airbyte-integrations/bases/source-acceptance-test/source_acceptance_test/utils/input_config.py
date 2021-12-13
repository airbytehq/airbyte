#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import argparse
import logging
import os
import sys
import yaml
import yaml
from argparse import Namespace
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Mapping, Any, List

logger = logging.getLogger(__name__)


@dataclass
class InputConfig(Namespace):
    args: Namespace
    unknown_args: List[str]

    @property
    def source_dir(self) -> Path:
        return self.args.source_dir or self.args.acceptance_test_config;

    def get_acceptance_test_config(self) -> Optional[Mapping[str, Any]]:
        config_file = self.source_dir / "acceptance-test-config.yaml"
        if not config_file.is_file():
            config_file = self.source_dir / "acceptance-test-config.yml"
        if not config_file.is_file():
            logger.warning(f"not found the file {config_file}")
            return None
        with open(config_file, "r") as file:
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as err:
                logger.error(f"can't parse the YAML file  {config_file}, error: {str(err)}")
        return None

    @property
    def is_python(self):
        return self.setup_py is not None

    @property
    def setup_py(self) -> Optional[Path]:
        file = self.source_dir / "setup.py"
        return file if file.is_file() else None

    @property
    def py_integration_tests_dir(self) -> Optional[Path]:
        dir = self.source_dir / "integration_tests"
        return dir if (self.is_python and dir.is_dir()) else None

    @property
    def acceptance_tests(self) -> bool:
        return self.args.acceptance_tests

    @classmethod
    def parse(cls) -> "InputConfig":
        """Parses all input attributes"""
        parser = argparse.ArgumentParser(prog='SourceAcceptanceTests')
        source_dir = parser.add_mutually_exclusive_group(required=True)
        source_dir.add_argument('--acceptance-test-config', type=Path,
                                help='DEPRECATED: please use --source_folder')
        source_dir.add_argument('-d', '--source_dir', type=Path,
                                help='folder with the file acceptance-test-config.yaml and all possible tests.')
        parser.add_argument('--acceptance-tests', '--acceptance_tests', action='store_true',
                            help="Try to run all acceptance exists tests")

        return cls(*parser.parse_known_args())
