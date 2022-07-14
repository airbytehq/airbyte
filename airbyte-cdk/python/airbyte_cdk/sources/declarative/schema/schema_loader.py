#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Mapping

from airbyte_cdk.sources.declarative.declarative_component_mixin import DeclarativeComponentMixin


class SchemaLoader(ABC, DeclarativeComponentMixin):
    @abstractmethod
    def get_json_schema(self) -> Mapping[str, Any]:
        pass
