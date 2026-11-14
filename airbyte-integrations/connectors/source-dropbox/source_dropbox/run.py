# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys

from airbyte_cdk.entrypoint import launch
from source_dropbox.source import SourceDropbox


def main() -> None:
    launch(SourceDropbox(), sys.argv[1:])


if __name__ == "__main__":
    main()
