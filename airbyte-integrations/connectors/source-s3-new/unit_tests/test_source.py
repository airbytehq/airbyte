#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock, patch

from source_s3_new.source import SourceS3New


def test_instantiation():
    source = SourceS3New()


# TODO: if you add or override any methods in source.py, add unit tests for those here
