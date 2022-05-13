#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_sendgrid.sendgrid import SendgridSource

if __name__ == "__main__":
    source = SendgridSource()
    launch(source, sys.argv[1:])
