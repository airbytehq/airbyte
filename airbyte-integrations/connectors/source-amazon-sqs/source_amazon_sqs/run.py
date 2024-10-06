#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_amazon_sqs import SourceAmazonSqs


def run():
    source = SourceAmazonSqs()
    launch(source, sys.argv[1:])
