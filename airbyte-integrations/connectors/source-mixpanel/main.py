#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_mixpanel import SourceMixpanel

if __name__ == "__main__":
    source = SourceMixpanel()
    launch(source, sys.argv[1:])
