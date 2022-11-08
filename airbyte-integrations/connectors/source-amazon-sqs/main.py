#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_amazon_sqs import SourceAmazonSqs

if __name__ == "__main__":
    source = SourceAmazonSqs()
    launch(source, sys.argv[1:])
