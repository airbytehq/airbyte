#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


from typing import Any, MutableMapping, Tuple

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.utils import is_cloud_environment

from .utils import parse_url


class SourceGitlab(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    @staticmethod
    def _ensure_default_values(config: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        config["api_url"] = config.get("api_url") or "gitlab.com"
        return config

    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        config = self._ensure_default_values(config)
        is_valid, scheme, _ = parse_url(config["api_url"])
        if not is_valid:
            return False, "Invalid API resource locator."
        if scheme == "http" and is_cloud_environment():
            return False, "Http scheme is not allowed in this environment. Please use `https` instead."
        return super().check_connection(logger, config)
