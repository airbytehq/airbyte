#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_rocket_chat import SourceRocketChat

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceRocketChat()
    launch(source, sys.argv[1:])
