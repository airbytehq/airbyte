#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, TYPE_CHECKING

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from . import fields



# Basic full refresh stream
class GetintentStream(HttpStream, ABC):
    url_base = "https://ui.getintent.com/api/v2/"

    def __init__(self, access_token: str):
        super().__init__(authenticator=None)
        self.access_token = access_token

    def next_page_token(
        self,
        response: requests.Response,
    ) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {"token": self.access_token}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        print(response.request.url)
        yield from response.json()["data"].values()


class ObjectStream(GetintentStream, ABC):
    primary_key = "id"

    @property
    @abstractmethod
    def fields(self) -> list[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def object_name(self) -> str:
        raise NotImplementedError

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return f"{self.object_name}/list"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        custom_fields = {}
        if self.fields:
            custom_fields["custom_fields"] = ",".join(self.fields)
        return {
            **super().request_params(
                stream_state,
                stream_slice,
                next_page_token,
            ),
            **custom_fields,
        }


class Campaigns(ObjectStream):
    fields = fields.campaigns_fields
    object_name = "campaigns"


class CampaignGroups(ObjectStream):
    fields = fields.campaign_groups_fields
    object_name = "campaign_groups"


class Creatives(ObjectStream):
    fields = fields.creatives_fields
    object_name = "creatives"


class Sites(ObjectStream):
    fields = fields.sites_fields
    object_name = "sites"


class Segments(ObjectStream):
    fields = fields.segments_fields
    object_name = "segments"


class Snippets(ObjectStream):
    fields = fields.snippets_fields
    object_name = "snippets"


class ReportStream(GetintentStream):
    primary_key = "day"

    @property
    def name(self) -> str:
        return self.internal_name

    def __init__(
        self,
        access_token: str,
        internal_name: str,
        date_from: datetime,
        date_to: datetime,
        dataset_name: str,
        group_keys: list[str] = [],
        specific_values: list[str] = [],
        filters: list[str] = [],
        having: list[str] = [],
    ):
        super().__init__(access_token)
        self.date_from = date_from
        self.date_to = date_to
        self.dataset_name = dataset_name
        self.group_keys = group_keys
        self.specific_values = specific_values
        self.filters = filters
        self.having = having
        self.internal_name = internal_name

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "reports"

    @staticmethod
    def datetime_to_str(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%d")

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        optional_params = {
            "keys": ",".join(getattr(self, "group_keys", [])),
            "values": ",".join(getattr(self, "specific_values", [])),
            "filter[]": getattr(self, "filters", []),
            "having[]": getattr(self, "having", []),
        }
        params = {
            **super().request_params(
                stream_state,
                stream_slice,
                next_page_token,
            ),
            "dataset_name": self.dataset_name,
            "start": self.datetime_to_str(self.date_from),
            "end": self.datetime_to_str(self.date_to),
            "format": "json",
            "relations": 1,
        }
        for param_name in optional_params.keys():
            value = optional_params[param_name]
            if value:
                params[param_name] = value
        return params


# Source
class SourceGetintent(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        access_token = config["access_token"]
        shared_kwargs = dict(access_token=access_token)

        streams: List[Stream] = [
            Campaigns(**shared_kwargs),
            CampaignGroups(**shared_kwargs),
            Creatives(**shared_kwargs),
            Sites(**shared_kwargs),
            Segments(**shared_kwargs),
            Snippets(**shared_kwargs),
        ]

        for report_config in config.get("reports", []):
            streams.append(
                ReportStream(
                    **shared_kwargs,
                    date_from=config["date_from"],
                    date_to=config["date_to"],
                    internal_name=report_config["name"],
                    dataset_name=report_config["dataset_name"],
                    group_keys=report_config.get("group_keys", []),
                    specific_values=report_config.get("specific_values", []),
                    filters=report_config.get("filters", []),
                    having=report_config.get("having", []),
                )
            )

        return streams
