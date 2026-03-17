#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


class SourceFacebookPages(YamlDeclarativeSource):
    def __init__(
        self,
        catalog: Optional[ConfiguredAirbyteCatalog] = None,
        config: Optional[Mapping[str, Any]] = None,
        state: Optional[List[AirbyteStateMessage]] = None,
    ):
        super().__init__(
            path_to_yaml="manifest.yaml",
            catalog=catalog,
            config=config,
            state=state,
        )
