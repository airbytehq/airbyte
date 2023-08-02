#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from source_s3 import SourceS3
from source_s3.v4.main import get_source

if __name__ == "__main__":
    args = sys.argv[1:]
    config_path = AirbyteEntrypoint.extract_config(args)
    source = SourceS3()
    if config_path:
        config = source.read_config(config_path)
        if config.get("config_version"):
            source = get_source(args)

    launch(source, sys.argv[1:])
