#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping

from airbyte_cdk.config_observation import emit_configuration_as_airbyte_control_message
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from source_gcs.legacy_config_transformer import LegacyConfigTransformer
from source_gcs.spec import SourceGCSSpec


class SourceGCS(FileBasedSource):
    @classmethod
    def read_config(cls, config_path: str) -> Mapping[str, Any]:
        """
        Override the default read_config to transform the legacy config format
        into the new one before validating it against the new spec.
        """
        config = FileBasedSource.read_config(config_path)
        if not cls._is_file_based_config(config):
            parsed_legacy_config = SourceGCSSpec(**config)
            converted_config = LegacyConfigTransformer.convert(parsed_legacy_config)
            emit_configuration_as_airbyte_control_message(converted_config)
            return converted_config
        return config

    @staticmethod
    def _is_file_based_config(config: Mapping[str, Any]) -> bool:
        return "streams" in config
