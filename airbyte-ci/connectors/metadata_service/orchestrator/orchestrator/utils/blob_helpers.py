# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import yaml
from google.cloud import storage


def yaml_blob_to_dict(yaml_blob: storage.Blob) -> dict:
    """
    Convert the given yaml blob to a dictionary.
    """
    yaml_string = yaml_blob.download_as_string().decode("utf-8")
    return yaml.safe_load(yaml_string)
