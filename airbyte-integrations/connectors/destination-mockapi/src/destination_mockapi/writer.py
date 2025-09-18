# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import logging
from typing import Any, Dict, List

from .client import MockAPIClient
from .schemas.deals import map_to_deal_schema
from .schemas.users import map_to_user_schema


logger = logging.getLogger(__name__)


class MockAPIWriter:
    def __init__(self, client: MockAPIClient, batch_size: int = 100):
        self.client = client
        self.batch_size = batch_size
        self.buffer: Dict[str, List[Dict[str, Any]]] = {}

    def write_record(self, stream_name: str, record: Dict[str, Any]) -> None:
        """Write a single record to the buffer"""
        if stream_name not in self.buffer:
            self.buffer[stream_name] = []

        self.buffer[stream_name].append(record)

        # Flush if batch size reached
        if len(self.buffer[stream_name]) >= self.batch_size:
            self._flush_stream(stream_name)

    def flush(self) -> None:
        """Flush all buffered records"""
        for stream_name in list(self.buffer.keys()):
            if self.buffer[stream_name]:
                self._flush_stream(stream_name)

    def _flush_stream(self, stream_name: str) -> None:
        """Flush records for a specific stream"""
        if not self.buffer.get(stream_name):
            return

        records = self.buffer[stream_name]
        logger.info(f"Flushing {len(records)} records for stream {stream_name}")

        try:
            if stream_name.lower() == "users":
                self._write_users(records)
            elif stream_name.lower() == "deals":
                self._write_deals(records)
            else:
                logger.warning(f"Unknown stream: {stream_name}")

            # Clear buffer after successful write
            self.buffer[stream_name] = []

        except Exception as e:
            logger.error(f"Failed to write {stream_name} records: {e}")
            raise

    def _write_users(self, records: List[Dict[str, Any]]) -> None:
        """Write user records to MockAPI"""
        for record in records:
            try:
                mapped_user = map_to_user_schema(record)
                self.client.create_user(mapped_user)
                logger.debug(f"Created user: {mapped_user.get('name', 'Unknown')}")
            except Exception as e:
                logger.error(f"Failed to create user: {e}")
                # Continue with other records

    def _write_deals(self, records: List[Dict[str, Any]]) -> None:
        """Write deal records to MockAPI"""
        for record in records:
            try:
                mapped_deal = map_to_deal_schema(record)
                self.client.create_deal(mapped_deal)
                logger.debug(f"Created deal: {mapped_deal.get('title', 'Unknown')}")
            except Exception as e:
                logger.error(f"Failed to create deal: {e}")
                # Continue with other records
