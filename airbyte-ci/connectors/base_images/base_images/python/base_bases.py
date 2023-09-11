#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from base_images import common

PYTHON_3_9_18 = common.PublishedDockerImage(
    registry="docker.io",
    image_name="python",
    tag="3.9.18-slim-bookworm",
    sha="44b7f161ed03f85e96d423b9916cdc8cb0509fb970fd643bdbc9896d49e1cad0",
)
