#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path
from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource

"""
This file provides the necessary constructs to interpret a provided declarative YAML configuration file into
source connector.
WARNING: Do not modify this file.
"""

# Declarative Source
class SourceTiktokOrganic(YamlDeclarativeSource):
    def __init__(
        self,
        config: Optional[Mapping[str, Any]] = None,
        config_path: Optional[str] = None,
    ):
        manifest_path = str(Path(__file__).with_name("manifest.yaml"))
        super().__init__(
            path_to_yaml=manifest_path,
            config=config,
            config_path=config_path,
        )
