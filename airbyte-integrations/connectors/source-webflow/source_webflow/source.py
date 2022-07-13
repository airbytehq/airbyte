#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream

from .auth import WebflowTokenAuthenticator
from .webflow_to_airbyte_mapping import WebflowToAirbyteMapping

"""
This module is used for pulling the contents of "collections" out of Webflow, which is a CMS for hosting websites.
A Webflow collection may be a group of items such as "Blog Posts", "Blog Authors", etc.
There may be many collections, each of which can have its own distinct schema. This module will dynamically figure out
which collections are available, and will dynamically create the schema for each collection based on information
extracted from Webflow. It will then download all of the items from all of the selected collections.

Because the amount of data is expected to be "small" (not TB of data), we have not implemented any kind of
incremental downloading of data from Webflow. Each time this code is exectued, it will pull back all of the items
that are contained in each of the desired collections.
"""


# Webflow expects a 'accept-version' header with a value of '1.0.0' (as of May 2022)
WEBFLOW_ACCEPT_VERSION = "1.0.0"


# Basic full refresh stream
class WebflowStream(HttpStream, ABC):
    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL,
    pagination strategy, parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.
    """

    url_base = "https://api.webflow.com/"

    # The following call is need to fix what appears to be  a bug in http.py line 119
    # Bug reported at: https://github.com/airbytehq/airbyte/issues/13283
    @property
    def authenticator(self) -> WebflowTokenAuthenticator:
        return self._session.auth

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Common params e.g. pagination size etc.
        """
        return {}


class CollectionSchema(WebflowStream):
    """
    Gets the schema of the current collection - see: https://developers.webflow.com/#get-collection-with-full-schema, and
    then converts that schema to a json-schema.org-compatible schema that uses supported Airbyte types.

    More info about Webflow schema: https://developers.webflow.com/#get-collection-with-full-schema
    Airbyte data types: https://docs.airbyte.com/understanding-airbyte/supported-data-types/
    """

    #  primary_key is not used as we don't do incremental syncs - https://docs.airbyte.com/understanding-airbyte/connections/
    primary_key = None

    def __init__(self, collection_id: str = None, **kwargs):
        self.collection_id = collection_id
        super().__init__(**kwargs)

    def path(self, **kwargs) -> str:
        """
        See: https://developers.webflow.com/#list-collections
        Returns a list which contains high-level information about each collection.
        """

        path = f"collections/{self.collection_id}"
        return path

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Converts the webflow schema into an Airbyte-compatible schema

        Webflow schema API returns an array of fields contained in the "fields" field.
        Get field name and field type from this array, and then map it to an airbyte-supported type
        """

        response_json = response.json()
        for field in response_json["fields"]:
            try:
                field_name = field["slug"]
                field_type = field["type"]
                field_schema = {field_name: WebflowToAirbyteMapping.webflow_to_airbyte_mapping[field_type]}
                yield field_schema  # get records from the "fields" array
            except Exception as e:
                msg = f"""Encountered an exception parsing schema for Webflow type: {field_type}.
Is "{field_type}" defined in the mapping between Webflow and json schma ? """
                self.logger.exception(msg)

                # Don't eat the exception, raise it again as this needs to be fixed
                raise e

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """This API does not return any information to support pagination"""
        return {}


class CollectionsList(WebflowStream):
    """
    The data that we are generally interested in pulling from Webflow is stored in "Collections".
    Example Collections that may be of interest are: "Blog Posts", "Blog Authors", etc.

    This class provides the functionality for getting a list containing metadata about available collections
    More info https://developers.webflow.com/#list-collections
    """

    #  primary_key is not used as we don't do incremental syncs - https://docs.airbyte.com/understanding-airbyte/connections/
    primary_key = None

    def __init__(self, site_id: str = None, **kwargs):
        self.site_id = site_id
        super().__init__(**kwargs)

    def path(self, **kwargs) -> str:
        """
        See: https://developers.webflow.com/#list-collections
        Returns a list which contains high-level information about each collection.
        """

        path = f"sites/{self.site_id}/collections"
        return path

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        This API returns a list containing json objects. So we can just yield each element from the list
        """
        response_json = response.json()
        yield from response_json

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """This API does not return any information to support pagination"""
        return {}


