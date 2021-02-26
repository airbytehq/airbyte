"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Mapping, Tuple

from base_python import BaseClient
from source_hubspot.api import (
    API,
    CampaignsAPI,
    CompaniesAPI,
    ContactListsAPI,
    ContactsAPI,
    ContactsByCompanyAPI,
    DealPipelinesAPI,
    DealsAPI,
    EmailEventsAPI,
    EngagementsAPI,
    FormsAPI,
    LineItemsAPI,
    OwnersAPI,
    ProductsAPI,
    QuotesAPI,
    SubscriptionChangesAPI,
    TicketsAPI,
    WorkflowsAPI,
)


class Client(BaseClient):
    def __init__(self, start_date, credentials, **kwargs):
        self._start_date = start_date
        self._api = API(credentials=credentials)

        self._apis = {
            "campaigns": CampaignsAPI(api=self._api, start_date=self._start_date),
            "companies": CompaniesAPI(api=self._api, start_date=self._start_date),
            "contact_lists": ContactListsAPI(api=self._api, start_date=self._start_date),
            "contacts": ContactsAPI(api=self._api, start_date=self._start_date),
            "contacts_by_company": ContactsByCompanyAPI(api=self._api, start_date=self._start_date),
            "deal_pipelines": DealPipelinesAPI(api=self._api, start_date=self._start_date),
            "deals": DealsAPI(api=self._api, start_date=self._start_date),
            "email_events": EmailEventsAPI(api=self._api, start_date=self._start_date),
            "engagements": EngagementsAPI(api=self._api, start_date=self._start_date),
            "forms": FormsAPI(api=self._api, start_date=self._start_date),
            "line_items": LineItemsAPI(api=self._api, start_date=self._start_date),
            "owners": OwnersAPI(api=self._api, start_date=self._start_date),
            "products": ProductsAPI(api=self._api, start_date=self._start_date),
            "quotes": QuotesAPI(api=self._api, start_date=self._start_date),
            "subscription_changes": SubscriptionChangesAPI(api=self._api, start_date=self._start_date),
            "tickets": TicketsAPI(api=self._api, start_date=self._start_date),
            "workflows": WorkflowsAPI(api=self._api, start_date=self._start_date),
        }

        super().__init__(**kwargs)

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {name: api.list for name, api in self._apis.items()}

    def health_check(self) -> Tuple[bool, str]:
        pass
