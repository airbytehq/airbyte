#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_aws_cloudtrail import SourceAwsCloudtrail

if __name__ == "__main__":
    source = SourceAwsCloudtrail()
    launch(source, sys.argv[1:])
