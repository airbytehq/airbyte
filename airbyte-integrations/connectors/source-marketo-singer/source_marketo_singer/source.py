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

from airbyte_protocol import AirbyteCatalog, AirbyteConnectionStatus, Status
from base_python import AirbyteLogger, CatalogHelper, ConfigContainer
from base_singer import SingerSource

TAP_CMD = "tap-marketo"


class SourceMarketoSinger(SingerSource):
    def __init__(self):
        super().__init__()

    def transform_config(self, raw_config):
        return {
            "endpoint": raw_config["endpoint_url"],
            "identity": raw_config["identity_url"],
            "client_id": raw_config["client_id"],
            "client_secret": raw_config["client_secret"],
            "start_date": raw_config["start_date"],
        }

    def check(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteConnectionStatus:
        try:
            self.discover(logger, config_container)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            logger.error("Exception while connecting to the Marketo API")
            logger.error(str(e))
            return AirbyteConnectionStatus(
                status=Status.FAILED, message="Unable to connect to the Marketo API with the provided credentials. "
            )

    def discover_cmd(self, logger: AirbyteLogger, config_path: str) -> str:
        return f"{TAP_CMD} -c {config_path} --discover"

    def discover(self, logger: AirbyteLogger, config_container: ConfigContainer) -> AirbyteCatalog:
        catalog = super().discover(logger, config_container)
        return CatalogHelper.coerce_catalog_as_full_refresh(catalog)

    def read_cmd(self, logger: AirbyteLogger, config_path: str, catalog_path: str, state_path: str = None) -> str:
        # We don't pass in state to force the tap to run in full refresh since this tap does not respect the replication-method flag.
        return f"{TAP_CMD} -c {config_path} -p {catalog_path}"
