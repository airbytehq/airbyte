#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_amazon_iam import SourceAmazonIam

if __name__ == "__main__":
    source = SourceAmazonIam()
    launch(source, sys.argv[1:])
