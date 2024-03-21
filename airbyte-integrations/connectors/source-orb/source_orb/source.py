#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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

    def __init__(self, start_date: Optional[pendulum.DateTime] = None, end_date: Optional[pendulum.DateTime] = None, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date
        self.end_date = end_date

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
            params[f"{self.cursor_field}[gte]"] = state_based_start_timestamp

        if self.end_date:
            params[f"{self.cursor_field}[lte]"] = self.end_date

        return params


class Customers(IncrementalOrbStream):
    """
    API Docs: https://docs.withorb.com/reference/list-customers
    """

    use_cache = True

    def path(self, **kwargs) -> str:
        return "customers"


class Subscriptions(IncrementalOrbStream):
    """
    API Docs: https://docs.withorb.com/reference/list-subscriptions
    """

    def path(self, **kwargs) -> str:
        return "subscriptions"

    def transform_record(self, subscription_record):
        # Un-nest customer -> id, external_customer_id into customer_id,external_customer_id
        nested_customer_id = subscription_record["customer"]["id"]
        nested_external_customer_id = subscription_record["customer"]["external_customer_id"]
        del subscription_record["customer"]
        subscription_record["customer_id"] = nested_customer_id
        subscription_record["external_customer_id"] = nested_external_customer_id

        # Un-nest plan -> id into plan_id
        nested_plan_id = subscription_record["plan"]["id"]
        del subscription_record["plan"]
        subscription_record["plan_id"] = nested_plan_id

        return subscription_record


# helpers for working with pendulum dates and strings
def to_datetime(time) -> Optional[pendulum.DateTime]:
    if time is None:
        return None
    elif isinstance(time, pendulum.DateTime):
        return time
    elif isinstance(time, str):
        return pendulum.parse(time)
    else:
        raise TypeError(f"Cannot convert input of type {type(time)} to DateTime")


def to_utc_isoformat(time) -> Optional[str]:
    if time is None:
        return None
    elif isinstance(time, pendulum.DateTime):
        return time.in_timezone("UTC").isoformat()
    elif isinstance(time, str):
        return pendulum.parse(time).in_timezone("UTC").isoformat()
    else:
        raise TypeError(f"Cannot convert input of type {type(time)} to isoformat")


def chunk_date_range(start_date: pendulum.DateTime, end_date: Optional[pendulum.DateTime] = None) -> Iterable[pendulum.Period]:
    """
    Yields a list of the beginning and ending timestamps of each day between the start date and now.
    The return value is a pendulum.period
    """
    one_day = pendulum.duration(days=1)
    end_date = end_date or pendulum.now()

    # Each stream_slice contains the beginning and ending timestamp for a 24 hour period
    chunk_start_date = start_date
    while chunk_start_date < end_date:
        chunk_end_date = min(chunk_start_date + one_day, end_date)
        yield pendulum.period(chunk_start_date, chunk_end_date)
        chunk_start_date = chunk_end_date
    # yield from empty list to avoid returning None in case chunk_start_date >= end_date
    yield from []


class SubscriptionUsage(IncrementalOrbStream):
    """
    API Docs: https://docs.withorb.com/docs/orb-docs/api-reference/operations/get-a-subscription-usage
    """

    cursor_field = "timeframe_start"

    def __init__(
        self,
        start_date: pendulum.DateTime,
        subscription_usage_grouping_key: Optional[str] = None,
        plan_id: Optional[str] = None,
        end_date: Optional[pendulum.DateTime] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.subscription_usage_grouping_key = subscription_usage_grouping_key
        self.plan_id = plan_id
        self.start_date = start_date
        # default to current time if end_date is unspecified
        self.end_date = end_date if end_date else pendulum.now()

    @property
    def primary_key(self) -> Iterable[str]:
        key = ["subscription_id", "billable_metric_id", "timeframe_start"]

        # If a grouping key is present, it should be included in the primary key
        if self.subscription_usage_grouping_key:
            key.append(self.subscription_usage_grouping_key)

        return key

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        subscription_id = stream_slice["subscription_id"]

        # Records are in a container array called data
        response_json = response.json()
        records = response_json.get("data", [])
        for record in records:
            yield from self.yield_transformed_subrecords(record, subscription_id)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # This API endpoint is not paginated, so there will never be a next page
        return None

    def yield_transformed_subrecords(self, record, subscription_id):
        # for each top level response record, there can be multiple sub-records depending
        # on granularity and other input params. This function yields one transformed record
        # for each subrecord in the response.

        subrecords = record.get("usage", [])
        del record["usage"]
        for subrecord in subrecords:
            # skip records that don't contain any actual usage
            if subrecord.get("quantity", 0) > 0:
                # Merge the parent record with the sub record
                output = {**record, **subrecord}

                # Add the subscription ID to the output
                output["subscription_id"] = subscription_id

                # Un-nest billable_metric -> name,id into billable_metric_name and billable_metric_id
                nested_billable_metric_name = output["billable_metric"]["name"]
                nested_billable_metric_id = output["billable_metric"]["id"]
                del output["billable_metric"]
                output["billable_metric_name"] = nested_billable_metric_name
                output["billable_metric_id"] = nested_billable_metric_id

                # If a group_by key is specified, un-nest it
                if self.subscription_usage_grouping_key:
                    nested_key = output["metric_group"]["property_key"]
                    nested_value = output["metric_group"]["property_value"]
                    del output["metric_group"]
                    output[nested_key] = nested_value
                yield output
        yield from []

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, **kwargs) -> MutableMapping[str, Any]:
        """
        This is a non-paginated API that operates on specified timeframe_start/timeframe_end
        windows.

        Request params are based on the specific slice (i.e. subscription_id) we are requesting for,
        and so we need to pull out relevant slice state from the stream state.

        Force granularity to 'day' so that this stream can be used incrementally,
        with a day-based "cursor" based on timeframe_start and timeframe_end

        If a subscription_usage_grouping_key is present, adds a `group_by` param
        and `billable_metric_id` param from the stream slice. This is because
        the API requires a specific `billable_metric_id` to be set when using a
        `group_by` key.
        """

        params = {
            "granularity": "day",
            "timeframe_start": to_utc_isoformat(stream_slice["timeframe_start"]),
            "timeframe_end": to_utc_isoformat(stream_slice["timeframe_end"]),
        }

        if self.subscription_usage_grouping_key:
            params["group_by"] = self.subscription_usage_grouping_key

            # if a group_by key is specified, assume the stream slice contains a billable_metric_id
            params["billable_metric_id"] = stream_slice["billable_metric_id"]

        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}
        current_subscription_id = latest_record["subscription_id"]
        current_subscription_state = current_stream_state.get(current_subscription_id, {})

        record_cursor_value = to_datetime(latest_record[self.cursor_field])
        state_cursor_value = to_datetime(current_subscription_state.get(self.cursor_field, self.start_date))
        max_cursor_value = max(record_cursor_value, state_cursor_value)

        current_subscription_state[self.cursor_field] = to_utc_isoformat(max_cursor_value)

        return {**current_stream_state, current_subscription_id: current_subscription_state}

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        """
        Orb does not support querying for all subscription usage in an unscoped
        way, so the path here is dependent on the stream_slice, which determines
        the `subscription_id`.
        """
        subscription_id = stream_slice["subscription_id"]
        return f"subscriptions/{subscription_id}/usage"

    def get_billable_metric_ids_by_plan_id(self) -> Mapping[str, Any]:
        metric_ids_by_plan_id = {}

        for plan in Plans(authenticator=self._session.auth).read_records(sync_mode=SyncMode.full_refresh):
            # if a plan_id filter is specified, skip any plan that doesn't match
            if self.plan_id and plan["id"] != self.plan_id:
                continue

            prices = plan.get("prices", [])
            metric_ids_by_plan_id[plan["id"]] = [(price.get("billable_metric") or {}).get("id") for price in prices]

        # self.logger.warning("returning %s from get_billable_metric_ids", metric_ids_by_plan_id)
        return metric_ids_by_plan_id

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        This schema differs from `subscription_usage.json` based on the configuration
        of the Stream. If a group_by key is specified, the stream will output
        records that contain the group_key name and value.
        """
        schema = super().get_json_schema()
        if self.subscription_usage_grouping_key:
            schema["properties"][self.subscription_usage_grouping_key] = {"type": "string"}

        return schema

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        This stream is sliced per `subscription_id` and day, as well as `billable_metric_id`
        if a grouping key is provided. This is because the API only supports a
        single billable_metric_id per API call when using a group_by param.

        """
        stream_state = stream_state or {}
        slice_yielded = False
        subscriptions_stream = Subscriptions(authenticator=self._session.auth)

        # if using a group_by key, populate prices_by_plan_id so that each
        # billable metric will get its own slice
        if self.subscription_usage_grouping_key:
            metric_ids_by_plan_id = self.get_billable_metric_ids_by_plan_id()

        for subscription in subscriptions_stream.read_records(sync_mode=SyncMode.full_refresh):
            subscription_id = subscription["id"]
            subscription_plan_id = subscription["plan_id"]

            # if filtering subscription usage by plan ID, skip any subscription that doesn't match the plan_id
            if self.plan_id and subscription_plan_id != self.plan_id:
                continue

            subscription_state = stream_state.get(subscription_id, {})
            start_date = to_datetime(subscription_state.get(self.cursor_field, self.start_date))
            end_date = to_datetime(self.end_date)

            # create one slice for each day of usage between the start and end date
            for period in chunk_date_range(start_date=start_date, end_date=end_date):
                slice = {
                    "subscription_id": subscription_id,
                    "timeframe_start": to_utc_isoformat(period.start),
                    "timeframe_end": to_utc_isoformat(period.end),
                }

                # if using a group_by key, yield one slice per billable_metric_id.
                # otherwise, yield slices without a billable_metric_id because
                # each API call will return usage broken down by billable metric
                # when grouping isn't used.
                if self.subscription_usage_grouping_key:
                    metric_ids = metric_ids_by_plan_id.get(subscription_plan_id)
                    if metric_ids is not None:
                        for metric_id in metric_ids:
                            # self.logger.warning("stream_slices is about to yield the following slice: %s", slice)
                            yield {**slice, "billable_metric_id": metric_id}
                            slice_yielded = True
                else:
                    # self.logger.warning("stream_slices is about to yield the following slice: %s", slice)
                    yield slice
                    slice_yielded = True
        if not slice_yielded:
            # yield an empty slice to checkpoint state later
            yield {}


