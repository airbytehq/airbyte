#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from base_images.registries import VersionRegistry

from .common import AirbytePythonConnectorBaseImage

VERSION_REGISTRY: VersionRegistry = VersionRegistry.build_from_package(AirbytePythonConnectorBaseImage, __name__, __path__)
