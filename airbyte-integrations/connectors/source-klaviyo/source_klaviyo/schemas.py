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


from datetime import datetime
from typing import Any, List, MutableMapping, Optional

from pydantic import BaseModel, Extra


class BaseSchemaModel(BaseModel):
    class Config:
        extra = Extra.allow

        @staticmethod
        def schema_extra(schema: MutableMapping[str, Any], model) -> None:
            # Pydantic adds title to every attribute, this is too much, so we manually drop them
            for prop in schema.get("properties", {}).values():
                prop.pop("title", None)

    object: str


class PersonList(BaseModel):
    id: str
    name: str
    created: datetime
    updated: datetime
    person_count: int
    list_type: str
    folder: Optional[str]


class Campaign(BaseSchemaModel):
    id: str
    name: str
    created: Optional[datetime]
    updated: Optional[datetime]
    status: str
    status_id: int
    status_label: str
    from_name: str
    from_email: str
    num_recipients: int
    lists: List[PersonList]
    excluded_lists: List[PersonList]
    is_segmented: bool
    send_time: Optional[datetime]
    sent_at: Optional[datetime]
    campaign_type: str
    subject: Optional[str]
    message_type: str
    template_id: Optional[str]


class Event(BaseSchemaModel):
    id: str
    uuid: str
    event_name: str
    timestamp: int
    datetime: str
    statistic_id: str
    event_properties: dict
    person: dict


class GlobalExclusion(BaseSchemaModel):
    email: str
    reason: str
    timestamp: datetime


class Integration(BaseSchemaModel):
    id: str
    name: str
    category: str


class Metric(BaseSchemaModel):
    id: str
    name: str
    created: datetime
    updated: datetime
    integration: Integration
