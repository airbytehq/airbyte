"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import requests
from airbyte_protocol import AirbyteCatalog, AirbyteConnectionStatus, Status, SyncMode
from base_python import AirbyteLogger, ConfigContainer
from base_singer import SingerHelper, SingerSource


class SourceGithubSinger(SingerSource):
    def __init__(self):
        super().__init__()

    def check(self, logger, config_container) -> AirbyteConnectionStatus:
        try:

            json_config = config_container.rendered_config
            r = requests.get("https://api.github.com/repos/airbytehq/airbyte/commits", auth=(json_config["access_token"], ""))
            if r.status_code == 200:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                return AirbyteConnectionStatus(status=Status.FAILED, message=r.text)
        except Exception as e:
            logger.error(e)
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{str(e)}")

    def discover_cmd(self, logger: AirbyteLogger, config_path: str) -> str:
        return f"tap-github --config {config_path} --discover"

    def discover(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteCatalog:
        """
        HACK.
        The singer tap does not declare any valid cursors for use in incremental sync. This is because its cursor is not a field on any of the objects
        it returns. But by default the singer tap assumes an incremental sync on all of its output streams. So we alter each steam in the outgoing
        catalog to:
            1. Reflect that it only supports incremental syncs
            2. Add one of the stream's properties (its primary key) as a "bogus" cursor to avoid having an empty cursor_field.
        """
        discover_cmd = self.discover_cmd(logger, config_container.rendered_config_path)
        catalogs = SingerHelper.get_catalogs(logger, discover_cmd)
        singer_catalog = catalogs.singer_catalog
        streams_to_modify = {}
        for stream in singer_catalog["streams"]:
            if "key_properties" in stream and len(stream["key_properties"]) > 0:
                fake_cursor = stream["key_properties"][0]
                streams_to_modify[stream["stream"]] = fake_cursor

        airyte_catalog = catalogs.airbyte_catalog
        for stream in airyte_catalog.streams:
            if stream.name in streams_to_modify:
                stream.supported_sync_modes = [SyncMode.incremental]
                stream.source_defined_cursor = True
                stream.default_cursor_field = [streams_to_modify[stream.name]]

        return catalogs.airbyte_catalog

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        config_option = f"--config {config_path}"
        properties_option = f"--properties {catalog_path}"
        state_option = f"--state {state_path}" if state_path else ""
        return f"tap-github {config_option} {properties_option} {state_option}"
