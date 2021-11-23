#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys

from base_python.entrypoint import launch
from source_freshdesk import SourceFreshdesk

if __name__ == "__main__":
    source = SourceFreshdesk()
    launch(source, sys.argv[1:])
