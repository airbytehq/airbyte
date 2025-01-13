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

PYTHON_3_10_14 = PublishedImage(
    registry="docker.io",
    repository="python",
    tag="3.10.14-slim-bookworm",
    sha="2407c61b1a18067393fecd8a22cf6fceede893b6aaca817bf9fbfe65e33614a3",
)

AMAZON_CORRETTO_21_AL_2023 = PublishedImage(
    registry="docker.io",
    repository="amazoncorretto",
    tag="21-al2023",
    sha="5454cb606e803fce56861fdbc9eab365eaa2ab4f357ceb8c1d56f4f8c8a7bc33",
)
