#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping

from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from source_s3.source import SourceS3Spec
from source_s3.v4.legacy_config_transformer import LegacyConfigTransformer


class SourceS3(FileBasedSource):
    def read_config(self, config_path: str) -> Mapping[str, Any]:
        """
        Used to override the default read_config so that when the new file-based S3 connector processes a config
        in the legacy format, it can be transformed into the new config. This happens in entrypoint before we
        validate the config against the new spec.
        """
        config = super().read_config(config_path)
        if not config.get("streams"):
            parsed_legacy_config = SourceS3Spec(**config)
            return LegacyConfigTransformer.convert(parsed_legacy_config)
        return config
