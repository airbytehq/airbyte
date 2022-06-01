#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources.singer.source import BaseSingerSource
from requests import HTTPError
from tap_zoom.client import ZoomClient


class SourceZoomSinger(BaseSingerSource):
    """
    Zoom API Reference: https://marketplace.zoom.us/docs/api-reference/zoom-api
    """

    tap_cmd = "tap-zoom"
    tap_name = "Zoom API"
    api_error = HTTPError
    force_full_refresh = True

    def try_connect(self, logger: AirbyteLogger, config: dict):
        client = ZoomClient(config=config, config_path="")
        client.get(path="users")
