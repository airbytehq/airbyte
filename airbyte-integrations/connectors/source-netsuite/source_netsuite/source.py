#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from collections import Counter
from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from requests_oauthlib import OAuth1
from source_netsuite.streams import (
    META_PATH,
    RECORD_PATH,
    SCHEMA_HEADERS,
    CustomIncrementalNetsuiteStream,
    IncrementalNetsuiteStream,
    NetsuiteStream,
)


class SourceNetsuite(AbstractSource):
    def auth(self, config: Mapping[str, Any]) -> OAuth1:
        return OAuth1(
            client_key=config["consumer_key"],
            client_secret=config["consumer_secret"],
            resource_owner_key=config["token_key"],
            resource_owner_secret=config["token_secret"],
            realm=config["realm"],
            signature_method="HMAC-SHA256",
        )

    def base_url(self, config: Mapping[str, Any]) -> str:
        realm = config["realm"]
        subdomain = realm.lower().replace("_", "-")
        return f"https://{subdomain}.suitetalk.api.netsuite.com"

    def get_session(self, auth: OAuth1) -> requests.Session:
        session = requests.Session()
        session.auth = auth
        return session

    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        auth = self.auth(config)
        object_types = config.get("object_types")
        base_url = self.base_url(config)
        session = self.get_session(auth)
        # if record types are specified make sure they are valid
        if object_types:
            # ensure there are no duplicate record types as this will break Airbyte
            duplicates = [k for k, v in Counter(object_types).items() if v > 1]
            if duplicates:
                return False, f'Duplicate record type: {", ".join(duplicates)}'
            # check connectivity to all provided `object_types`
            url = base_url + RECORD_PATH
            for object in object_types:
                try:
                    response = session.get(url=url + object, params={"limit": 1})
                    response.raise_for_status()
                    return True, None
                except requests.exceptions.HTTPError as e:
                    return False, e
        else:
            # if `object_types` are not provided, use `Contact` stream
            # there should be at least 1 contact available in every NetSuite account by default.
            url = base_url + RECORD_PATH + "contact"
            try:
                response = session.get(url=url, params={"limit": 1})
                response.raise_for_status()
                return True, None
            except requests.exceptions.HTTPError as e:
                return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        base_url = self.base_url(config)
        auth = self.auth(config)
        start_datetime = config["start_datetime"]
        window_in_days = config["window_in_days"]
        session = self.get_session(auth)
        metadata_url = base_url + META_PATH
        object_names = config.get("object_types", [])

        if not object_names:
            # retrieve all record types
            objects_metadata = session.get(metadata_url).json().get("items")
            object_names = [object["name"] for object in objects_metadata]

        # fetch schemas
        schemas = {n: session.get(metadata_url + n, headers=SCHEMA_HEADERS).json() for n in object_names}
        # get incremental object names
        # incremental streams must have a `lastModifiedDate` property
        incremental_object_names = [n for n in object_names if schemas[n]["properties"].get("lastModifiedDate")]
        # get custom incremental object names
        # custom incremental streams must have a `lastmodified` property
        custom_incremental_object_names = [n for n in object_names if schemas[n]["properties"].get("lastmodified")]
        # get full-refresh object names
        standard_object_names = [n for n in object_names if n not in incremental_object_names]

        incremental_streams = [
            IncrementalNetsuiteStream(auth, name, base_url, start_datetime, window_in_days) for name in incremental_object_names
        ]
        custom_incremental_streams = [
            CustomIncrementalNetsuiteStream(auth, name, base_url, start_datetime, window_in_days)
            for name in custom_incremental_object_names
        ]
        streams = [NetsuiteStream(auth, name, base_url, start_datetime, window_in_days) for name in standard_object_names]

        return streams + incremental_streams + custom_incremental_streams
