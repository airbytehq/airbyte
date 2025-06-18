# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
import logging
from typing import Any

from airbyte_cdk.models import AirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from source_exact.api import ExactAPI
from source_exact.streams import CRMAccountClassifications, ExactStream


class SourceExact(AbstractSource):
    def check_connection(self, logger: logging.Logger, config) -> tuple[bool, Any]:
        client_id = (config or {}).get("credentials", {}).get("client_id")
        client_secret = (config or {}).get("credentials", {}).get("client_secret")
        access_token = (config or {}).get("credentials", {}).get("access_token")
        refresh_token = (config or {}).get("credentials", {}).get("refresh_token")
        divisions = (config or {}).get("divisions", [])
        # Set a request to CRMAccountClassification to verify its access

        if not access_token or not refresh_token:
            return False, "Missing access or refresh token"
        if not divisions:
            return False, "Missing divisions"

        api = ExactAPI(config)
        return api.check_connection()

    def streams(self, config) -> list[ExactStream]:
        return [
            CRMAccountClassifications(config),
        ]

    def discover(self, logger: logging.Logger, config) -> AirbyteCatalog:
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

    def spec(self, logger:logging.Logger):
        super().spec(logger)
