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

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Implements the Check Connection operation from the Airbyte Specification.
        See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#check.
        """
        check_outcome = config["check_outcome"]["check_outcome"]
        if check_outcome == "check_job_failure_with_trace":
            raise Exception("Test Exception - shout @ Ella if you see this")

        check_succeeded, error = self.check_connection(logger, config)
        if check_succeeded:
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        if not check_succeeded:
            return AirbyteConnectionStatus(status=Status.FAILED, message=repr(error))

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        check_outcome = config["check_outcome"]["check_outcome"]
        if check_outcome == "success":
            return True, None
        elif check_outcome == "check_job_success_check_connection_failure":
            return False, "Some error message"

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        """Implements the Discover operation from the Airbyte Specification.
        See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#discover.
        """
        streams = [stream.as_airbyte_stream() for stream in self.streams(config=config)]
        return AirbyteCatalog(streams=streams)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        count: int = config["count"] if "count" in config else 0
        seed: int = config["seed"] if "seed" in config else None
        records_per_sync: int = config["records_per_sync"] if "records_per_sync" in config else 500
        records_per_slice: int = config["records_per_slice"] if "records_per_slice" in config else 100
        parallelism: int = config["parallelism"] if "parallelism" in config else 4

        return [
            Products(count, seed, parallelism, records_per_sync, records_per_slice),
            Users(count, seed, parallelism, records_per_sync, records_per_slice),
            Purchases(count, seed, parallelism, records_per_sync, records_per_slice),
        ]
