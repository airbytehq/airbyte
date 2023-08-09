#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from source_s3.v4 import Config, SourceS3StreamReader
from source_s3.v4 import SourceS3 as SourceS3V4
from source_s3 import SourceS3 as SourceS3V3

if __name__ == "__main__":
    args = sys.argv[1:]
    if args[0] == "spec":
        source = SourceS3V3()
    else:
        catalog_path = AirbyteEntrypoint.extract_catalog(args)
        source = SourceS3V4(SourceS3StreamReader(), Config, catalog_path)
    launch(source, sys.argv[1:])
