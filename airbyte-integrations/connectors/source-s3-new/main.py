#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_s3_new import SourceS3New

if __name__ == "__main__":
    source = SourceS3New()
    launch(source, sys.argv[1:])
