#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""This module declares constants used by the base_images module.
"""

import dagger

REMOTE_REGISTRY = "docker.io"
PLATFORMS_WE_PUBLISH_FOR = (dagger.Platform("linux/amd64"), dagger.Platform("linux/arm64"))
CRANE_IMAGE_ADDRESS = (
    "gcr.io/go-containerregistry/crane/debug:v0.15.1@sha256:f6ddf8e2c47df889e06e33c3e83b84251ac19c8728a670ff39f2ca9e90c4f905"
)
