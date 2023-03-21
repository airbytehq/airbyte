#
# Copyright (c) 2023 Onyxia, Inc., all rights reserved.
#
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
import logging
import requests
import json
from urllib import parse
from datetime import datetime
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import IncrementalMixin, Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.models import SyncMode
from source_crowdstrike_falcon.utils import initialize_authenticator
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Level,
    Status,
    SyncMode,
)
from pydantic import BaseModel

logger = logging.getLogger("airbyte")

class HostModel(BaseModel):
    last_seen: str
    os_version: str
class IncidentModel(BaseModel):
    incident_id: str
    host_ids: List[str]
    hosts: List[HostModel]
    created: str
    start: str
    end: str
    status: str
    tactics: List[str]
    techniques: List[str]
    modified_timestamp: str
    fine_score: int

class DeviceModel(BaseModel):
    device_id: str
    first_seen: str
    last_seen: str
    major_version: str
    os_version: str
    product_type_desc: str

class behaviorModel(BaseModel):
    tactic: str
    technique: str

class DetectModel(BaseModel):
    created_timestamp: str
    detection_id: str
    device: DeviceModel
    behaviors: List[behaviorModel]
    first_behavior: str
    last_behavior: str
    max_severity_displayname: str
    status: str
    seconds_to_triaged: int
    seconds_to_resolved: int



class CrowdstrikeFalcon(HttpStream, ABC):
    limit = 10

    def __init__(self, url_base: str,*args, **kwargs):
        super().__init__(*args, **kwargs)

    def path(self, **kwargs) -> str:
        return self.resource_path

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        meta = data.get('meta')
        
        if meta:
            pagination = meta.get('pagination')
        
        offset = int(pagination.get('offset'))
        limit = int(pagination.get('limit'))
        total = int(pagination.get('total'))
        
        offset += limit
        
        if offset < total:
            return { "offset": offset, "limit": limit}

        return None
        

    def request_params(self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        curr_date = stream_state.get(self.cursor_field)
        params = {
            "limit": self.limit,
            "sort": self.order_field,
            "offset": 0
        }

        if next_page_token:
            params.update(next_page_token)
        
        return params

    def parse_response(self, response: requests.Response,stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        data = response.json()

        ids = data.get('resources')

        yield {
            "ids": ids
        }

class IncrementalCrowdstrikeFalcon(CrowdstrikeFalcon, IncrementalMixin):
    cursor_init_value = "1900-01-01T00:00:00.000Z"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cursor_value = self.cursor_init_value
        self._is_finished = False

    @property
    def state(self) -> MutableMapping[str, Any]:
        return { self.cursor_field: self._cursor_value }

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._cursor_value = value.get(self.cursor_field)

    def request_params(
        self, stream_state: Mapping[str, Any], next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        curr_date = stream_state.get(self.cursor_field)
        params = super().request_params(stream_state=self.state, next_page_token=next_page_token, **kwargs)
        curr_date = self.state.get(self.cursor_field)
        filter_param = {"filter": self.filter_field + ":>'" + curr_date + "'"}
        params.update(filter_param)
        return params

class IncidentsIds(IncrementalCrowdstrikeFalcon):
    url_base = "https://api.us-2.crowdstrike.com"
    primary_key = "modified_timestamp"
    order_field = "modified_timestamp.desc"
    filter_field = "modified_timestamp"
    cursor_field = 'last_synced_at'
    resource_path = "/incidents/queries/incidents/v1"

class Incidents(HttpSubStream):
    url_base = "https://api.us-2.crowdstrike.com"

    primary_key = "incident_id"

    @property
    def use_cache(self):
        return True

    @property
    def http_method(self) -> str:
        return "POST"

    def request_body_json(self,
                        stream_state: Mapping[str, Any],
                        stream_slice: Mapping[str, Any] = None,
                        next_page_token: Mapping[str, Any] = None) -> Optional[Mapping]:

        return {
            "ids": stream_slice.get('parent').get('ids')
        }

    def path(self, **kwargs) -> str:
        return "incidents/entities/incidents/GET/v1"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        resources = data.get('resources')

        return [IncidentModel(**r).dict() for r in resources]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

class DetectsIds(IncrementalCrowdstrikeFalcon):
    url_base = "https://api.us-2.crowdstrike.com"
    primary_key = "date_updated"
    order_field = "date_updated.desc"
    filter_field = "date_updated"
    cursor_field = 'last_synced_at'
    resource_path = "/detects/queries/detects/v1"

class Detects(HttpSubStream):
    url_base = "https://api.us-2.crowdstrike.com"

    primary_key = "detects_id"

    @property
    def use_cache(self):
        return True

    @property
    def http_method(self) -> str:
        return "POST"

    def request_body_json(self,
                        stream_state: Mapping[str, Any],
                        stream_slice: Mapping[str, Any] = None,
                        next_page_token: Mapping[str, Any] = None) -> Optional[Mapping]:
        ids = stream_slice.get('parent').get('ids')

        return {
            "ids": stream_slice.get('parent').get('ids')
        }

    def path(self, **kwargs) -> str:
        return "detects/entities/summaries/GET/v1"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        resources = data.get('resources')

        return [DetectModel(**r).dict() for r in resources]
    
    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

# Source
class SourceCrowdstrikeFalcon(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        url = parse.urljoin(config["base_url"], "/oauth2/token")
        payload = {"client_id": config["client_id"], "client_secret": config["client_secret"]}
        response = requests.post(url=url, data=payload)

        if response.status_code == 201:
            return True, None

        return (
                False,
                "The Crowdstrike Falcon account is not valid. Please make sure the credentials are valid.",
            )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = initialize_authenticator(config)
        initialization_params = {"authenticator": auth, "url_base": config.get("base_url")}
        incidentsIds = IncidentsIds(**initialization_params)
        detectsIds = DetectsIds(**initialization_params)
        return [
            Incidents(parent=incidentsIds, authenticator=auth),
            incidentsIds,
            Detects(parent=detectsIds, authenticator=auth),
            detectsIds,
        ]

    def _checkpoint_state(self, stream: Stream, stream_state, state_manager: ConnectorStateManager):
        # First attempt to retrieve the current state using the stream's state property. We receive an AttributeError if the state
        # property is not implemented by the stream instance and as a fallback, use the stream_state retrieved from the stream
        # instance's deprecated get_updated_state() method.
        try:
            now = {"last_synced_at": datetime.now().isoformat()}
            state_manager.update_state_for_stream(stream.name, stream.namespace, now)

        except AttributeError:
            state_manager.update_state_for_stream(stream.name, stream.namespace, stream_state)
        return state_manager.create_state_message(stream.name, stream.namespace, send_per_stream_state=self.per_stream_state_enabled)
