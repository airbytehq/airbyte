#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, Mapping, Optional, MutableMapping, List, Union

import logging

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_protocol.models import SyncMode

API_ROOT_V2 = "https://api.ironsrc.com/advertisers/v2/"
API_ROOT_V4 = "https://api.ironsrc.com/advertisers/v4/"

logger = logging.getLogger()


class IronsourceStream(HttpStream, ABC):
    url_base = API_ROOT_V4
    use_cache = True  # it is used in all streams
    send_fields = True
    page_number = 1
    paginate = True

    def __init__(self, page_size: int, **kwargs: Any):
        super().__init__(**kwargs)
        self.page_size = page_size

    @property
    def entity(self) -> Union[None, str]:
        return None

    @property
    def fields(self):
        return ",".join(self.get_json_schema().get("properties", {})),

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        if response.status_code in [401]:
            return 1.0
        return None

    def should_retry(self, response: requests.Response) -> bool:
        return self._check_token_expiration(response) or response.status_code == 429 or 500 <= response.status_code < 600

    def request_params(self, stream_state: Optional[Mapping[str, Any]],
                       stream_slice: Optional[Mapping[str, Any]] = None,
                       next_page_token: Optional[Mapping[str, Any]] = None) -> MutableMapping[str, Any]:
        params = {}
        if self.send_fields:
            params["fields"] = self.fields
        if self.paginate:
            params["resultsBulkSize"] = self.page_size
            if next_page_token:
                params.update(next_page_token)
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if not response:
            # We reset page number for caching (stream might be unrolled several times)
            self.page_number = 1
            return None
        if self.entity not in response.json():
            self.page_number = 1
            return None
        if not response.json()[self.entity]:
            self.page_number = 1
            return None
        if "requestId" not in response.json():
            self.page_number = 1
            return None
        self.page_number += 1
        return {
            "requestId": response.json()["requestId"],
            "pageNumber": self.page_number
        }

    def parse_response(self, response: requests.Response, *,
                       stream_state: Optional[Mapping[str, Any]],
                       stream_slice: Optional[Mapping[str, Any]] = None,
                       next_page_token: Optional[Mapping[str, Any]] = None) -> Iterable[Mapping]:
        if response.json() is None:
            return []
        if self.entity not in response.json():
            return []
        yield from response.json()[self.entity]

    def _check_token_expiration(self, response: requests.Response):
        # HTTP 401 errors likely mean that the bearer token is expired, so we ask for a new one and retry
        if response.status_code in [401]:
            self._session.auth.renew()
            return True
        return False

    def _send(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        # We need to force update the Authorization header as it might have changed since the request was generated (HTTP 401)
        request.headers.update(self._session.auth.get_auth_header())
        return super()._send(request, request_kwargs)


class IronsourceSubStream(IronsourceStream, ABC):
    def __init__(self, parent: HttpStream, **kwargs: Any):
        """
        :param parent: should be the instance of IronsourceStream class
        """
        super().__init__(**kwargs)
        self.parent = parent

    def stream_slices(
            self, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        # iterate over all parent stream_slices
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            # iterate over all parent records with current stream_slice
            for record in parent_records:
                yield {"parent": record}

    def add_parent_id(self, row: MutableMapping[str, Any], parent_key: str, parent_id: Any):
        row[parent_key] = parent_id
        return row

    def parse_response(self, response: requests.Response,
                       stream_state: Optional[Mapping[str, Any]],
                       stream_slice: Optional[Mapping[str, Any]] = None,
                       next_page_token: Optional[Mapping[str, Any]] = None) -> Iterable[Mapping]:
        if response.json() is None:
            return []
        if self.entity not in response.json():
            return []
        yield from (self.add_parent_id(b, "campaignId", stream_slice['parent']['id']) for b in response.json()[self.entity])


class Campaigns(IronsourceStream):
    primary_key = "id"
    entity = "campaigns"

    def path(self, **kwargs) -> str:
        return "campaigns"


class Assets(IronsourceStream):
    url_base = API_ROOT_V2
    primary_key = "id"
    entity = "assets"

    def path(self, **kwargs) -> str:
        return "assets"


class Creatives(IronsourceStream):
    send_fields = False
    primary_key = "id"
    entity = "creatives"

    def path(self, **kwargs) -> str:
        return "creatives"


class Titles(IronsourceStream):
    url_base = API_ROOT_V2
    primary_key = "id"
    entity = "titles"

    @property
    def fields(self):
        # Due to a bug in the APIs v2 field naming (input = bundle_id, output = bundleId)
        return [f.replace("bundleId", "bundle_id") for f in super().fields]

    def path(self, **kwargs) -> str:
        return "titles"


class Bids(IronsourceSubStream):
    primary_key = "bid"
    entity = "bids"
    send_fields = False

    def __init__(self, campaigns_stream: Campaigns, **kwargs: Any):
        super().__init__(campaigns_stream, **kwargs)

    def request_params(self, stream_state: Optional[Mapping[str, Any]],
                       stream_slice: Optional[Mapping[str, Any]] = None,
                       next_page_token: Optional[Mapping[str, Any]] = None) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["campaignId"] = stream_slice['parent']['id']
        return params

    def path(self, **kwargs):
        return "multiBid"


class CampaignTargetings(IronsourceSubStream):
    primary_key = "campaignId"
    entity = "data"
    send_fields = False
    paginate = False
    raise_on_http_errors = False

    def __init__(self, campaigns_stream: Campaigns, **kwargs: Any):
        super().__init__(campaigns_stream, **kwargs)

    def path(self,
             stream_state: Mapping[str, Any] = None,
             stream_slice: Mapping[str, Any] = None,
             next_page_token: Mapping[str, Any] = None) -> str:
        return f"targeting/campaign/{stream_slice['parent']['id']}"

    def parse_response(self, response: requests.Response,
                       stream_state: Optional[Mapping[str, Any]],
                       stream_slice: Optional[Mapping[str, Any]] = None,
                       next_page_token: Optional[Mapping[str, Any]] = None) -> Iterable[Mapping]:
        if response.status_code == 400 and response.json()["errorMessage"] == "Invalid field campaignId - Supports UAP campaigns only":
            return []
        if response.json() is None or self.entity not in response.json():
            return []
        response.raise_for_status()
        yield from [self.add_parent_id(response.json()[self.entity], "campaignId", stream_slice['parent']['id'])]


class CountryGroups(IronsourceSubStream):
    raise_on_http_errors = False
    primary_key = "id"
    entity = "countryGroups"
    send_fields = False

    def __init__(self, campaigns_stream: Campaigns, **kwargs: Any):
        super().__init__(campaigns_stream, **kwargs)

    def path(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"countryGroup/{stream_slice['parent']['id']}"

    def should_retry(self, response: requests.Response) -> bool:
        # We don't retry on 500 due to a bug on API side
        return self._check_token_expiration(response) or response.status_code == 429 or 501 <= response.status_code < 600

    def parse_response(self, response: requests.Response,
                       stream_state: Optional[Mapping[str, Any]],
                       stream_slice: Optional[Mapping[str, Any]] = None,
                       next_page_token: Optional[Mapping[str, Any]] = None) -> Iterable[Mapping]:
        # Some campaigns are not compatible, we ignore those
        if response.status_code == 400 and response.json()["errorMessage"] == "Invalid field campaignId - not compatible campaign":
            return []
        # FIXME: On some campaigns, retrieval is impossible
        if response.status_code in [500]:
            logger.warning(f"Skipping failing retrieval of item {response.request.path_url}")
            return []
        response.raise_for_status()
        yield from super().parse_response(response, stream_state, stream_slice, next_page_token)


class CampaignCreatives(IronsourceSubStream, ABC):
    raise_on_http_errors = False
    primary_key = "id"
    entity = "creatives"
    send_fields = False

    def __init__(self, campaigns_stream: Campaigns, **kwargs: Any):
        super().__init__(campaigns_stream, **kwargs)

    def path(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"creatives/campaignCreatives/{stream_slice['parent']['id']}"

    def parse_response(self, response: requests.Response,
                       stream_state: Optional[Mapping[str, Any]],
                       stream_slice: Optional[Mapping[str, Any]] = None,
                       next_page_token: Optional[Mapping[str, Any]] = None) -> Iterable[Mapping]:
        # non-UAP campaigns are not supported by the endpoint, so we ignore them
        if response.status_code == 400 and response.json()["errorMessage"] == "Invalid field campaignId - Supports UAP campaigns only":
            return []
        response.raise_for_status()
        yield from (self.add_parent_id(b, "campaignId", stream_slice['parent']['id']) for b in response.json()[self.entity])
