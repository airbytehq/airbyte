# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""BigGeo source implementation."""

import logging
from typing import Any, Iterable, List, Mapping, Tuple
from urllib.parse import urljoin

import requests

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream


logger = logging.getLogger("airbyte")

BIGGEO_BASE_URL = "https://studio.biggeo.com"


class BigGeoStream(Stream):
    """Base stream for BigGeo data sources."""

    primary_key = None

    def __init__(self, api_key: str, data_source_name: str, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.data_source_name = data_source_name

    @property
    def name(self) -> str:
        """Return the stream name (the data source name)."""
        return self.data_source_name

    def _get_headers(self) -> dict:
        """Generate headers for API requests."""
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        }

    def read_records(
        self,
        sync_mode: str,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Read records from the BigGeo API.
        """
        url = urljoin(BIGGEO_BASE_URL, f"data-sources/v1/get-data-source/{self.data_source_name}")
        headers = self._get_headers()

        logger.info(f"Fetching data from {url}")

        try:
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()

            data = response.json()

            logger.info(f"Received response from BigGeo API")
            logger.info(f"Response type: {type(data)}")

            if isinstance(data, list):
                logger.info(f"Response is an array with {len(data)} records")
                if data:
                    logger.info(f"First record: {data[0]}")
            elif isinstance(data, dict):
                logger.info(f"Response is a single object: {data}")

            logger.debug(f"Full response data: {data}")

            if isinstance(data, list):
                for record in data:
                    yield record

            elif isinstance(data, dict):
                yield data
            else:
                logger.warning(f"Unexpected response format: {type(data)}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch data from BigGeo: {e}")
            raise

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Return a dynamic JSON schema.
        Since we don't know the structure ahead of time, we use a flexible schema.
        """
        return {
            "type": "object",
            "additionalProperties": True,
            "properties": {},
        }


class SourceBiggeo(AbstractSource):
    """BigGeo source connector."""

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """
        Test if the input configuration can be used to successfully connect to the source.

        :param logger: Logging object to display debug/info/error to the logs
        :param config: Json object containing the configuration of this source
        :return: Tuple of (connection_successful, error_message)
        """
        try:
            api_key = config.get("api_key")

            if not api_key:
                return False, "API Key is required"

            check_url = urljoin(BIGGEO_BASE_URL, "data-sources/v1/check-connection")
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
            }

            logger.info(f"Checking connection to BigGeo at {check_url}")

            response = requests.get(check_url, headers=headers, timeout=60)
            response.raise_for_status()

            result = response.json()

            if result.get("status") == "SUCCEEDED":
                logger.info("Connection check succeeded")
                return True, None
            else:
                error_message = result.get("message", "Unknown error")
                logger.error(f"Connection check failed: {error_message}")
                return False, f"Connection failed: {error_message}"

        except requests.exceptions.RequestException as e:
            logger.error(f"Connection check exception: {repr(e)}")
            return False, f"Connection error: {repr(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during connection check: {repr(e)}")
            return False, f"An exception occurred: {repr(e)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        Return a list of streams available in this source.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        :return: List of streams
        """
        api_key = config.get("api_key")
        data_source_name = config.get("data_source_name")

        streams = []

        if data_source_name:
            streams.append(BigGeoStream(api_key=api_key, data_source_name=data_source_name))
        else:
            logger.warning("No data_source_name specified. Please provide a data_source_name in the configuration.")
            pass

        return streams
