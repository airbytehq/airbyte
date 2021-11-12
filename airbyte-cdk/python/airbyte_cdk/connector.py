#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import os
import pkgutil
from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteConnectionStatus, ConnectorSpecification


class AirbyteSpec(object):
    @staticmethod
    def from_file(file_name: str):
        with open(file_name) as file:
            spec_text = file.read()
        return AirbyteSpec(spec_text)

    def __init__(self, spec_string):
        self.spec_string = spec_string


class Connector(ABC):
    # configure whether the `check_config_against_spec_or_exit()` needs to be called
    check_config_against_spec: bool = True

    # can be overridden to change an input config
    def configure(self, config: Mapping[str, Any], temp_dir: str) -> Mapping[str, Any]:
        """
        Persist config in temporary directory to run the Source job
        """
        config_path = os.path.join(temp_dir, "config.json")
        self.write_config(config, config_path)
        return config

    @staticmethod
    def read_config(config_path: str) -> Mapping[str, Any]:
        with open(config_path, "r") as file:
            contents = file.read()
        return json.loads(contents)

    @staticmethod
    def write_config(config: Mapping[str, Any], config_path: str):
        with open(config_path, "w") as fh:
            fh.write(json.dumps(config))

    def spec(self, logger: AirbyteLogger) -> ConnectorSpecification:
        """
        Returns the spec for this integration. The spec is a JSON-Schema object describing the required configurations (e.g: username and password)
        required to run this integration.
        """
        raw_spec: Optional[bytes] = pkgutil.get_data(self.__class__.__module__.split(".")[0], "spec.json")
        if not raw_spec:
            raise ValueError("Unable to find spec.json.")
        return ConnectorSpecification.parse_obj(json.loads(raw_spec))

    @abstractmethod
    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the integration e.g: if a provided Stripe API token can be used to connect
        to the Stripe API.
        """
