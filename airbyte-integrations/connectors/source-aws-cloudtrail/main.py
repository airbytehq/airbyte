#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_aws_cloudtrail import SourceAwsCloudtrail

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceAwsCloudtrail()
    launch(source, sys.argv[1:])
