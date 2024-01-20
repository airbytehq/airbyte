#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.config_observation import emit_configuration_as_airbyte_control_message
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource

from .legacy_config_transformer import LegacyConfigTransformer


class SourceAzureBlobStorage(FileBasedSource):
    def read_config(self, config_path: str) -> Mapping[str, Any]:
        """
        Used to override the default read_config so that when the new file-based Azure Blob Storage connector processes a config
        in the legacy format, it can be transformed into the new config. This happens in entrypoint before we
        validate the config against the new spec.
        """
        config = super().read_config(config_path)
        if not self._is_v1_config(config):
            converted_config = LegacyConfigTransformer.convert(config)
            emit_configuration_as_airbyte_control_message(converted_config)
            return converted_config
        return config

    @staticmethod
    def _is_v1_config(config: Mapping[str, Any]) -> bool:
        return "streams" in config
