#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_reply_io import SourceReplyIo

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceReplyIo()
    launch(source, sys.argv[1:])
