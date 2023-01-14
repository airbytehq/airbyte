#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
from collections import Counter
from typing import Any, List, Mapping, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from requests_oauthlib import OAuth1
from source_netsuite.constraints import CUSTOM_INCREMENTAL_CURSOR, INCREMENTAL_CURSOR, META_PATH, RECORD_PATH, SCHEMA_HEADERS
from source_netsuite.streams import CustomIncrementalNetsuiteStream, IncrementalNetsuiteStream, NetsuiteStream


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
            for object in object_types:
                try:
                    response = session.get(url=base_url + RECORD_PATH + object, params={"limit": 1})
                    response.raise_for_status()
                    return True, None
                except requests.exceptions.HTTPError as e:
                    return False, e
        else:
            # if `object_types` are not provided, use `Contact` object
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

        logger: logging.Logger = (logging.Logger,)

        input_args = {
            "auth": auth,
            "object_name": object_name,
            "base_url": base_url,
            "start_datetime": start_datetime,
            "window_in_days": window_in_days,
        }
        try:
            schema = schemas[object_name]
            schema_props = schema["properties"]
            if schema_props:
                if INCREMENTAL_CURSOR in schema_props.keys():
                    return IncrementalNetsuiteStream(**input_args)
                elif CUSTOM_INCREMENTAL_CURSOR in schema_props.keys():
                    return CustomIncrementalNetsuiteStream(**input_args)
                else:
                    # all other streams are full_refresh
                    return NetsuiteStream(**input_args)
        except KeyError:
            logger.warn(f"Object `{object_name}` schema has missing `properties` key. Retry...")
            # somethimes object metadata returns data with missing `properties` key,
            # we should try to fetch metadata again to that object
            schemas = self.get_schemas(object_name, session, metadata_url)
            input_args.update(**{"session": session, "metadata_url": metadata_url, "schemas": schemas})
            return self.generate_stream(**input_args)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.auth(config)
        session = self.get_session(auth)
        base_url = self.base_url(config)
        metadata_url = base_url + META_PATH
        object_names = config.get("object_types")

        # retrieve all record types if `object_types` config field is not specified
        if not config.get("object_types"):
            objects_metadata = session.get(metadata_url).json().get("items")
            object_names = [object["name"] for object in objects_metadata]

        input_args = {"session": session, "metadata_url": metadata_url}
        schemas = self.get_schemas(object_names, **input_args)
        input_args.update(
            **{
                "auth": self.auth(config),
                "base_url": base_url,
                "start_datetime": config["start_datetime"],
                "window_in_days": config["window_in_days"],
                "schemas": schemas,
            }
        )
        # build streams
        streams: list = []
        for name in object_names:
            streams.append(self.generate_stream(object_name=name, **input_args))

        return streams
