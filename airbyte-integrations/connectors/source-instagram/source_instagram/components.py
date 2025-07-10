# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import logging
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Union

import dpath
import requests

from airbyte_cdk.sources.declarative.decoders import Decoder, JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers import SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.requesters.error_handlers.backoff_strategies.exponential_backoff_strategy import (
    ExponentialBackoffStrategy,
)
from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpClient, HttpMethod
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.sources.types import StreamSlice
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.utils.datetime_helpers import ab_datetime_format, ab_datetime_parse

from .common import remove_params_from_url


GRAPH_URL = "https://graph.facebook.com/v21.0"


def get_http_response(name: str, path: str, request_params: Dict, config: Config) -> Optional[MutableMapping[str, Any]]:
    http_logger = logging.getLogger(f"airbyte.HttpClient.{name}")
    try:
        url = f"{GRAPH_URL}/{path}"
        token = config["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        params = {
            **request_params,
        }
        factor = 5
        backoff_parameters = backoff_config = {"backoff": factor}
        backoff_strategy = ExponentialBackoffStrategy(factor=factor, parameters=backoff_parameters, config=backoff_config)
        error_handler = DefaultErrorHandler(config={}, parameters={}, backoff_strategies=[backoff_strategy])
        http_client = HttpClient(
            name=name,
            logger=http_logger,
            use_cache=False,
            error_handler=error_handler,
        )
        _, response = http_client.send_request(
            http_method=HttpMethod.GET.name,
            url=url,
            request_kwargs={},
            headers=headers,
            params=params,
        )
        response.raise_for_status()
    except requests.HTTPError as http_err:
        error = f"HTTP error occurred: {http_err.response.status_code} - {http_err.response.text}"
        http_logger.error(f"Error getting children data: {error}")
        raise Exception(error)
    except Exception as err:
        error = f"An error occurred: {err}"
        http_logger.error(f"Error getting children data: {error}")
        raise Exception(error)
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
                media_data = get_http_response(f"MediaInsights.{children_id}", children_id, {"fields": fields}, config=config)
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
class InstagramInsightsTransformation(RecordTransformation):
    def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        """
        The transformation flattens the array of insights into a single object (dictionary). In such object, each key-value pair
        in the resulting object represents a metric and and its corresponding value.

        Example Input:
        {
            "data": [
              {
                "name": "comments",
                "period": "lifetime",
                "values": [
                  {
                    "value": 7
                  }
                ],
                "title": "title1",
                "description": "Description1.",
                "id": "insta_id/insights/comments/lifetime"
              },
              {
                "name": "ig_reels_avg_watch_time",
                "period": "lifetime",
                "values": [
                  {
                    "value": 11900
                  }
                ],
                "title": "2",
                "description": "Description2.",
                "id": "insta_id/insights/ig_reels_avg_watch_time/lifetime"
              }
        }

        Example Output:
        {
            "comments": 7,
            "ig_reels_avg_watch_time": 11900
        }
        """
        if record.get("data"):
            insights_data = record.pop("data")
            for insight in insights_data:
                record[insight["name"]] = insight.get("values")[0]["value"]
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


@dataclass
class UserInsightsExtractor(RecordExtractor):
    """
    Custom extractor that is needed for the Instagram user_insights stream because the existing transformations
    functionality for AddedFieldDefinition does not support interpolation on the target path to inject a value
    into.

    The user_insights stream path is dependent on which slice query property chunk we are currently syncing
    because it is used in the key. For example, chunk for `week` period and the `reach` metric should
    be rendered as `reach_week`, but this can only be done with interpolation which currently isn't supported.
    """

    field_path: List[Union[InterpolatedString, str]]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = field(default_factory=lambda: JsonDecoder(parameters={}))

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._field_path = [InterpolatedString.create(path, parameters=parameters) for path in self.field_path]
        for path_index in range(len(self.field_path)):
            if isinstance(self.field_path[path_index], str):
                self._field_path[path_index] = InterpolatedString.create(self.field_path[path_index], parameters=parameters)

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        for body in self.decoder.decode(response):
            results = []
            if len(self._field_path) == 0:
                extracted = body
            else:
                path = [path.eval(self.config) for path in self._field_path]
                if "*" in path:
                    extracted = dpath.values(body, path)
                else:
                    extracted = dpath.get(body, path, default=[])  # type: ignore # extracted will be a MutableMapping, given input data structure
            if isinstance(extracted, list):
                results = extracted
            elif extracted:
                raise ValueError(f"field_path should always point towards a list field in the response body for property_history streams")

            complete_record = dict()
            for result in results:
                period = result.get("period")
                metric_key = result.get("name")
                if period in ["week", "days_28"]:
                    metric_key += f"_{period}"
                metric_value = result.get("values")[0].get("value")
                complete_record[metric_key] = metric_value
                if "date" not in complete_record:
                    complete_record["date"] = result.get("values")[0].get("end_time")
            yield complete_record


@dataclass
class UserInsightsSubstreamPartitionRouter(SubstreamPartitionRouter):
    """
    The way the Python user_insights stream was a substream of the Api/Accounts parent stream, but it only incorporated
    the business_account_id as the partition field. However, the actual parent stream slice is an account object made
    up of a business_account_id and a page_id. This creates issues when trying to extract the state of the current
    partition because the incoming state of an existing connection will not contain the page_id.

    This custom component retains the existing behavior of the Python implementation by only saving the business_account_id
    to the per-partition state while adding the page_id to the extra_fields so it can be used while readiing records
    for a given partition.
    """

    def stream_slices(self) -> Iterable[StreamSlice]:
        for stream_slice in super().stream_slices():
            account_object = stream_slice.partition.get("business_account_id")
            stream_slice = StreamSlice(
                partition={"business_account_id": account_object.get("business_account_id")},
                cursor_slice=stream_slice.cursor_slice,
                extra_fields={"page_id": account_object.get("page_id")},
            )
            yield stream_slice


class RFC3339DatetimeSchemaNormalization(TypeTransformer):
    """
    The Instagram API returns dates in the format 2025-01-01T07:00:00+0000, but the existing implementation
    normalized dates to the RFC 3339 format 2025-01-01T07:00:00+00:00.
    """

    def __init__(self, *args, **kwargs):
        config = TransformConfig.CustomSchemaNormalization
        super().__init__(config)
        self.registerCustomTransform(self.get_transform_function())

    def get_transform_function(self):
        def transform_function(original_value: str, field_schema: Dict[str, Any]) -> Any:
            target_format = field_schema.get("format")
            target_airbyte_type = field_schema.get("airbyte_type")

            if original_value and target_format == "date-time" and target_airbyte_type == "timestamp_with_timezone":
                ab_datetime = ab_datetime_parse(original_value)
                return ab_datetime_format(ab_datetime)
            return original_value

        return transform_function
