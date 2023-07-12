import json
from abc import ABC, abstractmethod
from collections.abc import AsyncIterable
from typing import Tuple, Mapping, Any, Optional

import yaml
from airbyte_cdk.sources.connector_state_manager import HashableStreamDescriptor
from airbyte_protocol.models import ConfiguredAirbyteCatalog, ConnectorSpecification, AirbyteCatalog, AirbyteMessage

from airbyte_cdk.connector import load_optional_package_file


# I think we don't need this class anymore. Ignore.
class AsyncSource(ABC):

    def spec(self, config: Mapping[str, Any] = None) -> ConnectorSpecification:
        """
        This was pretty much lifted from the V1 source.

        The optional config param is not currently used but is speculatively added in case we ever do



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

    @abstractmethod
    async def check(self, config, catalog: ConfiguredAirbyteCatalog = None) -> Tuple[bool, Optional[str]]:
        """
        The optional catalog parameter is not currently used but is speculatively added in case we
         ever get around to https://github.com/airbytehq/airbyte/issues/2364
        """

    @abstractmethod
    async def discover(self, config) -> AirbyteCatalog:
        """
        Discover
        """

    @abstractmethod
    async def read(
            self,
            config: Mapping[str, Any],
            catalog: ConfiguredAirbyteCatalog,
            state: Mapping[HashableStreamDescriptor, Any]
    ) -> AsyncIterable[AirbyteMessage]:
        """
        Read
        """
