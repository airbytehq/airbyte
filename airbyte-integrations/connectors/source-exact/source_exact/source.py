from typing import Any, Mapping

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState


class SourceExact(YamlDeclarativeSource):
    def __init__(self, catalog: ConfiguredAirbyteCatalog | None, config: Mapping[str, Any] | None, state: TState, **kwargs):
        super().__init__(catalog=catalog,config=config,state=state, **{"path_to_yaml": "exact.yaml"})