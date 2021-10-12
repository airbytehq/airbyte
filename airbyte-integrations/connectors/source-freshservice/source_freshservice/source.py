#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import base64
from abc import ABC
from typing import Any, Iterable, List, Dict, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


# Basic full refresh stream
class FreshserviceStream(HttpStream, ABC):
    url_base = "https://{}/api/v2/"
    primary_key = "id"
    order_field = "updated_at"
    results_per_page = 1 #TODO: update this

    def __init__(self, config: Dict):
        super().__init__(authenticator=config['authenticator'])
        self.config = config
        self.url_base = self.url_base.format(config['domain_name'])

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.links.get("next", None)
        if next_page:
            return dict(parse_qsl(urlparse(next_page.get("url")).query))
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            "per_page": self.results_per_page
        }
        if next_page_token:
            params.update(**next_page_token)
        else:
            params["order_by"] = self.order_field
            params["order_type"] = "asc"
            params["updated_since"] = self.config["start_date"]
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        records = json_response.get(self.object_name, []) if self.object_name is not None else json_response
        yield from records

# Basic incremental stream
class IncrementalFreshserviceStream(FreshserviceStream, ABC):
    state_checkpoint_interval = 60

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}

    def request_params(self, stream_state: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_state=stream_state, next_page_token=next_page_token, **kwargs)
        # If there is a next page token then we should only send pagination-related parameters.
        if not next_page_token:
            params["order_by"] = self.order_field
            params["order_type"] = "asc"
            if stream_state:
                params["updated_since"] = stream_state.get(self.cursor_field)
        return params

    # Parse the stream_slice with respect to stream_state for Incremental refresh
    # cases where we slice the stream, the endpoints for those classes don't accept any other filtering,
    # but they provide us with the updated_at field in most cases, so we used that as incremental filtering during the order slicing.
    def filter_records_newer_than_state(self, stream_state: Mapping[str, Any] = None, records_slice: Mapping[str, Any] = None) -> Iterable:
        # Getting records >= state
        if stream_state:
            for record in records_slice:
                if record.get(self.cursor_field) >= stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records_slice


class Tickets(IncrementalFreshserviceStream):
    object_name = 'tickets'
    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "tickets"

class Employees(IncrementalFreshserviceStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the cursor_field. Required.
    cursor_field = "start_date"

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.
    primary_key = "employee_id"

    def path(self, **kwargs) -> str:
        """
        TODO: Override this method to define the path this stream corresponds to. E.g. if the url is https://example-api.com/v1/employees then this should
        return "single". Required.
        """
        return "employees"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
        TODO: Optionally override this method to define this stream's slices. If slicing is not needed, delete this method.

        Slices control when state is saved. Specifically, state is saved after a slice has been fully read.
        This is useful if the API offers reads by groups or filters, and can be paired with the state object to make reads efficient. See the "concepts"
        section of the docs for more information.

        The function is called before reading any records in a stream. It returns an Iterable of dicts, each containing the
        necessary data to craft a request for a slice. The stream state is usually referenced to determine what slices need to be created.
        This means that data in a slice is usually closely related to a stream's cursor_field and stream_state.

        An HTTP request is made for each returned slice. The same slice can be accessed in the path, request_params and request_header functions to help
        craft that specific request.

        For example, if https://example-api.com/v1/employees offers a date query params that returns data for that particular day, one way to implement
        this would be to consult the stream state object for the last synced date, then return a slice containing each date from the last synced date
        till now. The request_params function would then grab the date from the stream_slice and make it part of the request by injecting it into
        the date query param.
        """
        raise NotImplementedError("Implement stream slices or delete this method!")



# Source
class HttpBasicAuthenticator(TokenAuthenticator):
    def __init__(self, auth: Tuple[str, str], auth_method: str = "Basic", **kwargs):
        auth_string = f"{auth[0]}:{auth[1]}".encode("utf8")
        b64_encoded = base64.b64encode(auth_string).decode("utf8")
        super().__init__(token=b64_encoded, auth_method=auth_method, **kwargs)

class SourceFreshservice(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        auth = HttpBasicAuthenticator((config["api_key"], "")).get_auth_header()
        url = f'https://{config["domain_name"]}/api/v2/tickets'
        try:
            session = requests.get(url, headers=auth)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config['authenticator'] = HttpBasicAuthenticator((config["api_key"], ""))
        return [Tickets(config)]
