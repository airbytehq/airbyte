import logging

from source_exact.streams import CRMAccountClassifications, ExactStream

from airbyte_cdk.models import AirbyteCatalog, AirbyteConnectionStatus, Status
from airbyte_cdk.sources import AbstractSource


class SourceExact(AbstractSource):
    def check_connection(self, logger: logging.Logger, config):
        divisions = (config or {}).get("divisions", [])

        if not divisions:
            return False, "Missing divisions"

        return True, None

    def streams(self, config) -> list[ExactStream]:
        return [CRMAccountClassifications(config),]

    def discover(
        self, logger: logging.Logger, config
    ) -> AirbyteCatalog:
        """Implements the Discover operation from the Airbyte Specification.
        See https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#discover.

        This method filters out any unauthorized streams from the list of all streams this connector supports.
        """

        filtered = []
        for stream in self.streams(config):
            if stream.test_access():
                filtered.append(stream.as_airbyte_stream())
            else:
                logger.info(f"Filtered out following stream: {stream.name}")

        return AirbyteCatalog(streams=filtered)

    def check(self, logger: logging.Logger, config) -> AirbyteConnectionStatus:
        try:
            """Connect to the Exact Online API and check the connection."""
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")

    def read(self, logger: logging.Logger, config, catalog, state=None):
        pass