class CollectionContents(WebflowStream):
    """
    This stream is used for pulling "items" out of a given Webflow collection. Because there is not a fixed number of collections with
    pre-defined names, each stream is an object that uses the passed-in collection name for the stream name.

     Note that because the Webflow API works with collection ids rather than collection names, the collection id is
     used for hitting the Webflow API.

    An example of a collection is "Blog Posts", which contains a list of items, where each item is a JSON-representation of a blog article.
    """

    #  primary_key is not used as we don't do incremental syncs - https://docs.airbyte.com/understanding-airbyte/connections/
    primary_key = None

    # only want to create the name to id lookup table once

    def __init__(self, site_id: str = None, collection_id: str = None, collection_name: str = None, **kwargs):
        """override __init__ to add collection-related variables"""
        self.site_id = site_id
        super().__init__(**kwargs)
        self.collection_name = collection_name
        self.collection_id = collection_id

    @property
    def name(self) -> str:
        return self.collection_name

    def path(self, **kwargs) -> str:
        """
        The path to get the "items" in the requested collection uses the "_id" of the collection in the URL.
        See: https://developers.webflow.com/#items

        return collections/<collection_id>/items
        """
        path = f"collections/{self.collection_id}/items"
        return path

    def next_page_token(self, response: requests.Response) -> Mapping[str, Any]:
        decoded_response = response.json()
        if decoded_response.get("count", 0) != 0 and decoded_response.get("items", []) != []:
            # Webflow uses an offset for pagination https://developers.webflow.com/#item-model
            offset = decoded_response["offset"] + decoded_response["count"]
            return {"offset": offset}
        else:
            return {}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:

        # Webflow default pagination is 100, for debugging pagination we set this to a low value.
        # This should be set back to 100 for production
        params = {"limit": 100}

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Webflow items API returns an array of items contained in the "items" field.
        """

        response_json = response.json()
        # The items API returns records inside a container list called "items"
        for item in response_json["items"]:
            yield item

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        Webflow has an API,but it is not consistent with json-schema.org schemas. We use the CollectionSchema stream
        to get these schemas and to also map them to json-schema format.
        """

        collection_id = self.collection_id
        schema_stream = CollectionSchema(authenticator=self.authenticator, collection_id=collection_id)
        schema_records = schema_stream.read_records(sync_mode="full_refresh")

        # each record corresponds to a property in the json schema. So we loop over each of these properties
        # and add it to the json schema.
        json_schema = {}
        for schema_property in schema_records:
            json_schema.update(schema_property)

        # Manually add in _cid and _id, which are not included in the list of fields sent back from Webflow,
        # but which are necessary for joining data in the database
        extra_fields = {
            "_id": {"type": ["null", "string"]},
            "_cid": {"type": ["null", "string"]},
        }
        json_schema.update(extra_fields)

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "type": "object",
            "properties": json_schema,
        }


class SourceWebflow(AbstractSource):

    """This is the main class that defines the methods that will be called by Airbyte infrastructure"""

    @staticmethod
    def _get_collection_name_to_id_dict(authenticator: str = None, site_id: str = None) -> Mapping[str, str]:
        """
        Most of the Webflow APIs require the collection id, but the streams that we are generating use the collection name.
        This function will return a dictionary containing collection_name: collection_id entries.
        """

        collection_name_to_id_dict = {}

        collections_stream = CollectionsList(authenticator=authenticator, site_id=site_id)
        collections_records = collections_stream.read_records(sync_mode="full_refresh")

        # Loop over the list of records and create a dictionary with name as key, and _id as value
        for collection_obj in collections_records:
            collection_name_to_id_dict[collection_obj["name"]] = collection_obj["_id"]

        return collection_name_to_id_dict

    @staticmethod
    def get_authenticator(config):
        """
        Verifies that the information for setting the header has been set, and returns a class
        which overloads that standard authentication to include additional headers that are required by Webflow.
        """
        api_key = config.get("api_key", None)
        accept_version = WEBFLOW_ACCEPT_VERSION
        if not api_key:
            raise Exception("Config validation error: 'api_key' is a required property")

        auth = WebflowTokenAuthenticator(token=api_key, accept_version=accept_version)
        return auth

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        """
        A check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """

        try:
            # Check that authenticator can be retrieved
            auth = self.get_authenticator(config)
            site_id = config.get("site_id")
            collections_stream = CollectionsList(authenticator=auth, site_id=site_id)
            collections_records = collections_stream.read_records(sync_mode="full_refresh")
            record = next(collections_records)
            logger.info(f"Successfully connected to CollectionsList stream. Pulled one record: {record}")
            return True, None
        except Exception as e:
            return False, e

    def generate_streams(self, authenticator: WebflowTokenAuthenticator, site_id: str) -> List[Stream]:
        """Generates a list of stream by their names."""

        collection_name_to_id_dict = self._get_collection_name_to_id_dict(authenticator=authenticator, site_id=site_id)

        for collection_name, collection_id in collection_name_to_id_dict.items():
            yield CollectionContents(
                authenticator=authenticator,
                site_id=site_id,
                collection_id=collection_id,
                collection_name=collection_name,
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        :return List[Stream]: A list/generator of the streams that Airbyte can pull data from.
        """

        auth = self.get_authenticator(config)
        site_id = config.get("site_id")

        # Return a list (iterator) of the streams that will be available for use.
        # We _dynamically_ generate streams that correspond to Webflow collections (eg. Blog Authors, Blog Posts, etc.)
        streams = self.generate_streams(authenticator=auth, site_id=site_id)

        return streams
