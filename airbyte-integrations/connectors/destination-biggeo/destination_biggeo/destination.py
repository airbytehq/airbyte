# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
import uuid
from collections import defaultdict
from logging import getLogger
from typing import Any, Dict, Iterable, List, Mapping
from urllib.parse import urljoin

import requests

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)


logger = getLogger("airbyte")

BIGGEO_BASE_URL = "https://studio.biggeo.com"


class DestinationBiggeo(Destination):
    def __init__(self):
        super().__init__()
        self.sync_id = None
        self.session = requests.Session()

    def _get_headers(self, api_key: str) -> Dict[str, str]:
        """Generate headers for API requests."""
        return {
            "Content-Type": "application/json",
            "x-api-key": api_key,
        }

    def _make_api_request(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        data: Dict[str, Any] = None,
        timeout: int = 60,
    ) -> requests.Response:
        """Make an API request with error handling."""
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination.

        :param logger: Logging object to display debug/info/error to the logs
        :param config: Json object containing the configuration of this destination
        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            api_key = config.get("api_key")

            if not api_key:
                return AirbyteConnectionStatus(status=Status.FAILED, message="API Key is required")

            check_url = urljoin(BIGGEO_BASE_URL, "data-sources/v1/check-connection")
            headers = self._get_headers(api_key)

            logger.info(f"Checking connection to BigGeo at {check_url}")

            response = self._make_api_request("GET", check_url, headers)
            result = response.json()

            if result.get("status") == "SUCCEEDED":
                logger.info("Connection check succeeded")
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                error_message = result.get("message", "Unknown error")
                logger.error(f"Connection check failed: {error_message}")
                return AirbyteConnectionStatus(status=Status.FAILED, message=f"Connection failed: {error_message}")

        except Exception as e:
            logger.error(f"Connection check exception: {repr(e)}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")

    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        """
        Reads the input stream of messages to write data to the BigGeo destination.

        :param config: dict of JSON configuration matching the configuration declared in spec.json
        :param input_messages: The stream of input messages received from the source
        :param configured_catalog: The Configured Catalog describing the schema of the data
        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """
        streams = {s.stream.name for s in configured_catalog.streams}
        logger.info(f"Starting write to BigGeo with {len(streams)} streams")

        api_key = config.get("api_key")
        batch_size = config.get("batch_size", 1000)

        post_url = urljoin(BIGGEO_BASE_URL, "data-sources/v1/post-data-source")
        headers = self._get_headers(api_key)

        if not self.sync_id:
            self.sync_id = str(uuid.uuid4())

        logger.info(f"Using sync_id: {self.sync_id}")

        buffer = defaultdict(list)
        records_sent = 0

        def send_batch(stream_name: str, chunks: List[Dict[str, Any]], is_final: bool = False):
            """Send a batch of chunks to the BigGeo API."""
            nonlocal records_sent

            # Only send if there is at least one RECORD chunk or is_final
            has_record = any(chunk.get("type") == "RECORD" for chunk in chunks)
            if not has_record and not is_final:
                logger.debug(f"Skipping send for stream '{stream_name}' - no RECORD chunks in batch.")
                return

            payload = {
                "sync_id": self.sync_id,
                "table_name": stream_name,
                "chunks": chunks,
                "is_final": is_final,
            }

            logger.info(f"Sending {len(chunks)} chunks for stream '{stream_name}' (is_final={is_final})")

            try:
                response = self._make_api_request("POST", post_url, headers, payload)
                result = response.json()
                if result.get("success"):
                    records_processed = result.get("records_processed", 0)
                    records_sent += records_processed
                    logger.info(f"Successfully sent batch. Records processed: {records_processed}")
                    if is_final and result.get("path"):
                        logger.info(f"Data exported to: {result.get('path')}")
                else:
                    error_message = result.get("message", "Unknown error")
                    raise Exception(f"API returned success=false: {error_message}")

            except Exception as e:
                logger.error(f"Failed to send batch: {e}")
                raise

        try:
            for message in input_messages:
                if message.type == Type.STATE:
                    logger.info(f"Processing STATE message")

                    state_chunk = {"type": "STATE", "state": {"data": {}}}

                    for stream_name in buffer.keys():
                        buffer[stream_name].append(state_chunk)

                    for stream_name, chunks in buffer.items():
                        send_batch(stream_name, chunks, is_final=False)

                    buffer.clear()

                    yield message

                elif message.type == Type.RECORD:
                    data = message.record.data
                    stream_name = message.record.stream
                    emitted_at = message.record.emitted_at

                    if stream_name not in streams:
                        logger.debug(f"Stream {stream_name} was not present in configured streams, skipping")
                        continue

                    chunk = {
                        "type": "RECORD",
                        "record": {
                            "stream": stream_name,
                            "data": data,
                            "emitted_at": emitted_at,
                        },
                    }

                    buffer[stream_name].append(chunk)

                    if len(buffer[stream_name]) >= batch_size:
                        send_batch(stream_name, buffer[stream_name], is_final=False)
                        buffer[stream_name].clear()

                else:
                    logger.info(f"Message type {message.type} not supported, skipping")

            for stream_name in streams:
                send_batch(stream_name, buffer[stream_name], is_final=True)

            logger.info(f"Write completed. Total records sent: {records_sent}")

        except Exception as e:
            logger.error(f"Error during write: {e}")
            raise

        finally:
            self.sync_id = None
            self.session.close()
