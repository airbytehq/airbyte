#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_reply_io import SourceReplyIo

if __name__ == "__main__":
    source = SourceReplyIo()
    launch(source, sys.argv[1:])
