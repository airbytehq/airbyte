# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""BigGeo source implementation."""

import logging
from typing import Any, Iterable, List, Mapping, Optional, Tuple
from urllib.parse import urljoin

import requests

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream


logger = logging.getLogger("airbyte")

BIGGEO_BASE_URL = "https://studio.biggeo.com"
DEFAULT_CHUNK_SIZE = 1000


class BigGeoStream(Stream):
    """
    Base stream for BigGeo data sources with chunked pagination support.

    This stream fetches data from the BigGeo API using cursor-based pagination.
    It manages sync sessions via syncId for resumable data transfers and fetches
    data in configurable chunk sizes to handle large datasets efficiently.

    Pagination Flow:
    1. First request: No cursor/syncId - API creates a new session
    2. API returns: data[], syncId, nextCursor, hasMore
    3. Subsequent requests: Include syncId and cursor=nextCursor
    4. Continue until hasMore=False
    """

    primary_key = None

    def __init__(self, api_key: str, data_source_name: str, chunk_size: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        self.data_source_name = data_source_name
        self.chunk_size = chunk_size or DEFAULT_CHUNK_SIZE

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

    def _fetch_chunk(
        self,
        cursor: Optional[int] = None,
        sync_id: Optional[str] = None,
    ) -> Mapping[str, Any]:
        """
        Fetch a single chunk of data from the BigGeo API.

        Args:
            cursor: The current offset position (None for first request)
            sync_id: The session ID for tracking sync state (None for first request)

        Returns:
            API response containing: data, syncId, nextCursor, hasMore
        """
        url = urljoin(BIGGEO_BASE_URL, f"data-sources/v1/get-data-source/{self.data_source_name}")
        headers = self._get_headers()

        params = {"chunkSize": str(self.chunk_size)}

        if cursor is not None:
            params["cursor"] = str(cursor)
        if sync_id is not None:
            params["syncId"] = sync_id

        logger.info(f"Fetching chunk from {url} with params: {params}")

        response = requests.get(url, headers=headers, params=params, timeout=300)
        response.raise_for_status()

        return response.json()

    def read_records(
        self,
        sync_mode: str = None,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
        **kwargs,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Read records from the BigGeo API using chunked pagination.

        This method handles the pagination loop, fetching chunks until
        all data has been retrieved.
        """
        sync_id: Optional[str] = None
        cursor: Optional[int] = None
        chunk_number = 0
        total_records = 0

        try:
            while True:
                chunk_number += 1
                logger.info(f"Fetching chunk {chunk_number} (cursor={cursor}, syncId={sync_id})")

                response = self._fetch_chunk(cursor=cursor, sync_id=sync_id)

                # Extract pagination info from response
                data = response.get("data", [])
                sync_id = response.get("syncId")
                next_cursor = response.get("nextCursor")
                has_more = response.get("hasMore", False)

                records_in_chunk = len(data)
                total_records += records_in_chunk

                logger.info(
                    f"Chunk {chunk_number}: received {records_in_chunk} records, "
                    f"hasMore={has_more}, nextCursor={next_cursor}, syncId={sync_id}"
                )

                # Yield each record from the current chunk
                for record in data:
                    yield record

                # Check if we've fetched all data
                if not has_more:
                    logger.info(f"Completed fetching all data. Total chunks: {chunk_number}, Total records: {total_records}")
                    break

                # Update cursor for next iteration
                cursor = next_cursor

                if cursor is None:
                    # Safety check - if hasMore is True but nextCursor is None, something is wrong
                    logger.warning("hasMore=True but nextCursor is None. Stopping pagination.")
                    break

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
        chunk_size = config.get("chunk_size")

        streams = []

        if data_source_name:
            streams.append(
                BigGeoStream(
                    api_key=api_key,
                    data_source_name=data_source_name,
                    chunk_size=chunk_size,
                )
            )
        else:
            logger.warning("No data_source_name specified. Please provide a data_source_name in the configuration.")

        return streams
