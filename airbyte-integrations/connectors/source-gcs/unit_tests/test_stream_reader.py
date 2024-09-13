# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import Mock

import pytest
from airbyte_cdk.sources.file_based.exceptions import ErrorListingFiles
from source_gcs import Config, SourceGCSStreamReader
from source_gcs.config import ServiceAccountCredentials


def test_get_matching_files_with_no_prefix(logger):
    reader = SourceGCSStreamReader()
    reader._config = Config(
        bucket="test_bucket",
        streams=[],
        credentials=ServiceAccountCredentials(
            service_account='{"type": "service_account"}',
            auth_type="Service"
        )
    )
    reader._gcs_client = Mock()
    globs = ["**/*.csv"]

    with pytest.raises(ErrorListingFiles):
        list(reader.get_matching_files(globs, None, logger))

    # Assert there is a valid prefix:glob pair, so for loop enters execution.
    assert reader._gcs_client.get_bucket.called == 1
