#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import gzip
import json
import logging
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.streams.http import HttpStream
from source_kyve.util import CustomResourceSchemaLoader

logger = logging.getLogger("airbyte")

# this mapping handles the schema to runtime relation
# this needs to be updated whenever a new schema is integrated
runtime_to_root_file_mapping = {
    "@kyvejs/bitcoin": "bitcoin/block",
    "@kyvejs/celo": "celo/block",
    "@kyvejs/cosmos": "cosmos/block",
    "@kyvejs/evm": "evm/block",
    "@kyvejs/uniswap": "uniswap/event",
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
        # this is KYVE's default schema, if a root_schema is defined
        # the ResourceSchemaLoader automatically resolves the dependency
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {"key": {"type": "integer"}, "value": {"type": "object"}},
            "required": ["key", "value"],
        }
        # in case we have defined a schema file, we can get it from the mapping
        schema_root_file = runtime_to_root_file_mapping.get(self.runtime, None)

        # we update the default schema in case there is a root_file
        if schema_root_file:
            inlay_schema = CustomResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema(schema_root_file)
            schema["properties"]["value"] = inlay_schema
        return schema

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"/kyve/query/v1beta1/finalized_bundles/{self.pool_id}"

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
            # retrieve file from Arweave
            response_from_arweave = requests.get(f"https://arweave.net/{storage_id}")

            if not response.ok:
                logger.error(f"Reading bundle {storage_id} with status code {response.status_code}")
                # todo future: this is a temporary fix until the bugs with Arweave are solved
                continue
            try:
                decompressed = gzip.decompress(response_from_arweave.content)
            except gzip.BadGzipFile as e:
                logger.error(f"Decompressing bundle {storage_id} failed with '{e}'")
                # todo future: this is a temporary fix until the bugs with Arweave are solved
                # todo future: usually this exception should fail
                continue

            # todo future: fail on incorrect hash, enabled after regenesis
            # bundle_hash = bundle.get("bundle_hash")
            # local_hash = hmac.new(b"", msg=decompressed, digestmod=hashlib.sha256).digest().hex()
            # assert local_hash == bundle_hash, print("HASHES DO NOT MATCH")
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
