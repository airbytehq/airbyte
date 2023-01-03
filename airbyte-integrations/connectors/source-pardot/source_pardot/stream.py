#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


# Basic full refresh stream
class PardotStream(HttpStream, ABC):
    url_base = "https://pi.pardot.com/api/"
    api_version = "4"
    time_filter_template = "%Y-%m-%dT%H:%M:%SZ"
    primary_key = "id"
    is_integer_state = False
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, config: Dict, **kwargs):
        super().__init__(**kwargs)
        self.config = config

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        results = response.json().get("result", {})
        record_count = results.get("total_results")
        if record_count and record_count > 0:
            # The result may be a dict if one record is returned
            if isinstance(results[self.data_key], list):
                return {self.filter_param: results[self.data_key][-1][self.cursor_field]}

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        headers = {"Pardot-Business-Unit-Id": self.config["pardot_business_unit_id"]}
        return headers

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {
            "format": "json",
        }
        start_date = self.config.get("start_date", None)
        if start_date:
            params.update({"created_after": pendulum.parse(start_date, strict=False).strftime(self.time_filter_template)})
        if next_page_token:
            params.update(**next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        results = response.json().get("result", {})
        record_count = results.get("total_results")
        # The result may be a dict if one record is returned
        if self.data_key in results and isinstance(results[self.data_key], dict):
            yield results[self.data_key]
        elif record_count and record_count > 0 and self.data_key in results:
            yield from results[self.data_key]

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.object_name}/version/{self.api_version}/do/query"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        blank_val = 0 if self.is_integer_state else ""
        return {
            self.cursor_field: max(latest_record.get(self.cursor_field, blank_val), current_stream_state.get(self.cursor_field, blank_val))
        }

    def filter_records_newer_than_state(self, stream_state: Mapping[str, Any] = None, records_slice: Mapping[str, Any] = None) -> Iterable:
        if stream_state:
            for record in records_slice:
                if record[self.cursor_field] >= stream_state.get(self.cursor_field):
                    yield record
        else:
            yield from records_slice


# PardotIdReplicationStreams
class PardotIdReplicationStream(PardotStream):
    cursor_field = "id"
    filter_param = "id_greater_than"
    is_integer_state = True


class EmailClicks(PardotIdReplicationStream):
    """
    API documentation: https://developer.salesforce.com/docs/marketing/pardot/guide/batch-email-clicks-v4.html
    """

    object_name = "emailClick"
    data_key = "emailClick"


class VisitorActivities(PardotIdReplicationStream):
    """
    API documentation: https://developer.salesforce.com/docs/marketing/pardot/guide/visitor-activities-v4.html
    """

    use_cache = True
    object_name = "visitorActivity"
    data_key = "visitor_activity"


# PardotUpdatedAtReplicationStreams
class PardotUpdatedAtReplicationStream(PardotStream):
    cursor_field = "updated_at"
    filter_param = "updated_after"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params.update({"sort_by": "updated_at", "sort_order": "ascending"})
        return params


class ProspectAccounts(PardotUpdatedAtReplicationStream):
    """
    API documentation: https://developer.salesforce.com/docs/marketing/pardot/guide/prospect-accounts-v4.html
    """

    object_name = "prospectAccount"
    data_key = "prospectAccount"


class Lists(PardotUpdatedAtReplicationStream):
    """
    API documentation: https://developer.salesforce.com/docs/marketing/pardot/guide/lists-v4.html
    """

    object_name = "list"
    data_key = "list"


class Prospects(PardotUpdatedAtReplicationStream):
    """
    API documentation: https://developer.salesforce.com/docs/marketing/pardot/guide/prospects-v4.html
    """

    object_name = "prospect"
    data_key = "prospect"


class Visitors(PardotUpdatedAtReplicationStream):
    """
    API documentation: https://developer.salesforce.com/docs/marketing/pardot/guide/visitors-v4.html
    """

    use_cache = True
    object_name = "visitor"
    data_key = "visitor"

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        slices = super().stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
        return slices


class Campaigns(PardotUpdatedAtReplicationStream):
    """
    API documentation: https://developer.salesforce.com/docs/marketing/pardot/guide/campaigns-v4.html
    """

    cursor_field = "id"
    filter_param = "id_greater_than"
    object_name = "campaign"
    data_key = "campaign"
    is_integer_state = True

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params.update({"sort_by": "id", "sort_order": "ascending"})
        return params


class ListMembership(PardotUpdatedAtReplicationStream):
    """
    API documentation: https://developer.salesforce.com/docs/marketing/pardot/guide/list-memberships-v4.html
    """

    object_name = "listMembership"
    data_key = "list_membership"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params.update({"sort_by": "id", "sort_order": "ascending"})
        return params


# PardotFullReplicationStreams
class Opportunities(PardotStream):
    """
    API documentation: https://developer.salesforce.com/docs/marketing/pardot/guide/opportunities-v4.html
    Currently disabled because test account doesn't have any data
    """

    object_name = "opportunity"
    data_key = "opportunity"
    filter_param = "created_after"
    cursor_field = "created_at"


class Users(PardotStream):
    """
    API documentation: https://developer.salesforce.com/docs/marketing/pardot/guide/users-v4.html
    """

    object_name = "user"
    data_key = "user"
    filter_param = "created_after"
    cursor_field = "created_at"


# PardotChildStreams
class PardotChildStream(PardotStream):
    max_ids_per_request = 200

    def __init__(self, parent_stream: PardotStream, **kwargs):
        super().__init__(**kwargs)
        self.parent_stream = parent_stream

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        id_list = []
        for slice in self.parent_stream.stream_slices(sync_mode=SyncMode.full_refresh):
            records = self.parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice)
            ids = [str(record["id"]) for record in records]
            id_list.extend(ids)

        while id_list:
            ids = id_list[: self.max_ids_per_request]
            yield ",".join(ids)
            id_list = id_list[self.max_ids_per_request :]


class Visits(PardotChildStream):
    """
    API documentation: https://developer.salesforce.com/docs/marketing/pardot/guide/visits-v4.html
    """

    object_name = "visit"
    data_key = "visit"
    filter_param = "offset"
    cursor_field = "id"
    offset = 0
    is_integer_state = True

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return {}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params.update({"visitor_ids": stream_slice})
        return params
