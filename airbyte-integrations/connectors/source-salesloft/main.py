#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_salesloft import SourceSalesloft

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceSalesloft()
    launch(source, sys.argv[1:])
