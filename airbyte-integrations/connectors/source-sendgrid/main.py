#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_sendgrid.sendgrid import SendgridSource

# from airbyte_cdk.sources.cac.configurable_source import ConfigurableSource

if __name__ == "__main__":
    source = SendgridSource()
    # source = ConfigurableSource("./source_sendgrid/sendgrid.yaml")
    launch(source, sys.argv[1:])
