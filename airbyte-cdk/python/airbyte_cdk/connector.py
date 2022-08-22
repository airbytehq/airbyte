#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import logging
import os
import pkgutil
from abc import ABC, abstractmethod
from typing import Any, Generic, Mapping, Optional, Protocol, TypeVar

import yaml
from airbyte_cdk.models import AirbyteConnectionStatus, ConnectorSpecification


def load_optional_package_file(package: str, filename: str) -> Optional[bytes]:
    """Gets a resource from a package, returning None if it does not exist"""
    try:
        return pkgutil.get_data(package, filename)
    except FileNotFoundError:
        return None


class AirbyteSpec(object):
    @staticmethod
    def from_file(file_name: str):
        with open(file_name) as file:
            spec_text = file.read()
        return AirbyteSpec(spec_text)

    def __init__(self, spec_string):
        self.spec_string = spec_string


TConfig = TypeVar("TConfig", bound=Mapping[str, Any])


class BaseConnector(ABC, Generic[TConfig]):
    # configure whether the `check_config_against_spec_or_exit()` needs to be called
    check_config_against_spec: bool = True

    @abstractmethod
    def configure(self, config: Mapping[str, Any], temp_dir: str) -> TConfig:
        """
        Persist config in temporary directory to run the Source job
        """

    @staticmethod
    def read_config(config_path: str) -> TConfig:
        with open(config_path, "r") as file:
            contents = file.read()
        return json.loads(contents)

    @staticmethod
    def write_config(config: TConfig, config_path: str):
        with open(config_path, "w") as fh:
            fh.write(json.dumps(config))

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        """
        Returns the spec for this integration. The spec is a JSON-Schema object describing the required configurations (e.g: username and password)
        required to run this integration. By default, this will be loaded from a "spec.yaml" or a "spec.json" in the package root.
        """

        package = self.__class__.__module__.split(".")[0]

        yaml_spec = load_optional_package_file(package, "spec.yaml")
        json_spec = load_optional_package_file(package, "spec.json")

        if yaml_spec and json_spec:
            raise RuntimeError("Found multiple spec files in the package. Only one of spec.yaml or spec.json should be provided.")

        if yaml_spec:
            spec_obj = yaml.load(yaml_spec, Loader=yaml.SafeLoader)
        elif json_spec:
            spec_obj = json.loads(json_spec)
        else:
            raise FileNotFoundError("Unable to find spec.yaml or spec.json in the package.")

        return ConnectorSpecification.parse_obj(spec_obj)

    @abstractmethod
    def check(self, logger: logging.Logger, config: TConfig) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the integration e.g: if a provided Stripe API token can be used to connect
        to the Stripe API.
        """


class _WriteConfigProtocol(Protocol):
    @staticmethod
    def write_config(config: Mapping[str, Any], config_path: str):
        ...


class DefaultConnectorMixin:
    # can be overridden to change an input config
    def configure(self: _WriteConfigProtocol, config: Mapping[str, Any], temp_dir: str) -> Mapping[str, Any]:
        config_path = os.path.join(temp_dir, "config.json")
        self.write_config(config, config_path)
        return config


class Connector(DefaultConnectorMixin, BaseConnector[Mapping[str, Any]], ABC):
    ...
