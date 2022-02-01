#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

ORB_API_BASE_URL = "https://api.billwithorb.com/v1/"


class OrbStream(HttpStream, ABC):
    """
    Implementation of a full-refresh stream. Note that this still has pagination so that
    a given run of the Stream can fetch data in a paginated manner. However, it does not have
    stream 'state', so all data is read in every run.
    """

    primary_key = "id"
    page_size = 50
    url_base = ORB_API_BASE_URL

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Constructs the parameter in order to fetch the next page of results from the current response.
        Note that we should not make any assumptions about the semantic meaning of `next_cursor` as per
        Orb's API docs.
        """
        decoded_response = response.json()
        if bool(decoded_response.get("pagination_metadata", {}).get("has_more", False)):
            return {"cursor": decoded_response["pagination_metadata"]["next_cursor"]}
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            "limit": self.page_size,
        }

        # Add the cursor if required.
        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Records are in a container array called data
        response_json = response.json()
        yield from response_json.get("data", [])


class IncrementalOrbStream(OrbStream, ABC):
    """
    An incremental stream is able to internally keep track of state such that each run of the connector
    will only query for new records, and output new records.

    Orb incremental streams are implemented with `created_at` as the field that determines record ordering,
    and we use API filtering to only fetch new records.
    """

    # We should not checkpoint the state after reading any finite number of records, because Orb returns
    # records in *descending* order of creation time; we can only be certain that we read records after
    # a particular creation_time after pagination is exhausted. Note that this doesn't mean we will read
    # *all* records period, because the request can still have a `created_at[gte]` parameter as a filter.
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        """
        Incremental streams should use the `created_at` field to update their state. This
        can be different than what's actually present in the pagination *response* of a given
        request, as long as more recent records have a lower `created_at`.
        """
        return "created_at"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        In order to update the state of the stream, take the max of the current `created_at` time and what might already be in the state.
        """
        latest_record_state_dt = pendulum.parse(latest_record.get(self.cursor_field))
        current_state_isoformat = current_stream_state.get(self.cursor_field)
        current_state_dt = pendulum.parse(current_state_isoformat) if current_state_isoformat is not None else pendulum.DateTime.min
        updated_state = max(latest_record_state_dt, current_state_dt)
        return {self.cursor_field: updated_state.isoformat()}

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        """
        These request params take care of both state and pagination.
        Previous stream state is accounted for by using the `created_at[gte]`, so we
        only fetch new records since the last run.

        We use GTE because of inclusive cursors
        (https://docs.airbyte.com/understanding-airbyte/connections/incremental-append#inclusive-cursors)

        Pagination is taken care of by `request_params` in `OrbStream`, hence the call to
        super().
        """
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)

        # State stores the timestamp is ISO format
        start_timestamp = stream_state.get(self.cursor_field)
        if start_timestamp:
            params["created_at[gte]"] = start_timestamp
        return params


class Customers(IncrementalOrbStream):
    """
    API Docs: https://docs.withorb.com/reference/list-customers
    """

    def path(self, **kwargs) -> str:
        return "customers"


class Subscriptions(IncrementalOrbStream):
    """
    API Docs: https://docs.withorb.com/reference/list-subscriptions
    """

    def path(self, **kwargs) -> str:
        return "subscriptions"


class Plans(IncrementalOrbStream):
    """
    API Docs: https://docs.withorb.com/reference/list-plans
    """

    def path(self, **kwargs) -> str:
        return "plans"


class CreditsLedgerEntries(IncrementalOrbStream):
    page_size = 500
    """
    API Docs: https://docs.withorb.com/reference/view-credits-ledger
    """

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        The state for this stream is *per customer* (i.e. slice), and is a map from
        customer_id -> "created_at" -> isoformat created_at date boundary

        In order to update state, figure out the slice corresponding to the latest_record,
        and take a max between the record `created_at` and what's already in the state.
        """
        latest_record_created_at_dt = pendulum.parse(latest_record.get(self.cursor_field))
        current_customer_id = latest_record["customer"]["id"]

        current_customer_state = current_stream_state.get(current_customer_id, {})
        current_customer_existing_created_at = current_customer_state.get(self.cursor_field)

        # Default existing state to DateTime.min. This means the latest record will always
        # exceed the existing state.
        current_customer_existing_created_at_dt = pendulum.DateTime.min
        if current_customer_existing_created_at is not None:
            current_customer_existing_created_at_dt = pendulum.parse(current_customer_existing_created_at)

        current_customer_updated_state = {
            self.cursor_field: max(latest_record_created_at_dt, current_customer_existing_created_at_dt).isoformat()
        }

        return {
            # We need to keep the other slices as is, and only override the dictionary entry
            # corresponding to the current slice customer id.
            **current_stream_state,
            current_customer_id: current_customer_updated_state,
        }

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, **kwargs) -> MutableMapping[str, Any]:
        """
        Request params are based on the specific slice (i.e. customer_id) we are requesting for,
        and so we need to pull out relevant slice state from the stream state.

        Note that the user of super() here implies that the state for a specific slice of this stream
        is of the same format as the stream_state of a regular incremental stream.
        """
        current_customer_state = stream_state.get(stream_slice["customer_id"], {})
        return super().request_params(current_customer_state, **kwargs)

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        """
        Orb does not support querying for all ledger entries in an unscoped way, so the path
        here is dependent on the stream_slice, which determines the `customer_id`.
        """
        customer_id = stream_slice["customer_id"]
        return f"customers/{customer_id}/credits/ledger"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        This stream is sliced per `customer_id`. This has two implications:
        (1) State can be checkpointed after processing each slice
        (2) The other parameters (e.g. request_params, path) can be dependent on this slice.

        This allows us to pull data on a per customer_id basis, since that's what Orb exposes.
        """
        # TODO: self.authenticator should optionally pull from self._session.auth
        customers_stream = Customers(authenticator=self._session.auth)
        for customer in customers_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"customer_id": customer["id"]}


# Source
class SourceOrb(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        Makes a request to the /ping endpoint, which validates that the authentication credentials are appropriate.
        API Docs: https://docs.withorb.com/reference/ping
        """
        auth_header = TokenAuthenticator(token=config["api_key"]).get_auth_header()
        ping_url = ORB_API_BASE_URL + "ping"
        ping_response = requests.get(ping_url, headers=auth_header)
        try:
            ping_response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(token=config["api_key"])
        return [
            Customers(authenticator=authenticator),
            Subscriptions(authenticator=authenticator),
            Plans(authenticator=authenticator),
            CreditsLedgerEntries(authenticator=authenticator),
        ]
