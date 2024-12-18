# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import base64
from datetime import datetime
from typing import List, Optional, Union

from airbyte_cdk.test.mock_http import HttpRequest
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


class ChargebeeRequestBuilder:

    @classmethod
    def addon_endpoint(cls, site: str, site_api_key: str) -> "ChargebeeRequestBuilder":
        return cls("addons", site, site_api_key)

    @classmethod
    def plan_endpoint(cls, site: str, site_api_key: str) -> "ChargebeeRequestBuilder":
        return cls("plans", site, site_api_key)

    @classmethod
    def virtual_bank_account_endpoint(cls, site: str, site_api_key: str) -> "ChargebeeRequestBuilder":
        return cls("virtual_bank_accounts", site, site_api_key)

    @classmethod
    def event_endpoint(cls, site: str, site_api_key: str) -> "ChargebeeRequestBuilder":
        return cls("events", site, site_api_key)

    @classmethod
    def site_migration_detail_endpoint(cls, site: str, site_api_key: str) -> "ChargebeeRequestBuilder":
        return cls("site_migration_details", site, site_api_key)

    @classmethod
    def customer_endpoint(cls, site: str, site_api_key: str) -> "ChargebeeRequestBuilder":
        return cls("customers", site, site_api_key)

    @classmethod
    def coupon_endpoint(cls, site: str, site_api_key: str) -> "ChargebeeRequestBuilder":
        return cls("coupons", site, site_api_key)

    @classmethod
    def subscription_endpoint(cls, site: str, site_api_key: str) -> "ChargebeeRequestBuilder":
        return cls("subscriptions", site, site_api_key)

    @classmethod
    def hosted_page_endpoint(cls, site: str, site_api_key: str) -> "ChargebeeRequestBuilder":
        return cls("hosted_pages", site, site_api_key)

    def __init__(self, resource: str, site: str, site_api_key: str) -> "ChargebeeRequestBuilder":
        self._resource: str = resource
        self._site: str = site
        self._site_api_key: str = site_api_key
        self._any_query_params: bool = False
        self._include_deleted: Optional[str] = None
        self._created_at_btw: Optional[str] = None
        self._updated_at_btw: Optional[str] = None
        self._occurred_at_btw: Optional[str] = None
        self._sort_by_asc: Optional[str] = None
        self._sort_by_desc: Optional[str] = None
        self._offset: Optional[str] = None
        self._limit: Optional[str] = None

    def with_any_query_params(self) -> "ChargebeeRequestBuilder":
        self._any_query_params = True
        return self

    def with_include_deleted(self, include_deleted: bool) -> "ChargebeeRequestBuilder":
        self._include_deleted = str(include_deleted).lower()
        return self

    def with_created_at_btw(self, created_at_btw: List[int]) -> "ChargebeeRequestBuilder":
        self._created_at_btw = f'{created_at_btw}'
        return self

    def with_updated_at_btw(self, updated_at_btw: List[int]) -> "ChargebeeRequestBuilder":
        self._updated_at_btw = f"{updated_at_btw}"
        return self

    def with_occurred_at_btw(self, occurred_at_btw: List[int]) -> "ChargebeeRequestBuilder":
        self._occurred_at_btw = f"{occurred_at_btw}"
        return self

    def with_sort_by_asc(self, sort_by_asc: str) -> "ChargebeeRequestBuilder":
        self._sort_by_asc = sort_by_asc
        return self

    def with_sort_by_desc(self, sort_by_desc: str) -> "ChargebeeRequestBuilder":
        self._sort_by_desc = sort_by_desc
        return self

    def with_offset(self, offset: str) -> "ChargebeeRequestBuilder":
        self._offset = offset
        return self

    def with_limit(self, limit: int) -> "ChargebeeRequestBuilder":
        self._limit = limit
        return self

    def build(self) -> HttpRequest:
        query_params= {}
        if self._sort_by_asc:
            query_params["sort_by[asc]"] = self._sort_by_asc
        if self._sort_by_desc:
            query_params["sort_by[desc]"] = self._sort_by_desc
        if self._include_deleted:
            query_params["include_deleted"] = self._include_deleted
        if self._created_at_btw:
            query_params["created_at[between]"] = self._created_at_btw
        if self._updated_at_btw:
            query_params["updated_at[between]"] = self._updated_at_btw
        if self._occurred_at_btw:
            query_params["occurred_at[between]"] = self._occurred_at_btw
        if self._offset:
            query_params["offset"] = self._offset
        if self._limit:
            query_params["limit"] = self._limit

        if self._any_query_params:
            if query_params:
                raise ValueError(f"Both `any_query_params` and {list(query_params.keys())} were configured. Provide only one of none but not both.")
            query_params = ANY_QUERY_PARAMS

        return HttpRequest(
            url=f"https://{self._site}.chargebee.com/api/v2/{self._resource}",
            query_params=query_params,
            headers={"Authorization": f"Basic {base64.b64encode((str(self._site_api_key) + ':').encode('utf-8')).decode('utf-8')}"},
        )

class ChargebeeSubstreamRequestBuilder(ChargebeeRequestBuilder):

    @classmethod
    def subscription_with_scheduled_changes_endpoint(cls, site: str, site_api_key: str) -> "ChargebeeRequestBuilder":
        return cls("subscriptions", site, site_api_key)

    def with_parent_id(self, parent_id: str) -> "ChargebeeSubstreamRequestBuilder":
        self._parent_id = parent_id
        return self

    def with_endpoint_path(self, endpoint_path: str) -> "ChargebeeSubstreamRequestBuilder":
        self._endpoint_path = endpoint_path
        return self

    def build(self) -> HttpRequest:
        query_params= {}
        if self._sort_by_asc:
            query_params["sort_by[asc]"] = self._sort_by_asc
        if self._sort_by_desc:
            query_params["sort_by[desc]"] = self._sort_by_desc
        if self._include_deleted:
            query_params["include_deleted"] = self._include_deleted
        if self._created_at_btw:
            query_params["created_at[between]"] = self._created_at_btw
        if self._updated_at_btw:
            query_params["updated_at[between]"] = self._updated_at_btw
        if self._occurred_at_btw:
            query_params["occurred_at[between]"] = self._occurred_at_btw
        if self._offset:
            query_params["offset"] = self._offset
        if self._limit:
            query_params["limit"] = self._limit

        if self._any_query_params:
            if query_params:
                raise ValueError(f"Both `any_query_params` and {list(query_params.keys())} were configured. Provide only one of none but not both.")
            query_params = ANY_QUERY_PARAMS

        return HttpRequest(
            url=f"https://{self._site}.chargebee.com/api/v2/{self._resource}/{self._parent_id}/{self._endpoint_path}",
            query_params=query_params,
            headers={"Authorization": f"Basic {base64.b64encode((str(self._site_api_key) + ':').encode('utf-8')).decode('utf-8')}"},
        )
