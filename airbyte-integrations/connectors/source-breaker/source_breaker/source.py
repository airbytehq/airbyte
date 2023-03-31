#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from typing import Any, List, Mapping, Tuple

import yaml
from airbyte_cdk.connector import load_optional_package_file
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteCatalog, AirbyteConnectionStatus, ConnectorSpecification, Status
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .streams import Products, Purchases, Users


class SourceBreaker(AbstractSource):
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
            try:
                spec_obj = json.loads(json_spec)
            except json.JSONDecodeError as error:
                raise ValueError(f"Could not read json spec file: {error}. Please ensure that it is a valid JSON.")
        else:
            raise FileNotFoundError("Unable to find spec.yaml or spec.json in the package.")

        return ConnectorSpecification.parse_obj(spec_obj)

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        check_outcome = config.get("check_outcome", "Check should succeed")
        if check_outcome == "The check job should fail (unexpected connector error)":
            raise Exception("Test Check Exception - shout @ Ella if you see this in prod")
        if check_outcome == "Check should succeed":
            return True, None
        if check_outcome == "Checking the connection should fail (user error)":
            return False, "Failed to authenticate - check your credentials"
        else:
            raise Exception("Got unexpected value for check outcome")

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        """Implements the Discover operation from the Airbyte Specification.
        See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#discover.
        """
        if config.get("discover_should_fail", False):
            raise Exception("Test Discover Exception - shout @ Ella if you see this")
        streams = [stream.as_airbyte_stream() for stream in self.streams(config=config)]
        return AirbyteCatalog(streams=streams)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        count: int = 1000
        seed: int = None
        records_per_sync: int = 500
        records_per_slice: int = 100
        parallelism: int = 4

        return [
            Products(count, seed, parallelism, records_per_sync, records_per_slice),
            Users(count, seed, parallelism, records_per_sync, records_per_slice),
            Purchases(count, seed, parallelism, records_per_sync, records_per_slice),
        ]
