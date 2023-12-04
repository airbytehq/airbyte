#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import gzip
import hashlib
import json
import logging
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.http import HttpStream
from source_kyve.utils import query_endpoint

logger = logging.getLogger("airbyte")

# 1: Arweave
# 2: Irys
# 3: KYVE Storage-Provider
storage_provider_gateways = {
    "1": [
        "arweave.net/",
        "arweave.dev/",
        "c7fqu7cwmsb7dsibz2pqicn2gjwn35amtazqg642ettzftl3dk2a.arweave.net/",
        "hkz3zh4oo432n4pxnvylnqjm7nbyeitajmeiwtkttijgyuvfc3sq.arweave.net/",
    ],
    "2": [
        "arweave.net/",
        "https://gateway.irys.xyz/",
        "arweave.dev/",
        "c7fqu7cwmsb7dsibz2pqicn2gjwn35amtazqg642ettzftl3dk2a.arweave.net/",
        "hkz3zh4oo432n4pxnvylnqjm7nbyeitajmeiwtkttijgyuvfc3sq.arweave.net/",
    ],
    "3": ["https://storage.kyve.network/"],
}


class KYVEStream(HttpStream, IncrementalMixin):
    url_base = None

    cursor_field = "offset"
    page_size = 100

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
        # this is an ugly solution but has to parsed by source to be a single item
        self._offset = int(config["start_ids"])

        self.page_size = config["page_size"]
        self.max_pages = config.get("max_pages", None)
        # For incremental querying
        self._cursor_value = None

    def get_json_schema(self) -> Mapping[str, Any]:
        # This is KYVE's default schema and won't be changed.
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {"key": {"type": "string"}, "value": {"type": "object"}},
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

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params["next_page_token"] = next_page_token

        # In case we use incremental streaming, we start with the stored _offset
        offset = stream_state.get(self.cursor_field, self._offset) or 0

        params["pagination.offset"] = offset

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
            latest_bundle = bundles[-1]

            self._cursor_value = latest_bundle.get("id")
        except IndexError:
            bundles = []

        for bundle in bundles:
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

            # extract the value from the key -> value mapping
            yield from decompressed_as_json

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # in case we set a max_pages parameter we need to abort
        if self.max_pages and self._offset >= self.max_pages * self.page_size:
            return

        json_response = response.json()
        next_key = json_response.get("pagination", {}).get("next_key")
        if next_key:
            self._offset += self.page_size
            return {"pagination.offset": self._offset}

    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value}
        else:
            return {self.cursor_field: self._offset}

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._cursor_value = value[self.cursor_field]
