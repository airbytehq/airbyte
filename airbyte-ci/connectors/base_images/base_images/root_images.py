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

PYTHON_3_11_11 = PublishedImage(
    registry="docker.io",
    repository="python",
    tag="3.11.11-slim-bookworm",
    sha="6ed5bff4d7d377e2a27d9285553b8c21cfccc4f00881de1b24c9bc8d90016e82",
)

AMAZON_CORRETTO_21_AL_2023 = PublishedImage(
    registry="docker.io",
    repository="amazoncorretto",
    tag="21-al2023",
    sha="c90f38f8a5c4494cb773a984dc9fa9a727b3e6c2f2ee2cba27c834a6e101af0d",
)
