#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource
from source_s3.v4 import Config, SourceS3StreamReader

if __name__ == "__main__":
    args = sys.argv[1:]
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    source = FileBasedSource(SourceS3StreamReader(), Config, catalog_path)
    launch(source, args)
