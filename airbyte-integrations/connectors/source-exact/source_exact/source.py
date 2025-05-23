import logging

from airbyte_cdk.sources import AbstractSource


class SourceExact(AbstractSource):
    def check_connection(self, logger: logging.Logger, config):
        divisions = (config or {}).get("divisions", [])

        if not divisions:
            return False, "Missing divisions"

        return True, None

    def streams(self, config):
        pass

    def discover(self, logger: logging.Logger, config):
        pass

    def check(self, logger: logging.Logger, config):
        pass

    def read(self, logger: logging.Logger, config, catalog, state=None):
        pass

