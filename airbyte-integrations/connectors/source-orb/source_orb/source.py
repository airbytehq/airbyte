#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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

    def __init__(self, start_date: Optional[pendulum.DateTime] = None, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date

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

        # Note that this doesn't take into account `stream_state` when constructing
        # this start date -- that happens in `IncrementalOrbStream`, so this may be
        # overriden by a value there.
        if self.start_date:
            params["created_at[gte]"] = self.start_date.isoformat()

        # Add the cursor if required.
        if next_page_token:
            params.update(next_page_token)

        return params

    def transform_record(self, single_record):
        """
        Used to transform the record. In this connector, we use this to
        take IDs out of nested objects, so that they are easier to work with for destinations.
        """
        return single_record

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        # Records are in a container array called data
        response_json = response.json()
        records = response_json.get("data", [])
        for record in records:
            yield self.transform_record(record)


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

    def __init__(self, lookback_window_days: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.lookback_window_days = lookback_window_days

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
        state_based_start_timestamp = stream_state.get(self.cursor_field)

        if state_based_start_timestamp and self.lookback_window_days:
            self.logger.info(f"Applying lookback window of {self.lookback_window_days} days to stream {self.name}")
            state_based_start_timestamp_dt = pendulum.parse(state_based_start_timestamp)
            # Modify state_based_start_timestamp to account for lookback
            state_based_start_timestamp = (state_based_start_timestamp_dt - pendulum.duration(days=self.lookback_window_days)).isoformat()

        if state_based_start_timestamp:
            # This may (reasonably) override the existing `created_at[gte]` set based on the start_date
            # of the stream, as configured.
            params["created_at[gte]"] = state_based_start_timestamp
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

    def transform_record(self, subscription_record):
        # Un-nest customer -> id into customer_id
        nested_customer_id = subscription_record["customer"]["id"]
        del subscription_record["customer"]
        subscription_record["customer_id"] = nested_customer_id

        # Un-nest plan -> id into plan_id
        nested_plan_id = subscription_record["plan"]["id"]
        del subscription_record["plan"]
        subscription_record["plan_id"] = nested_plan_id

        return subscription_record


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

    def __init__(
        self, string_event_properties_keys: Optional[List[str]] = None, numeric_event_properties_keys: Optional[List[str]] = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.string_event_properties_keys = string_event_properties_keys
        self.numeric_event_properties_keys = numeric_event_properties_keys

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        The state for this stream is *per customer* (i.e. slice), and is a map from
        customer_id -> "created_at" -> isoformat created_at date boundary

        In order to update state, figure out the slice corresponding to the latest_record,
        and take a max between the record `created_at` and what's already in the state.
        """
        latest_record_created_at_dt = pendulum.parse(latest_record.get(self.cursor_field))
        current_customer_id = latest_record["customer_id"]

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

        Ledger entries can either be `pending` or `committed`.
        We're filtering to only return `committed` ledger entries, which are entries that are older than the
        reporting grace period (12 hours) and are considered finalized.
        `pending` entries can change during the reporting grace period, so we don't want to export those entries.

        Note that the user of super() here implies that the state for a specific slice of this stream
        is of the same format as the stream_state of a regular incremental stream.
        """
        current_customer_state = stream_state.get(stream_slice["customer_id"], {})
        params = super().request_params(current_customer_state, **kwargs)
        params["entry_status"] = "committed"
        return params

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

    def transform_record(self, ledger_entry_record):
        # Un-nest customer -> id into customer_id
        nested_customer_id = ledger_entry_record["customer"]["id"]
        del ledger_entry_record["customer"]
        ledger_entry_record["customer_id"] = nested_customer_id

        # Un-nest credit_block -> expiry_date into block_expiry_date and id and per_unit_cost_basis
        nested_expiry_date = ledger_entry_record["credit_block"]["expiry_date"]
        nested_id = ledger_entry_record["credit_block"]["id"]
        nested_per_unit_cost_basis = ledger_entry_record["credit_block"]["per_unit_cost_basis"]
        del ledger_entry_record["credit_block"]
        ledger_entry_record["block_expiry_date"] = nested_expiry_date
        ledger_entry_record["credit_block_id"] = nested_id
        ledger_entry_record["credit_block_per_unit_cost_basis"] = nested_per_unit_cost_basis

        return ledger_entry_record

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Once we parse the response from the ledger entries stream, enrich the resulting entries
        with event metadata.
        """
        ledger_entries = list(super().parse_response(response, **kwargs))
        return self.enrich_ledger_entries_with_event_data(ledger_entries)

    def enrich_ledger_entries_with_event_data(self, ledger_entries):
        """
        Enriches a list of ledger entries with event metadata (applies only to decrements that
        have an event_id property set, i.e. automated decrements to the ledger applied by Orb).
        """
        # Build up a list of the subset of ledger entries we are expected
        # to enrich with event metadata.
        event_id_to_ledger_entries = {}
        for entry in ledger_entries:
            maybe_event_id: Optional[str] = entry.get("event_id")
            if maybe_event_id:
                # There can be multiple entries with the same event ID
                event_id_to_ledger_entries[maybe_event_id] = event_id_to_ledger_entries.get(maybe_event_id, []) + [entry]

        # Nothing to enrich; short-circuit
        if len(event_id_to_ledger_entries) == 0:
            return ledger_entries

        def modify_ledger_entry_schema(ledger_entry):
            """
            Takes a ledger entry with an `event_id` and instead turn it into
            an entry with an `event` dictionary, `event_id` nested.
            """
            event_id = ledger_entry["event_id"]
            del ledger_entry["event_id"]
            ledger_entry["event"] = {}
            ledger_entry["event"]["id"] = event_id

        for ledger_entries_in_map in event_id_to_ledger_entries.values():
            for ledger_entry in ledger_entries_in_map:
                modify_ledger_entry_schema(ledger_entry=ledger_entry)

        # Nothing to extract for each ledger entry
        merged_properties_keys = (self.string_event_properties_keys or []) + (self.numeric_event_properties_keys or [])
        if not merged_properties_keys:
            return ledger_entries

        # The events endpoint is a `POST` endpoint which expects a list of
        # event_ids to filter on
        request_filter_json = {"event_ids": list(event_id_to_ledger_entries)}

        # Prepare request with self._session, which should
        # automatically deal with the authentication header.
        args = {"method": "POST", "url": self.url_base + "events", "params": {"limit": self.page_size}, "json": request_filter_json}
        prepared_request = self._session.prepare_request(requests.Request(**args))
        events_response: requests.Response = self._session.send(prepared_request)
        # Error for invalid responses
        events_response.raise_for_status()
        paginated_events_response_body = events_response.json()

        if paginated_events_response_body["pagination_metadata"]["has_more"]:
            raise ValueError("Did not expect any pagination for events request when enriching ledger entries.")

        num_events_enriched = 0
        for serialized_event in paginated_events_response_body["data"]:
            event_id = serialized_event["id"]
            desired_properties_subset = {
                key: value for key, value in serialized_event["properties"].items() if key in merged_properties_keys
            }

            # This would imply that the endpoint returned an event that wasn't part of the filter
            # parameters, so log an error but ignore it.
            if event_id not in event_id_to_ledger_entries:
                self.logger.error(f"Unrecognized event received with ID {event_id} when trying to enrich ledger entries")
                continue

            # Replace ledger_entry.event_id with ledger_entry.event
            for ledger_entry in event_id_to_ledger_entries[event_id]:
                ledger_entry["event"]["properties"] = desired_properties_subset
                num_events_enriched += 1

        # Log an error if we did not enrich all the entries we asked for.
        if num_events_enriched != sum(len(le) for le in event_id_to_ledger_entries.values()):
            self.logger.error("Unable to enrich all eligible credit ledger entries with event metadata.")

        # Mutating entries within `event_id_to_ledger_entry` should have modified
        # the passed-in ledger_entries array
        return ledger_entries

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        This schema differs from `credit_ledger_entries.json` based on the configuration
        of the Stream. The configuration specifies a list of properties that each event
        is expected to have (and this connector returns). As of now, these properties
        are assumed to have String type.
        """
        schema = super().get_json_schema()
        dynamic_event_properties_schema = {}
        if self.string_event_properties_keys:
            for property_key in self.string_event_properties_keys:
                dynamic_event_properties_schema[property_key] = {"type": "string"}
        if self.numeric_event_properties_keys:
            for property_key in self.numeric_event_properties_keys:
                dynamic_event_properties_schema[property_key] = {"type": "number"}

        schema["properties"]["event"] = {
            "type": ["null", "object"],
            "properties": {
                "id": {"type": "string"},
                "properties": {"type": ["null", "object"], "properties": dynamic_event_properties_schema},
            },
            "required": ["id"],
        }

        return schema


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

    def input_keys_mutually_exclusive(
        self, string_event_properties_keys: Optional[List[str]] = None, numeric_event_properties_keys: Optional[List[str]] = None
    ):
        if string_event_properties_keys is None or numeric_event_properties_keys is None:
            return True
        else:
            return len(set(string_event_properties_keys) & set(numeric_event_properties_keys)) == 0

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = TokenAuthenticator(token=config["api_key"])
        lookback_window = config.get("lookback_window_days")
        string_event_properties_keys = config.get("string_event_properties_keys")
        numeric_event_properties_keys = config.get("numeric_event_properties_keys")

        if not self.input_keys_mutually_exclusive(string_event_properties_keys, numeric_event_properties_keys):
            raise ValueError("Supplied property keys for string and numeric valued property values must be mutually exclusive.")

        start_date_str = config.get("start_date")
        start_date = pendulum.parse(start_date_str) if start_date_str else None
        return [
            Customers(authenticator=authenticator, lookback_window_days=lookback_window, start_date=start_date),
            Subscriptions(authenticator=authenticator, lookback_window_days=lookback_window, start_date=start_date),
            Plans(authenticator=authenticator, lookback_window_days=lookback_window, start_date=start_date),
            CreditsLedgerEntries(
                authenticator=authenticator,
                lookback_window_days=lookback_window,
                start_date=start_date,
                string_event_properties_keys=string_event_properties_keys,
                numeric_event_properties_keys=numeric_event_properties_keys,
            ),
        ]
