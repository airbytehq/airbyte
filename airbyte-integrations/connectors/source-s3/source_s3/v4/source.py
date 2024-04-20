#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Mapping, Optional

from airbyte_cdk.config_observation import emit_configuration_as_airbyte_control_message
from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.sources.file_based.file_based_source import DEFAULT_CONCURRENCY, FileBasedSource
from airbyte_cdk.utils import is_cloud_environment
from source_s3.source import SourceS3Spec
from source_s3.v4.legacy_config_transformer import LegacyConfigTransformer

_V3_DEPRECATION_FIELD_MAPPING = {
    "dataset": "streams.name",
    "format": "streams.format",
    "path_pattern": "streams.globs",
    "provider": "bucket, aws_access_key_id, aws_secret_access_key and endpoint",
    "schema": "streams.input_schema",
}


class SourceS3(FileBasedSource):
    _concurrency_level = DEFAULT_CONCURRENCY

    @classmethod
    def read_config(cls, config_path: str) -> Mapping[str, Any]:
        """
        Used to override the default read_config so that when the new file-based S3 connector processes a config
        in the legacy format, it can be transformed into the new config. This happens in entrypoint before we
        validate the config against the new spec.
        """
        config = super().read_config(config_path)
        if not SourceS3._is_v4_config(config):
            parsed_legacy_config = SourceS3Spec(**config)
            converted_config = LegacyConfigTransformer.convert(parsed_legacy_config)
            emit_configuration_as_airbyte_control_message(converted_config)
            return converted_config
        return config

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        s3_spec = SourceS3Spec.schema()
        s4_spec = self.spec_class.schema()

        if s3_spec["properties"].keys() & s4_spec["properties"].keys():
            raise ValueError("Overlapping properties between V3 and V4")

        for v3_property_key, v3_property_value in s3_spec["properties"].items():
            s4_spec["properties"][v3_property_key] = v3_property_value
            s4_spec["properties"][v3_property_key]["airbyte_hidden"] = True
            s4_spec["properties"][v3_property_key]["order"] += 100
            s4_spec["properties"][v3_property_key]["description"] = (
                SourceS3._create_description_with_deprecation_prefix(_V3_DEPRECATION_FIELD_MAPPING.get(v3_property_key, None))
                + s4_spec["properties"][v3_property_key]["description"]
            )
            self._clean_required_fields(s4_spec["properties"][v3_property_key])

        if is_cloud_environment():
            s4_spec["properties"]["endpoint"].update(
                {
                    "description": "Endpoint to an S3 compatible service. Leave empty to use AWS. "
                    "The custom endpoint must be secure, but the 'https' prefix is not required.",
                    "pattern": "^(?!http://).*$",  # ignore-https-check
                }
            )

        return ConnectorSpecification(
            documentationUrl=self.spec_class.documentation_url(),
            connectionSpecification=s4_spec,
        )

    @staticmethod
    def _is_v4_config(config: Mapping[str, Any]) -> bool:
        return "streams" in config

    @staticmethod
    def _clean_required_fields(v3_field: Dict[str, Any]) -> None:
        """
        Not having V3 fields root level as part of the `required` field is not enough as the platform will create empty objects for those.
        For example, filling all non-hidden fields from the form will create a config like:
        ```
        {
          <...>
          "provider": {},
          <...>
        }
        ```

        As the field `provider` exists, the JSON validation will be applied and as `provider.bucket` is needed, the validation will fail
        with the following error:
        ```
          "errors": {
            "connectionConfiguration": {
              "provider": {
                "bucket": {
                  "message": "form.empty.error",
                  "type": "required"
                }
              }
            }
          }
        ```

        Hence, we need to make any V3 nested fields not required.
        """
        if "properties" not in v3_field:
            return

        v3_field["required"] = []
        for neste_field in v3_field["properties"]:
            SourceS3._clean_required_fields(neste_field)

    @staticmethod
    def _create_description_with_deprecation_prefix(new_fields: Optional[str]) -> str:
        if new_fields:
            return f"Deprecated and will be removed soon. Please do not use this field anymore and use {new_fields} instead. "
        return "Deprecated and will be removed soon. Please do not use this field anymore. "
