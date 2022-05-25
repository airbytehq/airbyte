#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_sftp import SourceSftp

if __name__ == "__main__":
    source = SourceSftp()
    launch(source, sys.argv[1:])
