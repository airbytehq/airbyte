#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from source_s3 import SourceS3
from source_s3.v4.main import get_source

def _use_file_based(args, config):
    return config.get("config_version") or args[0] == "spec"

if __name__ == "__main__":
    args = sys.argv[1:]
    config_path = AirbyteEntrypoint.extract_config(args)
    # FIXME: I think we can move a lot of this logic inside AdaptedSourceS3
    source = SourceS3()

    config = source.read_config(config_path) if config_path else {}
    if _use_file_based(args, config):
        source = get_source(args)

    launch(source, sys.argv[1:])
