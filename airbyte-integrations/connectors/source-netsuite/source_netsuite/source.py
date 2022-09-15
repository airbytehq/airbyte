#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from collections import Counter
from typing import Any, List, Mapping, Tuple, Union

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

    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
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

    def get_schemas(self, object_names: Union[List[str], str], session: requests.Session, metadata_url: str) -> Mapping[str, Any]:
        # fetch schemas
        if isinstance(object_names, list):
            return {object_name: session.get(metadata_url + object_name, headers=SCHEMA_HEADERS).json() for object_name in object_names}
        elif isinstance(object_names, str):
            return {object_names: session.get(metadata_url + object_names, headers=SCHEMA_HEADERS).json()}

    def generate_stream(
        self,
        session: requests.Session,
        metadata_url: str,
        schemas: dict,
        object_name: str,
        auth: OAuth1,
        base_url: str,
        start_datetime: str,
        window_in_days: int,
    ) -> Union[NetsuiteStream, IncrementalNetsuiteStream, CustomIncrementalNetsuiteStream]:
        # try to build the stream instance dynamicaly
        try:
            schema = schemas[object_name]
            schema_props = schema["properties"]
            if schema_props:
                if "lastModifiedDate" in schema_props.keys():
                    # if stream has `lastModifiedDate` as cursor - it's incremental
                    return IncrementalNetsuiteStream(auth, object_name, base_url, start_datetime, window_in_days)
                elif "lastmodified" in schema_props.keys():
                    # if stream has `lastmodified` as cursor - it's custom incrermental
                    return CustomIncrementalNetsuiteStream(auth, object_name, base_url, start_datetime, window_in_days)
                else:
                    # all other streams are full_refresh
                    return NetsuiteStream(auth, object_name, base_url, start_datetime, window_in_days)
        except KeyError:
            print(f"Object `{object_name}` schema has missing `properties` key. Retry...")
            # somethimes object metadata returns data with missing `properties` key,
            # we should try to fetch metadata again to that object
            self.get_schemas(object_name, session, metadata_url)
            self.generate_stream(session, metadata_url, schemas, object_name, auth, base_url, start_datetime, window_in_days)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        base_url = self.base_url(config)
        metadata_url = base_url + META_PATH
        auth = self.auth(config)
        session = self.get_session(auth)
        object_names = config.get("object_types", [])
        start_datetime = config["start_datetime"]
        window_in_days = config["window_in_days"]

        # retrieve all record types if `object_types` config field is not specified
        if not object_names:
            objects_metadata = session.get(metadata_url).json().get("items")
            object_names = [object["name"] for object in objects_metadata]

        schemas = self.get_schemas(object_names, session, metadata_url)

        # build streams
        streams: list = []
        for name in object_names:
            streams.append(self.generate_stream(session, metadata_url, schemas, name, auth, base_url, start_datetime, window_in_days))

        return streams
