#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator

def _auth_from_config(config):
    try:
        if config["api_key"]:
            return BasicHttpAuthenticator(username=config["api_key"], password=None, auth_method="Basic")
        else:
            print("Auth type was not configured properly")
            return None
    except Exception as e:
        print(f"{e.__class__} occurred, there's an issue with credentials in your config")
        raise e
    

class SourceLever(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            authenticator = _auth_from_config(config)
            _ = authenticator.get_auth_header()
        except Exception as e:
            return False, str(e)
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = _auth_from_config(config)
        # TODO: use extract_start_date
        return [
            Opportunities(authenticator=authenticator),
            Offers(authenticator=authenticator),
            Feedback(authenticator=authenticator),
            Interviews(authenticator=authenticator),
            Applications(authenticator=authenticator),
            Requisitions(authenticator=authenticator),
            Users(authenticator=authenticator),
            Stages(authenticator=authenticator),
            Postings(authenticator=authenticator),
            ArchiveReasons(authenticator=authenticator),
            Panels(authenticator=authenticator),
            Tags(authenticator=authenticator),
            Sources(authenticator=authenticator),
            RequisitionFields(authenticator=authenticator),
            Notes(authenticator=authenticator)
        ]

# Basic full refresh stream
class LeverStream(HttpStream, ABC):
    page_size = 100
    stream_params = {}
    
    API_VERSION = "v1"
    base_url = "https://api.lever.co"

    @property
    def url_base(self) -> str:
        return f"{self.base_url}/{self.API_VERSION}/"
    

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_data = response.json()
        if response_data.get("hasNext"):
            return {"offset": response_data["next"]}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.page_size}
        params.update(self.stream_params)
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, stream_slice:Mapping[str, Any],  **kwargs) -> Iterable[Mapping]:
        yield from response.json()["data"]

class Opportunities(LeverStream):
    primary_key = "id"
    stream_params = {"confidentiality": "all", "expand": "contact"}
    # 1797 opportunities
    # 1 record read
    # stream_params = {"confidentiality": "all", "expand": "contact", "stage_id": "e54475bb-d3ad-43ff-b8b9-76c4fc38e78c" }

    # 8311 opportunities
    # stream_params = {"confidentiality": "all", "expand": "contact", "stage_id": "3a255cc8-0732-4bee-92bd-62acfec3572c" }
    

    @property
    def use_cache(self) -> bool:
        return True

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "opportunities"

class Requisitions(LeverStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "requisitions"  

class Users(LeverStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "users"

class Stages(LeverStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "stages"
    
class Postings(LeverStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "postings"

class Tags(LeverStream):
    primary_key = "text"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "tags"

class Sources(LeverStream):
    primary_key = "text"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "sources"
    
class RequisitionFields(LeverStream):
    primary_key = "text"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "requisition_fields"


class ArchiveReasons(LeverStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "archive_reasons"


# TODO: Basic incremental stream
class IncrementalLeverStream(LeverStream, ABC):
    """
    TODO fill in details of this class to implement functionality related to incremental syncs for your connector.
         if you do not need to implement incremental sync for any streams, remove this class.
    """

    # TODO: Fill in to checkpoint stream reads after N records. This prevents re-reading of data if the stream fails for any reason.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        TODO
        Override to return the cursor field used by this stream e.g: an API entity might always use created_at as the cursor field. This is
        usually id or date based. This field's presence tells the framework this in an incremental stream. Required for incremental.

        :return str: The name of the cursor field.
        """
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        return {}


# Basic Sub streams using Opportunity id
class OpportunitySubStream(LeverStream, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    # def __init__(self, start_date: str, **kwargs):
    #     super().__init__(**kwargs)
    #     self._start_date = start_date
    
    def path(self, stream_slice: Mapping[str, any] = None, **kwargs) -> str:
        return f"opportunities/{stream_slice['opportunity_id']}/{self.name}"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for stream_slice in super().stream_slices(**kwargs):
            # opportunities_stream = Opportunities(authenticator=self.authenticator, base_url=self.base_url, start_date=self._start_date)
            opportunities_stream = Opportunities(authenticator=self.authenticator)
            for opportunity in opportunities_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
                yield {"opportunity_id": opportunity["id"]}
    

    def parse_response(self, response: requests.Response, stream_slice:[Mapping[str, Any]], **kwargs) -> Iterable[Mapping]:
        records = response.json()["data"]
        if not records:
            records = [{}]
        
        for record in records:
            record["opportunity"] = stream_slice["opportunity_id"]
        yield from records
        

class Offers(OpportunitySubStream):
    """
    Offers stream: https://hire.lever.co/developer/documentation#list-all-offers
    """
    primary_key = "id"

class Feedback(OpportunitySubStream):
    """
    Feedback stream: https://hire.lever.co/developer/documentation#list-all-feedback
    """
    primary_key = "id"

class Interviews(OpportunitySubStream):
    """
    Interviews stream: https://hire.lever.co/developer/documentation#list-all-interviews
    """
    primary_key = "id"

class Applications(OpportunitySubStream):
    """
    Applications stream: https://hire.lever.co/developer/documentation#list-all-applications
    """
    primary_key = "id"

class Panels(OpportunitySubStream):
    """
    Panels stream: https://hire.lever.co/developer/documentation#list-all-panels
    """
    primary_key = "id"

class Notes(OpportunitySubStream):
    """
    Notes stream: https://hire.lever.co/developer/documentation#list-all-notes
    """
    primary_key = "id"
