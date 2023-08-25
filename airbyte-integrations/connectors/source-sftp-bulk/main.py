#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_sftp_bulk import SourceFtp

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceFtp()
    launch(source, sys.argv[1:])
