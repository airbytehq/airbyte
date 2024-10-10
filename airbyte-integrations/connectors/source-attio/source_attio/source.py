#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
import json
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

# Experimentally, record endpoint latency scales sub-linearly up until about 1,000 responses
DEFAULT_RECORDS_LIMIT = 1000

# We set attributes limit to max allowed by response
DEFAULT_ATTRIBUTES_LIMIT = 1000


class AttioStream(HttpStream, ABC):
    url_base = "https://api.attio.com/v2/"

    # primary_key is not used as we don't do incremental syncs on any streams - https://docs.airbyte.com/understanding-airbyte/connections/
    primary_key = None

    def request_headers(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        """
        Authentication headers will overwrite any overlapping headers returned from this method.
        Authentication headers are handled by an HttpAuthenticator.
        """
        return {"Content-Type": "application/json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # Default to no pagination by returning None
        return None


class WorkspaceMembers(AttioStream):
    def path(self, **kwags) -> str:
        return "workspace_members"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        items = response.json()["data"]
        for member in items:
            member["workspace_id"] = member["id"]["workspace_id"]
            member["workspace_member_id"] = member["id"]["workspace_member_id"]
            del member["id"]
        return items


class Objects(AttioStream):
    """
    The stream responsible for returning the list of objects in the workspace.
    Not a dynamic stream like ObjectAttribute and Record; we have just one of these.
    """

    def path(self, **kwags) -> str:
        return "objects"

    def parse_response(self, response: requests.Response, **kwags) -> Iterable[Mapping]:
        items = response.json()["data"]
        for item in items:
            item["workspace_id"] = item["id"]["workspace_id"]
            item["object_id"] = item["id"]["object_id"]
            del item["id"]
        return items


class ObjectAttributes(AttioStream):
    """
    This stream is responsible for handling attributes for a given object in the workspace.

    Like the Record stream below, we generate one stream per object in the workspace, meaning we get
    a PeopleAttribute, a CompanyAttribute, and so on.
    """

    offset = 0

    def __init__(self, object_slug: str, object_id: str, limit=DEFAULT_ATTRIBUTES_LIMIT, **kwargs):
        self.object_slug = object_slug
        self.object_id = object_id
        self.limit = limit
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return f"{self.object_slug}_attributes"

    @property
    def use_cache(self) -> bool:
        return True

    def path(self, next_page_token, **kwags) -> str:
        """
        The path to the list attributes endpoint
        See: https://developers.attio.com/reference/get_v2-target-identifier-attributes
        """
        return f"objects/{self.object_id}/attributes"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        items = response.json()["data"]
        for item in items:
            item["workspace_id"] = item["id"]["workspace_id"]
            item["object_id"] = item["id"]["object_id"]
            item["attribute_id"] = item["id"]["attribute_id"]
            del item["id"]

            item["config_currency_display_type"] = item["config"]["currency"].get("display_type")
            item["config_currency_default_currency_code"] = item["config"]["currency"].get("default_currency_code")

            config_record_reference_allowed_object_ids = item["config"]["record_reference"].get("allowed_object_ids")
            item["config_record_reference_allowed_object_ids"] = config_record_reference_allowed_object_ids
            del item["config"]

            item["relationship"] = item["relationship"]["id"]

        return items

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Dynamically creates the schema for each stream that is created.
        We need to do this dynamically rather than in a JSON file as the name of each stream is
        dynamic, even if the schema is shared between them all.
        """
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "object_id": {"type": "string"},
                "attribute_id": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": ["string", "null"]},
                "api_slug": {"type": "string"},
                "type": {"type": "string"},
                "is_system_attribute": {"type": "boolean"},
                "is_writable": {"type": "boolean"},
                "is_required": {"type": "boolean"},
                "is_unique": {"type": "boolean"},
                "is_multiselect": {"type": "boolean"},
                "is_default_value_enabled": {"type": "boolean"},
                "is_archived": {"type": "boolean"},
                "default_value": {"type": ["string", "null"]},  # JSON serialized
                "relationship": {
                    "type": ["object", "null"],
                    "properties": {
                        "workspace_id": {"type": "string"},
                        "object_id": {"type": "string"},
                        "attribute_id": {"type": "string"},
                    },
                },
                "config_record_reference_allowed_object_ids": {"type": ["array", "null"], "items": {"type": "string"}},
                "config_currency_display_type": {"type": ["string", "null"]},
                "config_currency_default_currency_code": {"type": ["string", "null"]},
                "created_at": {"type": "string"},  # ISO 8601 timestamp
            },
        }

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        params = {"limit": self.limit, "offset": self.offset}

        if next_page_token is not None and next_page_token.get("offset") is not None:
            params["offset"] = next_page_token["offset"]

        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        num_items = len(stream_data["data"])

        if num_items < self.limit:
            return None

        self.offset += num_items
        return {"offset": self.offset}


class Records(AttioStream):
    """
    This stream is responsible for handling records for a given object in the workspace.
    Although all workspaces will have people and company objects enabled, there may also be other
    standard (e.g. users, deals) or custom (e.g. projects, tasks, ...) objects enabled.
    """

    offset = 0

    def __init__(self, object_slug: str, object_id: str, limit=DEFAULT_RECORDS_LIMIT, **kwargs):
        self.object_slug = object_slug
        self.object_id = object_id
        self.limit = limit
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return self.object_slug

    @property
    def http_method(self) -> str:
        return "POST"

    def path(self, **kwags) -> str:
        """
        The path to the query endpoint to get the list of records.
        See: https://developers.attio.com/reference/post_v2-objects-object-records-query
        """
        return f"objects/{self.object_id}/records/query"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Conforms to the schema returned by get_json_schema
        """
        object_id = self.object_id
        object_slug = self.object_slug

        attributes_stream = ObjectAttributes(authenticator=self.authenticator, object_id=object_id, object_slug=object_slug)
        # Attributes stream is cached
        attributes = list(attributes_stream.read_records(sync_mode=SyncMode.full_refresh))

        response_json = response.json()
        for record in response_json["data"]:
            # Flatten ID columns
            record["workspace_id"] = record["id"]["workspace_id"]
            record["object_id"] = record["id"]["object_id"]
            record["record_id"] = record["id"]["record_id"]
            del record["id"]

            # Iterate and output values in conformance with the schema generated by get_json_schema.
            # values is a dict from attribute api_slug to an array of values.
            values = record["values"]

            del record["values"]

            for attribute in attributes:
                t = attribute["type"]

                slug = attribute["api_slug"]
                is_multi = attribute["is_multiselect"]
                num_allowed_objects = (
                    0
                    if attribute["config_record_reference_allowed_object_ids"] is None
                    else len(attribute["config_record_reference_allowed_object_ids"])
                )

                vs = values[slug]

                if t == "text" and not is_multi:
                    record[slug] = None if len(vs) == 0 else vs[0]["value"]
                elif t == "number" and not is_multi:
                    record[slug] = None if len(vs) == 0 else vs[0]["value"]
                elif t == "checkbox" and not is_multi:
                    record[slug] = None if len(vs) == 0 else vs[0]["value"]
                elif t == "currency" and not is_multi:
                    record[slug] = None if len(vs) == 0 else vs[0]["currency_value"]
                elif t == "date" and not is_multi:
                    record[slug] = None if len(vs) == 0 else vs[0]["value"]
                elif t == "timestamp" and not is_multi:
                    record[slug] = None if len(vs) == 0 else vs[0]["value"]
                elif t == "rating" and not is_multi:
                    record[slug] = None if len(vs) == 0 else vs[0]["value"]
                elif t == "status" and not is_multi:
                    record[slug] = None if len(vs) == 0 else vs[0]["status"]["title"]
                elif t == "select" and not is_multi:
                    record[slug] = None if len(vs) == 0 else vs[0]["option"]["title"]
                elif t == "select" and is_multi:
                    record[slug] = [v["option"]["title"] for v in vs]
                elif t == "record-reference" and not is_multi:
                    if len(vs) == 0:
                        record[slug] = None
                    elif num_allowed_objects == 1:
                        record[slug] = vs[0]["target_record_id"]
                    else:
                        record[slug] = {
                            "target_object": vs[0]["target_object"],
                            "target_record_id": vs[0]["target_record_id"],
                        }
                elif t == "record-reference" and is_multi:
                    record[slug] = [
                        (
                            v["target_record_id"]
                            if num_allowed_objects == 1
                            else {
                                "target_object": v["target_object"],
                                "target_record_id": v["target_record_id"],
                            }
                        )
                        for v in vs
                    ]
                elif t == "actor-reference" and not is_multi:
                    record[slug] = (
                        None
                        if len(vs) == 0
                        else {
                            "referenced_actor_id": vs[0]["referenced_actor_id"],
                            "referenced_actor_type": vs[0]["referenced_actor_type"],
                        }
                    )
                elif t == "actor-reference" and is_multi:
                    record[slug] = [
                        {"referenced_actor_id": v["referenced_actor_id"], "referenced_actor_type": v["referenced_actor_type"]} for v in vs
                    ]
                elif t == "location" and not is_multi:
                    record[slug + "_line_1"] = None if len(vs) == 0 else vs[0]["line_1"]
                    record[slug + "_line_2"] = None if len(vs) == 0 else vs[0]["line_2"]
                    record[slug + "_line_3"] = None if len(vs) == 0 else vs[0]["line_3"]
                    record[slug + "_line_4"] = None if len(vs) == 0 else vs[0]["line_4"]
                    record[slug + "_locality"] = None if len(vs) == 0 else vs[0]["locality"]
                    record[slug + "_region"] = None if len(vs) == 0 else vs[0]["region"]
                    record[slug + "_postcode"] = None if len(vs) == 0 else vs[0]["postcode"]
                    record[slug + "_country_code"] = None if len(vs) == 0 else vs[0]["country_code"]
                    record[slug + "_latitude"] = None if len(vs) == 0 else vs[0]["latitude"]
                    record[slug + "_longitude"] = None if len(vs) == 0 else vs[0]["longitude"]
                elif t == "email-address" and not is_multi:
                    record[slug] = None if len(vs) == 0 else vs[0]["email_address"]
                elif t == "email-address" and is_multi:
                    record[slug] = [v["email_address"] for v in vs]
                elif t == "domain" and is_multi:
                    record[slug] = [v["domain"] for v in vs]
                elif t == "domain" and not is_multi:
                    record[slug] = None if len(vs) == 0 else vs[0]["domain"]
                elif t == "phone-number" and is_multi:
                    record[slug] = [v["phone_number"] for v in vs]
                elif t == "personal-name" and not is_multi:
                    record[slug + "_first_name"] = None if len(vs) == 0 else vs[0]["first_name"]
                    record[slug + "_last_name"] = None if len(vs) == 0 else vs[0]["last_name"]
                    record[slug + "_full_name"] = None if len(vs) == 0 else vs[0]["full_name"]
                elif t == "interaction" and not is_multi:
                    record[slug] = {
                        "interaction_type": None if len(vs) == 0 else vs[0]["interaction_type"],
                        "interacted_at": None if len(vs) == 0 else vs[0]["interacted_at"],
                        "owner_actor_type": None if len(vs) == 0 else vs[0]["owner_actor"]["type"],
                        "owner_actor_id": None if len(vs) == 0 else vs[0]["owner_actor"]["id"],
                    }
                    continue

            yield record

    def request_body_json(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        data = {
            "limit": self.limit,
            "offset": self.offset,
            "sorts": [{"direction": "asc", "attribute": "created_at"}],  # sort consistently, oldest to newest
        }

        if next_page_token is not None and next_page_token.get("offset") is not None:
            data["offset"] = next_page_token["offset"]

        return data

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        stream_data = response.json()
        num_items = len(stream_data["data"])

        if num_items < self.limit:
            return None

        self.offset += num_items
        return {"offset": self.offset}

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Dynamically creates the schema for each stream that is created.
        For example the people stream will have one schema, deals would have another, and so on.
        A record stream schema is determined from the object and the attributes of that object.
        """
        object_id = self.object_id
        object_slug = self.object_slug

        attributes_stream = ObjectAttributes(authenticator=self.authenticator, object_id=object_id, object_slug=object_slug)
        attributes = attributes_stream.read_records(sync_mode=SyncMode.full_refresh)

        properties = {
            "workspace_id": {"type": "string"},
            "object_id": {"type": "string"},
            "record_id": {"type": "string"},
        }

        for attr in attributes:
            slug = attr["api_slug"]
            if attr["type"] == "text" and not attr["is_multiselect"]:
                properties[slug] = {"type": ["string", "null"]}
            elif attr["type"] == "number" and not attr["is_multiselect"]:
                properties[slug] = {"type": ["number", "null"]}
            elif attr["type"] == "checkbox" and not attr["is_multiselect"]:
                properties[slug] = {"type": "boolean"}
            elif attr["type"] == "currency" and not attr["is_multiselect"]:
                properties[slug] = {"type": ["number", "null"]}
            elif attr["type"] == "date" and not attr["is_multiselect"]:
                properties[slug] = {"type": ["string", "null"], "format": "date"}
            elif attr["type"] == "timestamp" and not attr["is_multiselect"]:
                properties[slug] = {"type": ["string", "null"], "format": "date-time", "airbyte_type": "timestamp_with_timezone"}
            elif attr["type"] == "rating" and not attr["is_multiselect"]:
                properties[slug] = {"type": ["integer", "null"]}
            elif attr["type"] == "status" and not attr["is_multiselect"]:
                properties[slug] = {"type": ["string", "null"]}
            elif attr["type"] == "select" and attr["is_multiselect"]:
                properties[slug] = {"type": "array", "items": {"type": "string"}}
            elif attr["type"] == "select" and not attr["is_multiselect"]:
                properties[slug] = {"type": ["string", "null"]}
            elif attr["type"] == "record-reference" and not attr["is_multiselect"]:
                # If we only have a single allow object, return just the ID.
                # This makes joining and reading data much easier for the user.
                # However, if we return multiple allowed objects, we need to return the object too
                # so we can disambiguate the record across different objects where IDs might clash.
                # Note that zero allowed objects should be interpreted as allowing all objects.
                num_allowed_objects = (
                    0
                    if attr["config_record_reference_allowed_object_ids"] is None
                    else len(attr["config_record_reference_allowed_object_ids"])
                )

                if num_allowed_objects == 1:
                    properties[slug] = {
                        "type": ["string", "null"],
                    }
                else:
                    properties[slug] = {
                        "type": ["object", "null"],
                        "properties": {
                            "target_object": {"type": "string"},
                            "target_record_id": {"type": "string"},
                        },
                    }
            elif attr["type"] == "record-reference" and attr["is_multiselect"]:
                num_allowed_objects = (
                    0
                    if attr["config_record_reference_allowed_object_ids"] is None
                    else len(attr["config_record_reference_allowed_object_ids"])
                )
                if num_allowed_objects == 1:
                    properties[slug] = {"type": "array", "items": {"type": "string"}}
                else:
                    properties[slug] = {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "target_object": {"type": "string"},
                                "target_record_id": {"type": "string"},
                            },
                        },
                    }
            elif attr["type"] == "actor-reference" and attr["is_multiselect"]:
                properties[slug] = {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "referenced_actor_id": {"type": "string"},
                            "referenced_actor_type": {"type": "string"},
                        },
                    },
                }
            elif attr["type"] == "actor-reference" and not attr["is_multiselect"]:
                properties[slug] = {
                    "type": ["object", "null"],
                    "properties": {
                        "referenced_actor_id": {"type": "string"},
                        "referenced_actor_type": {"type": "string"},
                    },
                }
            elif attr["type"] == "location" and not attr["is_multiselect"]:
                properties[slug + "_line_1"] = {"type": ["string", "null"]}
                properties[slug + "_line_2"] = {"type": ["string", "null"]}
                properties[slug + "_line_3"] = {"type": ["string", "null"]}
                properties[slug + "_line_4"] = {"type": ["string", "null"]}
                properties[slug + "_locality"] = {"type": ["string", "null"]}
                properties[slug + "_region"] = {"type": ["string", "null"]}
                properties[slug + "_postcode"] = {"type": ["string", "null"]}
                properties[slug + "_country_code"] = {"type": ["string", "null"]}
                properties[slug + "_latitude"] = {"type": ["string", "null"]}
                properties[slug + "_longitude"] = {"type": ["string", "null"]}
            elif attr["type"] == "domain" and attr["is_multiselect"]:
                properties[slug] = {"type": "array", "items": {"type": "string"}}
            elif attr["type"] == "email-address" and attr["is_multiselect"]:
                properties[slug] = {"type": "array", "items": {"type": "string"}}
            elif attr["type"] == "email-address" and not attr["is_multiselect"]:
                properties[slug] = {"type": ["string", "null"]}
            elif attr["type"] == "phone-number" and attr["is_multiselect"]:
                properties[slug] = {"type": "array", "items": {"type": "string"}}
            elif attr["type"] == "personal-name" and not attr["is_multiselect"]:
                properties[slug + "_first_name"] = {"type": ["string", "null"]}
                properties[slug + "_last_name"] = {"type": ["string", "null"]}
                properties[slug + "_full_name"] = {"type": ["string", "null"]}
            elif attr["type"] == "interaction" and not attr["is_multiselect"]:
                properties[slug] = {
                    "type": ["object", "null"],
                    "properties": {
                        "interaction_type": {"type": "string"},
                        "interacted_at": {"type": "string", "airbyte_type": "timestamp_with_timezone", "format": "date-time"},
                        "owner_actor_type": {"type": ["string", "null"]},
                        "owner_actor_id": {"type": ["string", "null"]},
                    },
                }
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "type": "object",
            "properties": properties,
        }


class SourceAttio(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            response = requests.get(
                "https://api.attio.com/v2/self",
                headers={"Authorization": f"Bearer {config['access_token']}", "Content-Type": "application/json"},
            )
            response.raise_for_status()
            try:
                assert response.json()["active"] == True
            except Exception as e:
                raise Exception("Connection is inactive")
        except Exception as e:
            return False, e

        return True, None

    def generate_object_streams(self, authenticator: TokenAuthenticator) -> List[Stream]:
        """
        Generates a record and attribute streams for each object in the workspace.
        An ObjectStream is also returned from this function.
        """

        objects_stream = Objects(authenticator)
        streams = [objects_stream]
        objects = objects_stream.read_records(sync_mode=SyncMode.full_refresh)

        for object in objects:
            record_stream = Records(authenticator=authenticator, object_id=object["object_id"], object_slug=object["api_slug"])
            attribute_stream = ObjectAttributes(authenticator=authenticator, object_id=object["object_id"], object_slug=object["api_slug"])
            streams.append(record_stream)
            streams.append(attribute_stream)

        return streams

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        :return List[Stream]: A list/generator of the streams that Airbyte can pull data from.
        """

        authenticator = TokenAuthenticator(config["access_token"])

        static_streams = [
            WorkspaceMembers(authenticator=authenticator),
        ]

        record_streams = self.generate_object_streams(authenticator)

        return static_streams + record_streams
