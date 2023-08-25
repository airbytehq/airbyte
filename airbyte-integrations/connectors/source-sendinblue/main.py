#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_sendinblue import SourceSendinblue

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceSendinblue()
    launch(source, sys.argv[1:])
