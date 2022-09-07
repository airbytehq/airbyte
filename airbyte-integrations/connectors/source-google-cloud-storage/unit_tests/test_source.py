#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock, patch

from source_google_cloud_storage.source import SourceGoogleCloudStorage


def test_instantiation():
    source = SourceGoogleCloudStorage()


# TODO: if you add or override any methods in source.py, add unit tests for those here
