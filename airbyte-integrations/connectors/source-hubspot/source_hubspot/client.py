#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from typing import Any, Iterator, Mapping, Tuple

from airbyte_protocol import AirbyteStream
from base_python import BaseClient
from requests import HTTPError
from source_hubspot.api import (
    API,
    CampaignStream,
    ContactListStream,
    CRMObjectStream,
    DealPipelineStream,
    DealStream,
    EmailEventStream,
    EngagementStream,
    FormStream,
    OwnerStream,
    SubscriptionChangeStream,
    WorkflowStream,
)


class Client(BaseClient):
    """Hubspot client, provides methods to discover and read streams"""

    def __init__(self, start_date, credentials, **kwargs):
        self._start_date = start_date
        self._api = API(credentials=credentials)

        common_params = dict(api=self._api, start_date=self._start_date)
        self._apis = {
            "campaigns": CampaignStream(**common_params),
            "companies": CRMObjectStream(entity="company", associations=["contacts"], **common_params),
            "contact_lists": ContactListStream(**common_params),
            "contacts": CRMObjectStream(entity="contact", **common_params),
            "deal_pipelines": DealPipelineStream(**common_params),
            "deals": DealStream(**common_params),
            "email_events": EmailEventStream(**common_params),
            "engagements": EngagementStream(**common_params),
            "forms": FormStream(**common_params),
            "line_items": CRMObjectStream(entity="line_item", **common_params),
            "owners": OwnerStream(**common_params),
            "products": CRMObjectStream(entity="product", **common_params),
            "quotes": CRMObjectStream(entity="quote", **common_params),
            "subscription_changes": SubscriptionChangeStream(**common_params),
            "tickets": CRMObjectStream(entity="ticket", **common_params),
            "workflows": WorkflowStream(**common_params),
        }

        super().__init__(**kwargs)

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {name: api.list for name, api in self._apis.items()}

    @property
    def streams(self) -> Iterator[AirbyteStream]:
        """List of available streams, patch streams to append properties dynamically"""
        for stream in super().streams:
            properties = self._apis[stream.name].properties
            if properties:
                stream.json_schema["properties"]["properties"] = {"type": "object", "properties": properties}
                stream.default_cursor_field = [self._apis[stream.name].updated_at_field]
            yield stream

    def stream_has_state(self, name: str) -> bool:
        """Tell if stream supports incremental sync"""
        return hasattr(self._apis[name], "state")

    def get_stream_state(self, name: str) -> Any:
        """Get state of stream with corresponding name"""
        return self._apis[name].state

    def set_stream_state(self, name: str, state: Any):
        """Set state of stream with corresponding name"""
        self._apis[name].state = state

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_msg = None

        try:
            _ = self._apis["contacts"].properties
        except HTTPError as error:
            alive = False
            error_msg = repr(error)

        return alive, error_msg
