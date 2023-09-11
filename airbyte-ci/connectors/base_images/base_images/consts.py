#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declares constants used by the base_images module.
"""

from pathlib import Path

import dagger

PROJECT_DIR = Path(__file__).parent.parent
REMOTE_REGISTRY = "docker.io"
PLATFORMS_WE_PUBLISH_FOR = (dagger.Platform("linux/amd64"), dagger.Platform("linux/arm64"))
