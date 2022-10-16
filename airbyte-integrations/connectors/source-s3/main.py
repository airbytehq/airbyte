#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_s3 import SourceS3

if __name__ == "__main__":
    source = SourceS3()
    launch(source, sys.argv[1:])
