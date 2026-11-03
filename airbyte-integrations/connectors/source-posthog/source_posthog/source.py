#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Optional

from airbyte_cdk.models import AirbyteStateMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from source_posthog.components import PosthogModelToComponentFactory


"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.
"""


# Declarative Source
class SourcePosthog(YamlDeclarativeSource):
    def __init__(
        self,
        catalog: Optional[ConfiguredAirbyteCatalog] = None,
        config: Optional[Mapping[str, Any]] = None,
        state: Optional[List[AirbyteStateMessage]] = None,
    ):
        super().__init__(path_to_yaml="manifest.yaml", catalog=catalog, config=config, state=state)
        # The declarative source creates its component factory internally and offers no way to pass one in.
        # The factory only adds behavior on top of the CDK one (see PosthogModelToComponentFactory), so switching the
        # class of the instance keeps the message repository, state manager and catalog it was created with.
        if type(self._constructor) is not ModelToComponentFactory:
            raise TypeError(f"Unexpected component factory {type(self._constructor).__name__}")
        self._constructor.__class__ = PosthogModelToComponentFactory
