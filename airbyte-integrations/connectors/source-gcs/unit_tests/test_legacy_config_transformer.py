# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import Mock, patch

from pyarrow import MockOutputStream
from source_gcs import LegacyConfigTransformer, helpers
from source_gcs.spec import SourceGCSSpec


def test_convert_successfully():
    config = Mock(spec=SourceGCSSpec)
    config.gcs_path = "test_path"
    config.gcs_bucket = "test_bucket"
    config.service_account = "test_service_account"
    blob = Mock()
    blob.name = "test_blob"
    blob.prefix = "prefix"
    with patch("source_gcs.legacy_config_transformer.get_gcs_blobs", return_value=[blob]):
        transformed_config = LegacyConfigTransformer.convert(config)

    assert transformed_config["streams"][0]["name"] == "test_blob"
