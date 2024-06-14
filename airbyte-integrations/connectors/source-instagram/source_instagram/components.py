import requests

from dataclasses import dataclass
from typing import Any, MutableMapping, Optional, Dict

from airbyte_cdk.connector_builder.connector_builder_handler import resolve_manifest
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config

from .common import remove_params_from_url
from source_instagram import SourceInstagram

GRAPH_URL = resolve_manifest(source=SourceInstagram()).record.data["manifest"]["definitions"]["base_requester"]["url_base"]


def get_http_response(path: str, request_params: Dict, config: Config) -> Optional[MutableMapping[str, Any]]:
    url = f'{GRAPH_URL}/{path}'
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
        This function removes the _nc_rid parameter from the video url and ccb from profile_picture_url for users.
        _nc_rid is generated every time a new one and ccb can change its value, and tests fail when checking for identity.
        This does not spoil the link, it remains correct and by clicking on it you can view the video or see picture.
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
        Fetch children data if such field is present, it will update each element on the response
        """
        children = record.get('children')
        children_fetched = []
        fields = 'id,ig_id,media_type,media_url,owner,permalink,shortcode,thumbnail_url,timestamp,username'
        if children:
            children_ids = [child.get("id") for child in children.get("data")]
            for children_id in children_ids:
                    media_data = get_http_response(children_id, {"fields": fields}, config=config)
                    media_data = InstagramClearUrlTransformation().transform(media_data)
                    children_fetched.append(media_data)

            record["children"] = children_fetched
        return record


@dataclass
class InstagramBreakDownResultsTransformation(RecordTransformation):
    """
    Converts an array of breakdowns into an object.
    """
    def transform(self, record: MutableMapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        record["value"] = {res.get("dimension_values")[0]: res.get("value") for res in record["value"]}
        return record
