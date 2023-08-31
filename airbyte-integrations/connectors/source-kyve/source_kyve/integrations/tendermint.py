
import gzip
import json
import logging
import requests
from typing import Any, Iterable, Mapping
from source_kyve.stream import KYVEStream
from airbyte_cdk.sources.streams.core import package_name_from_class
from source_kyve.util import CustomResourceSchemaLoader


logger = logging.getLogger("airbyte")

def flatten_bundle(bundle):
    flattened_bundle = []
    for data_item in bundle:
        flattened_data_item = {}
        flatten_data_item(data_item, flattened_data_item)
        flattened_bundle.append(flattened_data_item)
    return flattened_bundle

def flatten_data_item(d, result, parent_key=''):
    for key, value in d.items():
        new_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, dict):
            flatten_data_item(value, result, new_key)
        else:
            result[new_key] = value


class TendermintStream(KYVEStream):
    def get_json_schema(self) -> Mapping[str, Any]:
        return CustomResourceSchemaLoader(package_name_from_class(self.__class__)).get_schema("tendermint/tendermint")
    
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

            if storage_provider_id != "3":
                # retrieve file from Arweave
                response_from_storage_provider = requests.get(f"https://arweave.net/{storage_id}")
            else:
                response_from_storage_provider = requests.get(f"https://storage.kyve.network/{storage_id}")

            if not response.ok:
                logger.error(f"Reading bundle {storage_id} with status code {response.status_code}")
                # todo future: this is a temporary fix until the bugs with Arweave are solved
                continue
            try:
                decompressed = gzip.decompress(response_from_storage_provider.content)
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

            output = flatten_bundle(decompressed_as_json)
            # extract the value from the key -> value mapping
            yield from output