class Plans(IncrementalOrbStream):
    """
    API Docs: https://docs.withorb.com/reference/list-plans
    """

    def path(self, **kwargs) -> str:
        return "plans"


class Invoices(IncrementalOrbStream):
    """
    Fetches non-draft invoices, including those that are paid, issued, void, or synced.
    API Docs: https://docs.withorb.com/docs/orb-docs/api-reference/operations/list-invoices
    """

    @property
    def cursor_field(self) -> str:
        """
        Invoices created in the past may be newly issued, so we store state on
        `invoice_date` instead.
        """
        return "invoice_date"

    def path(self, **kwargs) -> str:
        return "invoices"

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        request_params = super().request_params(stream_state, **kwargs)
        # Filter to all statuses. Note that if you're currently expecting the status of the invoice
        # to update at the sink, you should periodically still expect to re-sync this connector to
        # fetch updates.
        request_params["status[]"] = ["void", "paid", "issued", "synced"]
        return request_params


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
                created_at_timestamp = pendulum.parse(entry.get("created_at", pendulum.now()))
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
        request_filter_json = {
            "event_ids": list(event_id_to_ledger_entries),
            "timeframe_start": created_at_timestamp.to_iso8601_string(),
            "timeframe_end": created_at_timestamp.add(days=30).to_iso8601_string(),
        }

        # Prepare request with self._session, which should
        # automatically deal with the authentication header.
        args = {"method": "POST", "url": self.url_base + "events", "params": {"limit": self.page_size}, "json": request_filter_json}
        prepared_request = self._session.prepare_request(requests.Request(**args))
        events_response: requests.Response = self._session.send(prepared_request)
        # Error for invalid responses
        if events_response.status_code != 200:
            self.logger.info(request_filter_json)
            self.logger.error(events_response.text)
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
        subscription_usage_grouping_key = config.get("subscription_usage_grouping_key")
        plan_id = config.get("plan_id")
        start_date = to_datetime(config.get("start_date"))
        end_date = to_datetime(config.get("end_date"))

        if not self.input_keys_mutually_exclusive(string_event_properties_keys, numeric_event_properties_keys):
            raise ValueError("Supplied property keys for string and numeric valued property values must be mutually exclusive.")

        return [
            Customers(authenticator=authenticator, lookback_window_days=lookback_window, start_date=start_date, end_date=end_date),
            Subscriptions(authenticator=authenticator, lookback_window_days=lookback_window, start_date=start_date),
            Plans(authenticator=authenticator, lookback_window_days=lookback_window, start_date=start_date),
            Invoices(authenticator=authenticator, lookback_window_days=lookback_window),
            CreditsLedgerEntries(
                authenticator=authenticator,
                lookback_window_days=lookback_window,
                start_date=start_date,
                string_event_properties_keys=string_event_properties_keys,
                numeric_event_properties_keys=numeric_event_properties_keys,
            ),
            SubscriptionUsage(
                authenticator=authenticator,
                lookback_window_days=lookback_window,
                start_date=start_date,
                end_date=end_date,
                plan_id=plan_id,
                subscription_usage_grouping_key=subscription_usage_grouping_key,
            ),
        ]
