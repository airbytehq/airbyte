#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import Any, List, Mapping

from source_s3.source import SourceS3Spec

SECONDS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MICROS_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class LegacyConfigTransformer:
    """
    Class that takes in S3 source configs in the legacy format and transforms them into
    configs that can be used by the new S3 source built with the file-based CDK.
    """

    @classmethod
    def convert(cls, legacy_config: SourceS3Spec) -> Mapping[str, Any]:
        transformed_config = {
            "bucket": legacy_config.provider.bucket,
            "streams": [
                {
                    "name": legacy_config.dataset,
                    "file_type": legacy_config.format.filetype,
                    "globs": cls._create_globs(legacy_config.path_pattern, legacy_config.provider.path_prefix),
                    "validation_policy": "Emit Record",
                    # todo: add formats on a per-type basis in follow up PRs
                }
            ],
        }

        if legacy_config.provider.start_date:
            transformed_config["start_date"] = cls._transform_seconds_to_micros(legacy_config.provider.start_date)
        if legacy_config.provider.aws_access_key_id:
            transformed_config["aws_access_key_id"] = legacy_config.provider.aws_access_key_id
        if legacy_config.provider.aws_secret_access_key:
            transformed_config["aws_secret_access_key"] = legacy_config.provider.aws_secret_access_key
        if legacy_config.provider.endpoint:
            transformed_config["endpoint"] = legacy_config.provider.endpoint
        if legacy_config.user_schema and legacy_config.user_schema != "{}":
            transformed_config["streams"][0]["input_schema"] = legacy_config.user_schema

        return transformed_config

    @classmethod
    def _create_globs(cls, path_pattern: str, path_prefix: str) -> List[str]:
        if path_prefix:
            return [path_prefix + path_pattern]
        return [path_pattern]

    @classmethod
    def _transform_seconds_to_micros(cls, datetime_str: str) -> str:
        try:
            parsed_datetime = datetime.strptime(datetime_str, SECONDS_FORMAT)
            return datetime.strftime(parsed_datetime, MICROS_FORMAT)
        except ValueError as e:
            raise e
