# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, MutableMapping, Optional

import requests
from airbyte_cdk.connector_builder.connector_builder_handler import resolve_manifest
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config
from source_instagram import SourceInstagram

from .common import remove_params_from_url

GRAPH_URL = resolve_manifest(source=SourceInstagram()).record.data["manifest"]["definitions"]["base_requester"]["url_base"]


def get_http_response(path: str, request_params: Dict, config: Config) -> Optional[MutableMapping[str, Any]]:
    url = f"{GRAPH_URL}/{path}"
    token = config["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    params = {
        **request_params,
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()


@dataclass
class InstagramClearUrlTransformation(RecordTransformation):
    def transform(self, record: MutableMapping[str, Any], config: Optional[Config] = None, **kwargs) -> MutableMapping[str, Any]:
        """
        Transforms the given record by removing specific query parameters from certain URLs to ensure consistency
        and prevent test failures due to dynamic parameters.

        Specifically, this function removes the `_nc_rid` parameter from the `media_url` and the `ccb` parameter
        from the `profile_picture_url`. The `_nc_rid` parameter is generated anew each time and the `ccb` parameter
        can change its value, which can cause tests to fail when checking for identity.

        Removing these parameters does not invalidate the URLs. The links remain correct and functional, allowing
        users to view the video or see the picture.
        """
        if record.get("media_url"):
            record["media_url"] = remove_params_from_url(record["media_url"], params=["_nc_rid"])
        if record.get("profile_picture_url"):
            record["profile_picture_url"] = remove_params_from_url(record["profile_picture_url"], params=["ccb"])

        return record


@dataclass
class InstagramMediaChildrenTransformation(RecordTransformation):
    def transform(self, record: MutableMapping[str, Any], config: Optional[Config] = None, **kwargs) -> MutableMapping[str, Any]:
        """
        Transforms the 'children' field in the record, which is an array of Media IDs with a common Media parent.
        This transformation fetches detailed information for each Media ID from the /media endpoint and updates the 'children' array
        with this information.

        Example input:
            "children": {
                  "data": [
                    {
                      "id": "7608776690540"
                    },
                    {
                      "id": "2896800415362"
                    }
                  ]
                }

        After fetching information for each Media ID:
            children:
                [
                  {
                    "id": "7608776690540",
                    "ig_id": "2521545917836833225",
                    "media_type": "IMAGE",
                    "media_url": "https://fake_url?_nc_cat=...",
                    // more fields
                  },
                  {
                    "id": "2896800415362",
                    "ig_id": "2521545917736276706",
                    "media_type": "IMAGE",
                    "media_url": "https://fake_url?_nc_cat=...",
                    // more fields
                  }
                }
        """
        children = record.get("children")
        children_fetched = []
        fields = "id,ig_id,media_type,media_url,owner,permalink,shortcode,thumbnail_url,timestamp,username"
        if children:
            children_ids = [child.get("id") for child in children.get("data")]
            for children_id in children_ids:
                media_data = get_http_response(children_id, {"fields": fields}, config=config)
                media_data = InstagramClearUrlTransformation().transform(media_data)
                if media_data.get("timestamp"):
                    dt = datetime.strptime(media_data["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
                    formatted_str = dt.strftime("%Y-%m-%dT%H:%M:%S%z")
                    formatted_str_with_colon = formatted_str[:-2] + ":" + formatted_str[-2:]
                    media_data["timestamp"] = formatted_str_with_colon
                children_fetched.append(media_data)

            record["children"] = children_fetched
        return record


@dataclass
class InstagramBreakDownResultsTransformation(RecordTransformation):
    """
    The transformation flattens a nested array of breakdown results located at total_value.breakdowns[0].results into a single object
    (dictionary). In this transformation, each key-value pair in the resulting object represents a dimension and its corresponding value.

    Example input:
        {
        "total_value": {
          "breakdowns": [
            {
              "dimension_keys": [
                "city"
              ],
              "results": [
                {
                  "dimension_values": [
                    "London, England"
                  ],
                  "value": 263
                },
                {
                  "dimension_values": [
                    "Sydney, New South Wales"
                  ],
                  "value": 467
                }
              ]
            }
          ]
        },
        "id": "id/insights/follower_demographics/lifetime"
      }

    Example output:
        {
        "value": {
          "London, England": 263,
          "Sydney, New South Wales": 467,
        }
    The nested 'results' array is transformed into a 'value' dictionary where each key is a dimension and each value is the corresponding value.
    """

    def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record_total_value = record.pop("total_value")
        record["value"] = {res.get("dimension_values", [""])[0]: res.get("value") for res in record_total_value["breakdowns"][0]["results"]}
        return record
