#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Dict, Mapping

from source_gcs.spec import SourceGCSSpec

from .helpers import get_gcs_blobs, get_stream_name


class LegacyConfigTransformer:
    """
    Transforms GCS source configs from legacy format to be compatible
    with the new GCS source built with the file-based CDK.
    """

    @staticmethod
    def _create_stream(blob: Any, legacy_prefix: str) -> Dict[str, Any]:
        """
        Create a stream dict from a blob.

        :param blob: The blob from which to create the stream.
        :param legacy_prefix: The legacy prefix path on GCS.
        :return: A dictionary representing the stream.
        """
        return {
            "name": get_stream_name(blob),
            "legacy_prefix": f"{legacy_prefix}/{blob.name.split('/')[-1]}",
            "validation_policy": "Emit Record",
            "format": {"filetype": "csv"},
        }

    @classmethod
    def convert(cls, legacy_config: SourceGCSSpec) -> Mapping[str, Any]:
        """
        Convert a legacy configuration to a transformed configuration.

        :param legacy_config: Legacy configuration of type SourceGCSSpec.
        :return: Transformed configuration as a dictionary.
        """
        blobs = get_gcs_blobs(legacy_config)
        streams = [cls._create_stream(blob, legacy_config.gcs_path) for blob in blobs]

        return {"bucket": legacy_config.gcs_bucket, "service_account": legacy_config.service_account, "streams": streams}
