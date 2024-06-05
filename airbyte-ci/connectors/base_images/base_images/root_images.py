#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from .published_image import PublishedImage

PYTHON_3_9_18 = PublishedImage(
    registry="docker.io",
    repository="python",
    tag="3.9.18-slim-bookworm",
    sha="44b7f161ed03f85e96d423b9916cdc8cb0509fb970fd643bdbc9896d49e1cad0",
)

PYTHON_3_9_19 = PublishedImage(
    registry="docker.io",
    repository="python",
    tag="3.9.19-slim-bookworm",
    sha="088d9217202188598aac37f8db0929345e124a82134ac66b8bb50ee9750b045b",
)
