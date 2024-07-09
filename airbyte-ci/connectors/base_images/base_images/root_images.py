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
    sha="e6941b744e8eb9df6cf6baf323d2b9ad1dfe17d118f5efee14634aff4d47c76f",
)
