#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import gzip
import hashlib
import json
import logging
import math
import sys
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from source_kyve.utils import query_endpoint, split_data_item_in_chunks

logger = logging.getLogger("airbyte")

# 1: Arweave
# 2: Irys
# 3: KYVE Storage-Provider
storage_provider_gateways = {
    "1": [
        "https://arweave.net/",
        "https://arweave.dev/",
        "https://c7fqu7cwmsb7dsibz2pqicn2gjwn35amtazqg642ettzftl3dk2a.arweave.net/",
        "https://hkz3zh4oo432n4pxnvylnqjm7nbyeitajmeiwtkttijgyuvfc3sq.arweave.net/",
    ],
    "2": [
        "https://arweave.net/",
        "https://gateway.irys.xyz/",
        "https://arweave.dev/",
        "https://c7fqu7cwmsb7dsibz2pqicn2gjwn35amtazqg642ettzftl3dk2a.arweave.net/",
        "https://hkz3zh4oo432n4pxnvylnqjm7nbyeitajmeiwtkttijgyuvfc3sq.arweave.net/",
    ],
    "3": ["https://storage.kyve.network/"],
}


class KYVEStream(HttpStream, IncrementalMixin):
    url_base = None

    cursor_field = "offset"

    # Set this as a noop.
    primary_key = None

    name = None

    def __init__(self, config: Mapping[str, Any], pool_data: Mapping[str, Any], **kwargs):
        super().__init__(**kwargs)
        # Here's where we set the variable from our input to pass it down to the source.
        self.pool_id = pool_data.get("id")

        self.name = f"pool_{self.pool_id}"
        self.runtime = pool_data.get("runtime")

        self.url_base = config["url_base"]

        self._offset = int(config["start_ids"])

        self._start_key = int(config["start_keys"])
        self._end_key = int(config["end_keys"])

        self._data_item_size_limit = config["data_item_size_limit"]

        self._reached_end = False

        self.page_size = 100
        self.max_pages = config.get("max_pages", None)

        # For incremental querying
        self._cursor_value = self._offset

    def get_json_schema(self) -> Mapping[str, Any]:
        # This is KYVE's default schema and won't be changed.
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {"key": {"type": "string"}, "value": {"type": "any"}, "offset": {"type": "string"}, "chunk_index": {"type": "number"}},
            "required": ["key", "value"],
        }

        return schema

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"/kyve/v1/bundles/{self.pool_id}"

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # Set the pagesize in the request parameters
        params = {"pagination.limit": self.page_size}

        if self._offset == 0:
            # Handle pagination by inserting the next page's token in the request parameters
            self._offset = stream_state.get(self.cursor_field, self._cursor_value) or 0
        params["pagination.offset"] = self._offset

        # Use next_page_token if existing
        if next_page_token:
            params["pagination.offset"] = next_page_token

        return params

    def parse_response(
            self,
            response: requests.Response,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        try:
            # set the state to store the latest bundle_id
            bundles = response.json().get("finalized_bundles")
            if not len(bundles):
                self._reached_end = True
        except IndexError:
            bundles = []

        for bundle in bundles:
            if int(bundle.get("id")) >= self._cursor_value or self._cursor_value == 0:
                storage_id = bundle.get("storage_id")
                storage_provider_id = bundle.get("storage_provider_id")

                # Load endpoints for each storage_provider
                gateway_endpoints = storage_provider_gateways.get(storage_provider_id)

                # If storage_provider provides gateway_endpoints, query endpoint - otherwise stop syncing.
                if gateway_endpoints is not None:
                    # Try to query each endpoint in the given order and break loop if query was successful
                    # If no endpoint is successful, skip the bundle
                    for endpoint in gateway_endpoints:
                        response_from_storage_provider = query_endpoint(f"{endpoint}{storage_id}")
                        if response_from_storage_provider is not None:
                            break
                    else:
                        logger.error(f"couldn't query any endpoint successfully with storage_id {storage_id}; skipping bundle...")
                        continue
                else:
                    logger.error(f"storage provider with id {storage_provider_id} is not supported ")
                    raise Exception("unsupported storage provider")

                if not response_from_storage_provider.ok:
                    # TODO: add fallback to different storage provider in case resource is unavailable
                    logger.error(f"Reading bundle {storage_id} with status code {response.status_code}")

                try:
                    decompressed = gzip.decompress(response_from_storage_provider.content)
                except gzip.BadGzipFile as e:
                    logger.error(f"Decompressing bundle {storage_id} failed with '{e}'")
                    continue

                # Compare hash of the downloaded data from Arweave with the hash from KYVE.
                # This is required to make sure, that the Arweave Gateway provided the correct data.
                bundle_hash = bundle.get("data_hash")
                local_hash = hashlib.sha256(response_from_storage_provider.content).hexdigest()
                assert local_hash == bundle_hash, print("HASHES DO NOT MATCH")
                decompressed_as_json = json.loads(decompressed)

                # Add offset to each_data_item
                for index, data_item in enumerate(decompressed_as_json):
                    # Add offset and gt100
                    data_item["offset"] = bundle.get("id")

                    if self._data_item_size_limit > 0:
                        # Get size of data_item in MB
                        size_of_data_item = sys.getsizeof(str(data_item)) / (1000*1000)

                        # Split if data_item > 80MB
                        if size_of_data_item > self._data_item_size_limit:
                            print("Data item with key", data_item["key"], "> than", self._data_item_size_limit, "MB with ",
                                  size_of_data_item, "MB; start chunking")
                            chunks_amount = math.ceil(size_of_data_item / (self._data_item_size_limit / 20))
                            chunks = split_data_item_in_chunks(data_item, chunks_amount)
                            decompressed_as_json.pop(index)
                            decompressed_as_json.extend(chunks)
                            print("Chunked successfully")

                # Skip bundle if start_key not reached
                if int(bundle.get("to_key")) < self._start_key:
                    self._cursor_value = int(bundle.get("id")) + 1
                    continue

                # If start_key reached, remove all data items of bundles that have a key
                # smaller than start_key
                if int(bundle.get("from_key")) <= self._start_key <= int(bundle.get("to_key")):
                    decompressed_as_json = [data_item for data_item in decompressed_as_json if self._start_key <= int(data_item.get("key"))
                                            <= self._end_key]
                    yield from decompressed_as_json
                    continue

                # If end_key reached, remove all data items of bundles that have a key
                # bigger than end_key and stop the stream
                if int(bundle.get("from_key")) <= self._end_key <= int(bundle.get("to_key")):
                    decompressed_as_json = [data_item for data_item in decompressed_as_json if self._start_key <= int(data_item.get("key"))
                                            <= self._end_key]
                    self._reached_end = True
                    yield from decompressed_as_json
                    return

                # If end_key already reached, stop stream without syncing anything
                if int(bundle.get("from_key")) > self._end_key:
                    self._reached_end = True
                    return

                # extract the value from the key -> value mapping
                yield from decompressed_as_json
                # Set cursor value to next bundle id
                self._cursor_value = int(bundle.get("id")) + 1

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # in case we set a max_pages parameter we need to abort
        if self.max_pages and self._cursor_value >= self.max_pages * self.page_size:
            return

        self._offset = self._cursor_value

        if self._reached_end:
            return
        else:
            return str(self._offset)

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        else:
            return {self.cursor_field: self._offset}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]
