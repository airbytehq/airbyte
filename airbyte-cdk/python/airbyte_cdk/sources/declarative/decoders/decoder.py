#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Mapping

import requests
from airbyte_cdk.sources.declarative.cdk_jsonschema import JsonSchemaMixin
from airbyte_cdk.sources.declarative.declarative_component_mixin import DeclarativeComponentMixin


@dataclass
class Decoder(ABC, JsonSchemaMixin, DeclarativeComponentMixin):
    @abstractmethod
    def decode(self, response: requests.Response) -> Mapping[str, Any]:
        pass
