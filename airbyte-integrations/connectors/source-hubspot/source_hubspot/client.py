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

from typing import Any, Mapping, Tuple

from base_python import BaseClient
from base_python.client import ResourceSchemaLoader
from base_python.entrypoint import logger
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


class HubspotResourceSchemaLoader(ResourceSchemaLoader):
    field_type_schema = {
        "bool": {"type": ["null", "boolean"]},
        "datetime": {"type": ["null", "string"], "format": "date-time"},
        "number": {"type": ["null", "integer"]},
    }

    def __init__(self, *args, **kwargs):
        self._apis = None
        super().__init__(*args, **kwargs)

    def parse_custom_schema(self, properties: Mapping[str, Any]) -> Mapping[str, Mapping]:
        schema = {}
        for field_name, field_schema in properties.items():
            schema[field_name] = self.field_type_schema.get(field_schema["type"], {"type": ["null", "string"]})
        return schema

    def get_schema(self, name: str) -> dict:
        schema = super().get_schema(name)
        if self._apis:
            if name in self._apis:
                custom_schema = self.parse_custom_schema(self._apis[name].properties)

                schema["properties"]["properties"] = {
                    "type": "object",
                    "properties": custom_schema,
                }
        return schema


class Client(BaseClient):
    schema_loader_class = HubspotResourceSchemaLoader

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

        self._schema_loader._apis = self._apis

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {name: api.list for name, api in self._apis.items()}

    def health_check(self) -> Tuple[bool, str]:
        logger.error("Health check not implemented")
        return True, "TODO"
