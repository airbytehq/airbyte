#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys

from source_scaffold_source_http import SourceScaffoldSourceHttp

from airbyte_cdk.entrypoint import launch

if __name__ == "__main__":
    source = SourceScaffoldSourceHttp()
    launch(source, sys.argv[1:])
