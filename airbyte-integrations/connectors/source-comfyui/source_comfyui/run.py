# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import sys

from airbyte_cdk.entrypoint import launch

from source_comfyui.source import SourceComfyUI


def run():
    source = SourceComfyUI()
    launch(source, sys.argv[1:])


if __name__ == "__main__":
    run()
