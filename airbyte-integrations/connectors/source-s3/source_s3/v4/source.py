#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import orjson
from airbyte_cdk import (
    AirbyteEntrypoint,
    ConnectorSpecification,
    emit_configuration_as_airbyte_control_message,
    is_cloud_environment,
    launch,
)
from airbyte_cdk.models import (
    AirbyteErrorTraceMessage,
    AirbyteMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteCatalogSerializer,
    TraceType,
    Type,
)
from airbyte_cdk.sources.file_based.file_based_source import DEFAULT_CONCURRENCY, FileBasedSource
from source_s3.source import SourceS3Spec
from source_s3.utils import airbyte_message_to_json
from source_s3.v4.config import Config
from source_s3.v4.cursor import Cursor
from source_s3.v4.legacy_config_transformer import LegacyConfigTransformer
from source_s3.v4.stream_reader import SourceS3StreamReader

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
            raise ValueError("Overlapping properties between V3 and V4")  # pragma: no cover

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
    def _create_description_with_deprecation_prefix(new_fields: Optional[str]) -> str:  # pragma: no cover
        if new_fields:
            return f"Deprecated and will be removed soon. Please do not use this field anymore and use {new_fields} instead. "

        return "Deprecated and will be removed soon. Please do not use this field anymore. "

    @classmethod
    def launch(cls, args: list[str] | None = None) -> None:
        """Launch the source using the provided CLI args.

        If no args are provided, the launch args will be inferred automatically.

        In the future, we should consider moving this method to the Connector base class,
        so that all sources and destinations can launch themselves and so none of this
        code needs to live in the connector itself.
        """
        args = args or sys.argv[1:]
        catalog_path = AirbyteEntrypoint.extract_catalog(args)
        # TODO: Delete if not needed:
        # config_path = AirbyteEntrypoint.extract_config(args)
        # state_path = AirbyteEntrypoint.extract_state(args)

        source = cls.create(
            configured_catalog_path=Path(catalog_path) if catalog_path else None,
        )
        # The following function will wrap the execution in proper error handling.
        # Failures prior to here may not emit proper Airbyte TRACE or CONNECTION_STATUS messages.
        launch(
            source=source,
            args=args,
        )

    @classmethod
    def create(
        cls,
        *,
        configured_catalog_path: Path | str | None = None,
    ) -> SourceS3:
        """Create a new instance of the source.

        This is a bit of a hack because (1) the source needs the catalog early, and (2), the
        constructor asks for things that the caller won't know about, specifically: the stream
        reader class, the spec class, and the cursor class.

        We should consider refactoring the constructor so that these inputs don't need to be
        provided by the caller. This probably requires changes to the base class in the CDK.

        We prefer to fail in the `launch` method, where proper error handling is in place.
        """
        try:
            configured_catalog: ConfiguredAirbyteCatalog | None = (
                ConfiguredAirbyteCatalogSerializer.load(orjson.loads(Path(configured_catalog_path).read_text()))
                if configured_catalog_path
                else None
            )
        except Exception as ex:
            print(
                airbyte_message_to_json(
                    AirbyteMessage(
                        type=Type.TRACE,
                        trace=AirbyteTraceMessage(
                            type=TraceType.ERROR,
                            emitted_at=int(datetime.now().timestamp() * 1000),
                            error=AirbyteErrorTraceMessage(
                                message="Error starting the sync. This could be due to an invalid configuration or catalog. Please contact Support for assistance.",
                                stack_trace=traceback.format_exc(),
                                internal_message=str(ex),
                            ),
                        ),
                    ),
                    newline=True,
                )
            )
            # Ideally we'd call `raise` here, but sometimes the stack trace bleeds into
            # the Airbyte logs, which is not ideal. So we'll just exit with an error code instead.
            sys.exit(1)

        return cls(
            # These are the defaults for the source. No need for a caller to change them:
            stream_reader=SourceS3StreamReader(),
            spec_class=Config,
            cursor_cls=Cursor,
            # This is needed early. (We also will provide it again later.)
            catalog=configured_catalog,
            # These will be provided later, after we have wrapped proper error handling.
            config=None,
            state=None,
        )
