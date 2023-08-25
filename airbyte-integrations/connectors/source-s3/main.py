#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_s3 import SourceS3

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceS3()
    launch(source, sys.argv[1:])
