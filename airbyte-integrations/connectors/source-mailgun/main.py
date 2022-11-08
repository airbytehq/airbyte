#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_mailgun import SourceMailgun

if __name__ == "__main__":
    source = SourceMailgun()
    launch(source, sys.argv[1:])
