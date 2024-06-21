#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_alipay_worldfirst import SourceAlipayWorldfirst

if __name__ == "__main__":
    source = SourceAlipayWorldfirst()
    launch(source, sys.argv[1:])
