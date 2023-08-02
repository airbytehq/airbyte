#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import pathlib

import pytest
import json
import yaml
from pydash.objects import get

from metadata_service import gcs_upload
from metadata_service.models.generated.ConnectorMetadataDefinitionV0 import ConnectorMetadataDefinitionV0
from metadata_service.constants import METADATA_FILE_NAME
from metadata_service.models import transform


def test_transform_to_json(get_fixture_path):
    internal_metadata_file_path = get_fixture_path("metadata_validate/valid/metadata_internal_fields.yaml")
    metadata_file_path = pathlib.Path(internal_metadata_file_path)
    metadata = ConnectorMetadataDefinitionV0.parse_obj(yaml.safe_load(metadata_file_path.read_text()))
    assert False
