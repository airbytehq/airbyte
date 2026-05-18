# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys

from airbyte_cdk.entrypoint import launch

from .source import SourceComfyUI


def main():
    source = SourceComfyUI()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    main()
